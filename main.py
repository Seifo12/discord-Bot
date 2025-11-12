import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio
import random
import os
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread

# ====================== إعدادات التوكن ======================
# التوكن يُقرأ من المتغيرات البيئية (Secrets في Replit أو Variables في Railway)
TOKEN = os.environ.get('TOKEN')

if not TOKEN:
    print("❌ خطأ: لم يتم العثور على التوكن!")
    print("📝 تأكد من إضافة TOKEN في:")
    print("   - Replit: اذهب إلى Secrets وأضف TOKEN")
    print("   - Railway: اذهب إلى Variables وأضف TOKEN")
    exit()

# ====================== إعداد Flask للإبقاء على البوت حياً ======================
app = Flask('')

@app.route('/')
def home():
    return """
    <html>
        <head>
            <title>Discord Bot Status</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .container {
                    background: white;
                    padding: 50px;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    text-align: center;
                }
                h1 { color: #667eea; }
                .status { 
                    color: #10b981; 
                    font-size: 24px; 
                    font-weight: bold;
                    margin: 20px 0;
                }
                .info { color: #6b7280; margin: 10px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 بوت ديسكورد المتكامل</h1>
                <div class="status">✅ البوت شغال!</div>
                <div class="info">⚡ الحالة: نشط</div>
                <div class="info">🕐 الوقت: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</div>
                <div class="info">☁️ مستضاف على السحابة</div>
            </div>
        </body>
    </html>
    """

def run():
    app.run(host='0.0.0.0', port=5000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ====================== إعدادات البوت ======================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# قواعد البيانات
tickets_db = {}
warnings_db = {}
levels_db = {}
economy_db = {}

# الرتب
ROLES = [
    {"name": "👑 • المالك", "color": 0xFF0000, "permissions": discord.Permissions.all()},
    {"name": "🔮 • المالك المشارك", "color": 0x9B59B6, "permissions": discord.Permissions.all()},
    {"name": "⚔️ • الإدارة", "color": 0x3498DB, "permissions": discord.Permissions(administrator=True)},
    {"name": "🛡️ • المشرف", "color": 0x2ECC71, "permissions": discord.Permissions(
        kick_members=True, ban_members=True, manage_messages=True, 
        manage_channels=True, mute_members=True, deafen_members=True
    )},
    {"name": "🎯 • المساعد", "color": 0xF1C40F, "permissions": discord.Permissions(
        kick_members=True, manage_messages=True, mute_members=True
    )},
    {"name": "💎 • البوستر", "color": 0xE91E63, "permissions": discord.Permissions.none()},
    {"name": "🏆 • الرائع", "color": 0xE67E22, "permissions": discord.Permissions.none()},
    {"name": "👤 • العضو", "color": 0x95A5A6, "permissions": discord.Permissions.none()},
]

# القنوات
CATEGORIES_AND_CHANNELS = {
    "📢 • الإعلانات": [
        "📣・الإعلانات-الرسمية",
        "📰・الأخبار",
        "🎉・الفعاليات",
        "🎁・الهدايا"
    ],
    "💬 • الدردشة": [
        "💭・الدردشة-العامة",
        "🎮・الألعاب",
        "🎨・الفن-والإبداع",
        "📷・الصور-والميمز",
        "🤖・أوامر-البوت"
    ],
    "🎵 • الصوتيات": [
        "🔊・الروم-العام",
        "🎵・الموسيقى",
        "🎮・الجيمنج-1",
        "🎮・الجيمنج-2",
        "🎤・البودكاست"
    ],
    "🎫 • الدعم الفني": [
        "🎫・إنشاء-تذكرة",
        "📋・التذاكر-المفتوحة"
    ],
    "⚙️ • الإدارة": [
        "🛠️・إدارة-السيرفر",
        "📊・السجلات",
        "⚠️・البلاغات",
        "🚨・التحذيرات"
    ],
    "ℹ️ • المعلومات": [
        "📜・القوانين",
        "👋・الترحيب",
        "📌・الروابط-المهمة",
        "📊・الإحصائيات"
    ]
}

# ==================== نظام التذاكر ====================
class TicketButton(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="📩 إنشاء تذكرة", style=discord.ButtonStyle.green, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        member = interaction.user
        
        if str(member.id) in tickets_db:
            await interaction.response.send_message("❌ لديك تذكرة مفتوحة بالفعل!", ephemeral=True)
            return
        
        category = discord.utils.get(guild.categories, name="🎫 • الدعم الفني")
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        admin_role = discord.utils.get(guild.roles, name="⚔️ • الإدارة")
        mod_role = discord.utils.get(guild.roles, name="🛡️ • المشرف")
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        if mod_role:
            overwrites[mod_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        ticket_channel = await guild.create_text_channel(
            f"🎫┃{member.name}",
            category=category,
            overwrites=overwrites
        )
        
        tickets_db[str(member.id)] = ticket_channel.id
        
        embed = discord.Embed(
            title="🎫 تذكرة دعم فني",
            description=f"مرحباً {member.mention}!\n\nالرجاء شرح مشكلتك وسيتم الرد عليك قريباً.",
            color=0x00FF00
        )
        
        close_view = CloseTicketView()
        await ticket_channel.send(f"{member.mention}", embed=embed, view=close_view)
        await interaction.response.send_message(f"✅ تم إنشاء تذكرتك {ticket_channel.mention}", ephemeral=True)

class CloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🔒 إغلاق التذكرة", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("⏳ جاري إغلاق التذكرة...")
        
        for user_id, channel_id in list(tickets_db.items()):
            if channel_id == interaction.channel.id:
                del tickets_db[user_id]
                break
        
        await asyncio.sleep(3)
        await interaction.channel.delete()

# ==================== نظام المستويات ====================
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    user_id = str(message.author.id)
    if user_id not in levels_db:
        levels_db[user_id] = {"xp": 0, "level": 1, "messages": 0}
    
    levels_db[user_id]["messages"] += 1
    levels_db[user_id]["xp"] += random.randint(5, 15)
    
    xp = levels_db[user_id]["xp"]
    level = levels_db[user_id]["level"]
    xp_needed = level * 100
    
    if xp >= xp_needed:
        levels_db[user_id]["level"] += 1
        new_level = levels_db[user_id]["level"]
        
        embed = discord.Embed(
            title="🎉 ترقية مستوى!",
            description=f"{message.author.mention} وصل للمستوى **{new_level}**!",
            color=0xFFD700
        )
        await message.channel.send(embed=embed)
    
    if user_id not in economy_db:
        economy_db[user_id] = {"coins": 0, "bank": 0}
    
    economy_db[user_id]["coins"] += random.randint(1, 5)
    
    await bot.process_commands(message)

@bot.command(name='مستوى')
async def level(ctx, member: discord.Member = None):
    member = member or ctx.author
    user_id = str(member.id)
    
    if user_id not in levels_db:
        levels_db[user_id] = {"xp": 0, "level": 1, "messages": 0}
    
    data = levels_db[user_id]
    xp_needed = data["level"] * 100
    
    embed = discord.Embed(title=f"📊 مستوى {member.name}", color=0x3498DB)
    embed.add_field(name="المستوى", value=f"🏆 {data['level']}", inline=True)
    embed.add_field(name="الخبرة", value=f"⭐ {data['xp']}/{xp_needed}", inline=True)
    embed.add_field(name="الرسائل", value=f"💬 {data['messages']}", inline=True)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    await ctx.send(embed=embed)

@bot.command(name='ترتيب')
async def leaderboard(ctx):
    sorted_users = sorted(levels_db.items(), key=lambda x: x[1]["xp"], reverse=True)[:10]
    
    embed = discord.Embed(title="🏆 ترتيب الأعضاء", color=0xFFD700)
    
    for idx, (user_id, data) in enumerate(sorted_users, 1):
        member = ctx.guild.get_member(int(user_id))
        if member:
            embed.add_field(
                name=f"{idx}. {member.name}",
                value=f"المستوى: {data['level']} | الخبرة: {data['xp']}",
                inline=False
            )
    
    await ctx.send(embed=embed)

# ==================== نظام الاقتصاد ====================
@bot.command(name='فلوس')
async def balance(ctx, member: discord.Member = None):
    member = member or ctx.author
    user_id = str(member.id)
    
    if user_id not in economy_db:
        economy_db[user_id] = {"coins": 0, "bank": 0}
    
    data = economy_db[user_id]
    
    embed = discord.Embed(title=f"💰 رصيد {member.name}", color=0xFFD700)
    embed.add_field(name="المحفظة", value=f"🪙 {data['coins']}", inline=True)
    embed.add_field(name="البنك", value=f"🏦 {data['bank']}", inline=True)
    embed.add_field(name="الإجمالي", value=f"💎 {data['coins'] + data['bank']}", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='يومي')
async def daily(ctx):
    user_id = str(ctx.author.id)
    
    if user_id not in economy_db:
        economy_db[user_id] = {"coins": 0, "bank": 0, "last_daily": None}
    
    if "last_daily" in economy_db[user_id] and economy_db[user_id]["last_daily"]:
        last = economy_db[user_id]["last_daily"]
        if (datetime.now() - datetime.fromisoformat(last)).days < 1:
            await ctx.send("❌ حصلت على مكافأتك اليومية! عد غداً.")
            return
    
    reward = random.randint(100, 500)
    economy_db[user_id]["coins"] += reward
    economy_db[user_id]["last_daily"] = datetime.now().isoformat()
    
    embed = discord.Embed(
        title="🎁 مكافأة يومية!",
        description=f"حصلت على **{reward}** 🪙",
        color=0x00FF00
    )
    await ctx.send(embed=embed)

# ==================== الألعاب ====================
@bot.command(name='قمار')
async def gamble(ctx, amount: int):
    user_id = str(ctx.author.id)
    
    if user_id not in economy_db:
        economy_db[user_id] = {"coins": 0, "bank": 0}
    
    if amount <= 0 or economy_db[user_id]["coins"] < amount:
        await ctx.send("❌ مبلغ غير صالح!")
        return
    
    win = random.choice([True, False])
    
    if win:
        economy_db[user_id]["coins"] += amount
        embed = discord.Embed(title="🎰 فزت!", description=f"ربحت **{amount}** 🪙", color=0x00FF00)
    else:
        economy_db[user_id]["coins"] -= amount
        embed = discord.Embed(title="💔 خسرت!", description=f"خسرت **{amount}** 🪙", color=0xFF0000)
    
    await ctx.send(embed=embed)

# ==================== أوامر الإدارة ====================
@bot.command(name='تحذير')
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason: str = "لا يوجد سبب"):
    user_id = str(member.id)
    
    if user_id not in warnings_db:
        warnings_db[user_id] = []
    
    warnings_db[user_id].append({
        "reason": reason,
        "moderator": str(ctx.author.id),
        "date": datetime.now().isoformat()
    })
    
    embed = discord.Embed(title="⚠️ تحذير", description=f"{member.mention} تم تحذيرك", color=0xFFA500)
    embed.add_field(name="السبب", value=reason, inline=False)
    embed.add_field(name="عدد التحذيرات", value=len(warnings_db[user_id]), inline=False)
    
    await ctx.send(embed=embed)
    
    if len(warnings_db[user_id]) >= 3:
        await member.timeout(timedelta(hours=1), reason="3 تحذيرات")
        await ctx.send(f"🔇 {member.mention} تم كتمه لمدة ساعة")

@bot.command(name='كتم')
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, minutes: int = 10, *, reason: str = "لا يوجد سبب"):
    await member.timeout(timedelta(minutes=minutes), reason=reason)
    await ctx.send(f"🔇 تم كتم {member.mention} لمدة {minutes} دقيقة")

@bot.command(name='مسح')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    deleted = await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"✅ تم مسح {len(deleted) - 1} رسالة")
    await asyncio.sleep(3)
    await msg.delete()

# ==================== إعداد السيرفر ====================
@bot.command(name='اعداد_السيرفر')
@commands.has_permissions(administrator=True)
async def setup_server(ctx):
    guild = ctx.guild
    await ctx.send("🚀 **بدء إعداد السيرفر...**")
    
    # حذف القنوات والرتب القديمة
    for channel in guild.channels:
        try:
            await channel.delete()
            await asyncio.sleep(1)
        except:
            pass
    
    for role in guild.roles:
        if role.name != "@everyone":
            try:
                await role.delete()
                await asyncio.sleep(1)
            except:
                pass
    
    # إنشاء الرتب
    for role_data in ROLES:
        try:
            await guild.create_role(
                name=role_data["name"],
                color=discord.Color(role_data["color"]),
                permissions=role_data["permissions"],
                hoist=True
            )
            await asyncio.sleep(1)
        except:
            pass
    
    # إنشاء القنوات
    ticket_channel = None
    for category_name, channels in CATEGORIES_AND_CHANNELS.items():
        try:
            category = await guild.create_category(category_name)
            await asyncio.sleep(1)
            
            for channel_name in channels:
                if "🔊" in channel_name or "🎵" in channel_name or "🎮" in channel_name or "🎤" in channel_name:
                    await guild.create_voice_channel(channel_name, category=category)
                else:
                    channel = await guild.create_text_channel(channel_name, category=category)
                    if channel_name == "🎫・إنشاء-تذكرة":
                        ticket_channel = channel
                await asyncio.sleep(1)
        except:
            pass
    
    # إعداد نظام التذاكر
    if ticket_channel:
        ticket_embed = discord.Embed(
            title="🎫 نظام الدعم الفني",
            description="اضغط على الزر لإنشاء تذكرة",
            color=0x00FF00
        )
        view = TicketButton()
        await ticket_channel.send(embed=ticket_embed, view=view)
    
    await ctx.send("✅ **تم إعداد السيرفر بنجاح!**")

@bot.command(name='مساعدة')
async def help_command(ctx):
    embed = discord.Embed(title="📚 أوامر البوت", color=0x3498DB)
    embed.add_field(name="!اعداد_السيرفر", value="إعداد السيرفر", inline=False)
    embed.add_field(name="!مستوى", value="عرض مستواك", inline=False)
    embed.add_field(name="!فلوس", value="عرض رصيدك", inline=False)
    embed.add_field(name="!يومي", value="مكافأة يومية", inline=False)
    embed.add_field(name="!قمار [مبلغ]", value="لعبة القمار", inline=False)
    await ctx.send(embed=embed)

# ==================== الأحداث ====================
@bot.event
async def on_ready():
    print("=" * 50)
    print(f"🤖 البوت جاهز: {bot.user.name}")
    print("✅ متصل بالإنترنت")
    print(f"📊 متصل بـ {len(bot.guilds)} سيرفر")
    print("☁️ يعمل على السحابة")
    print("=" * 50)
    
    bot.add_view(TicketButton())
    bot.add_view(CloseTicketView())

@bot.event
async def on_member_join(member):
    welcome_channel = discord.utils.get(member.guild.text_channels, name="👋・الترحيب")
    if welcome_channel:
        embed = discord.Embed(
            title=f"🎉 مرحباً {member.name}!",
            description=f"أهلاً بك في **{member.guild.name}**!",
            color=0x00FF00
        )
        await welcome_channel.send(f"{member.mention}", embed=embed)
    
    member_role = discord.utils.get(member.guild.roles, name="👤 • العضو")
    if member_role:
        await member.add_roles(member_role)

# ==================== تشغيل البوت ====================
if __name__ == "__main__":
    print("=" * 50)
    print("🚀 بوت ديسكورد المتكامل - نسخة السحابة")
    print("=" * 50)
    print("☁️ مستضاف على: Replit/Railway/Render")
    print("🌐 بدء Web Server...")
    
    # تشغيل Web Server
    keep_alive()
    
    print("🤖 بدء تشغيل البوت...")
    print("=" * 50)
    
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ خطأ: {e}")
