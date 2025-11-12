import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View, Select
import asyncio
import random
import os
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread

# ====================== إعدادات التوكن ======================
TOKEN = os.environ.get('TOKEN')

if not TOKEN:
    print("❌ خطأ: لم يتم العثور على التوكن!")
    print("📝 تأكد من إضافة TOKEN في:")
    print("   - Replit: اذهب إلى Secrets وأضف TOKEN")
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
tickets_by_channel = {}
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

# التسلسل الهرمي للرتب (من الأعلى إلى الأدنى)
# كل رتبة يمكنها إعطاء الرتب التي تحتها فقط
ROLE_HIERARCHY = [
    "👑 • المالك",
    "🔮 • المالك المشارك",
    "⚔️ • الإدارة",
    "🛡️ • المشرف",
    "🎯 • المساعد",
    "💎 • البوستر",
    "🏆 • الرائع",
    "👤 • العضو"
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

# ====================== نظام التذاكر المحسّن ======================
class TicketTypeSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="دعم فني",
                description="مشاكل تقنية وأسئلة حول البوت",
                emoji="💻",
                value="tech_support"
            ),
            discord.SelectOption(
                label="مشكلة بالسيرفر",
                description="مشاكل متعلقة بإعدادات السيرفر",
                emoji="⚙️",
                value="server_problem"
            ),
            discord.SelectOption(
                label="مشكلة بسبب الإدارة",
                description="شكاوى أو مشاكل مع الإدارة",
                emoji="👔",
                value="admin_problem"
            ),
        ]
        
        super().__init__(
            placeholder="🎫 اختر نوع التذكرة...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_type_select"
        )
    
    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        ticket_type = self.values[0]
        
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
        coowner_role = discord.utils.get(guild.roles, name="🔮 • المالك المشارك")
        
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        if mod_role:
            overwrites[mod_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        ticket_channel = await guild.create_text_channel(
            f"🎫┃{member.name}",
            category=category,
            overwrites=overwrites
        )
        
        ticket_data = {
            "channel_id": ticket_channel.id,
            "type": ticket_type,
            "accepted_by": None,
            "owner_id": str(member.id)
        }
        tickets_db[str(member.id)] = ticket_data
        tickets_by_channel[ticket_channel.id] = ticket_data
        
        type_names = {
            "tech_support": "💻 دعم فني",
            "server_problem": "⚙️ مشكلة بالسيرفر",
            "admin_problem": "👔 مشكلة بسبب الإدارة"
        }
        
        terms_embed = discord.Embed(
            title="📜 قواعد وشروط فتح التذكرة",
            description=(
                "🔹 يُمنع إرسال رسائل غير ضرورية\n"
                "🔹 احترام فريق الدعم\n"
                "🔹 شرح المشكلة بوضوح\n"
                "🔹 عدم فتح تذاكر متعددة لنفس المشكلة\n"
                "🔹 الانتظار حتى يتم قبول التذكرة"
            ),
            color=0xFFA500
        )
        
        embed = discord.Embed(
            title="🎫 تذكرة دعم جديدة",
            description=f"**النوع:** {type_names[ticket_type]}\n\nمرحباً {member.mention}!\n\nالرجاء انتظار الرد من فريق الدعم.",
            color=0x00FF00
        )
        embed.set_footer(text="✅ سيتم الرد عليك قريباً")
        
        mention_text = ""
        if ticket_type == "admin_problem" and coowner_role:
            mention_text = f"{coowner_role.mention}"
        elif admin_role:
            mention_text = f"{admin_role.mention}"
        
        ticket_view = TicketManagementView(ticket_channel.id)
        
        await ticket_channel.send(content=mention_text, embeds=[terms_embed, embed], view=ticket_view)
        await interaction.response.send_message(f"✅ تم إنشاء تذكرتك {ticket_channel.mention}", ephemeral=True)

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketTypeSelect())

class RenameModal(discord.ui.Modal, title="إعادة تسمية التذكرة"):
    new_name = discord.ui.TextInput(
        label="الاسم الجديد",
        placeholder="أدخل اسم القناة الجديد...",
        required=True,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            new_channel_name = self.new_name.value
            await interaction.channel.edit(name=new_channel_name)
            await interaction.response.send_message(f"✅ تم تغيير اسم القناة إلى: **{new_channel_name}**", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ خطأ في تغيير الاسم: {str(e)}", ephemeral=True)

class TicketManagementView(View):
    def __init__(self, channel_id):
        super().__init__(timeout=None)
        self.channel_id = channel_id
    
    @discord.ui.button(label="✅ قبول التذكرة", style=discord.ButtonStyle.success, custom_id="accept_ticket")
    async def accept_ticket(self, interaction: discord.Interaction, button: Button):
        admin_roles = ["👑 • المالك", "🔮 • المالك المشارك", "⚔️ • الإدارة", "🛡️ • المشرف"]
        user_roles = [role.name for role in interaction.user.roles]
        
        if not any(role in admin_roles for role in user_roles):
            await interaction.response.send_message("❌ ليس لديك صلاحية قبول التذكرة!", ephemeral=True)
            return
        
        ticket_data = tickets_by_channel.get(self.channel_id)
        if ticket_data:
            ticket_data["accepted_by"] = str(interaction.user.id)
        
        embed = discord.Embed(
            title="✅ تم قبول التذكرة",
            description=f"{interaction.user.mention} قام بقبول هذه التذكرة وسيساعدك الآن.",
            color=0x00FF00
        )
        await interaction.response.send_message(embed=embed)
    
    @discord.ui.button(label="🔄 إعادة تسمية", style=discord.ButtonStyle.primary, custom_id="rename_ticket")
    async def rename_ticket(self, interaction: discord.Interaction, button: Button):
        admin_roles = ["👑 • المالك", "🔮 • المالك المشارك", "⚔️ • الإدارة"]
        user_roles = [role.name for role in interaction.user.roles]
        
        if not any(role in admin_roles for role in user_roles):
            await interaction.response.send_message("❌ ليس لديك صلاحية إعادة تسمية التذكرة!", ephemeral=True)
            return
        
        modal = RenameModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🔒 إغلاق التذكرة", style=discord.ButtonStyle.danger, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        ticket_data = tickets_by_channel.get(self.channel_id)
        if not ticket_data:
            await interaction.response.send_message("❌ خطأ في بيانات التذكرة!", ephemeral=True)
            return
        
        admin_roles = ["👑 • المالك", "🔮 • المالك المشارك", "⚔️ • الإدارة", "🛡️ • المشرف"]
        user_roles = [role.name for role in interaction.user.roles]
        is_admin = any(role in admin_roles for role in user_roles)
        
        can_close = (
            str(interaction.user.id) == ticket_data["owner_id"] or
            (ticket_data["accepted_by"] and str(interaction.user.id) == ticket_data["accepted_by"]) or
            is_admin
        )
        
        if not can_close:
            await interaction.response.send_message("❌ ليس لديك صلاحية إغلاق التذكرة!", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("⏳ جاري إغلاق التذكرة...", ephemeral=True)
        
        if ticket_data["owner_id"] in tickets_db:
            del tickets_db[ticket_data["owner_id"]]
        if self.channel_id in tickets_by_channel:
            del tickets_by_channel[self.channel_id]
        
        await asyncio.sleep(3)
        await interaction.channel.delete(reason=f"تم إغلاق التذكرة بواسطة {interaction.user}")
    
    @discord.ui.button(label="🗑️ حذف التذكرة", style=discord.ButtonStyle.secondary, custom_id="delete_ticket")
    async def delete_ticket(self, interaction: discord.Interaction, button: Button):
        admin_roles = ["👑 • المالك", "🔮 • المالك المشارك", "⚔️ • الإدارة"]
        user_roles = [role.name for role in interaction.user.roles]
        
        if not any(role in admin_roles for role in user_roles):
            await interaction.response.send_message("❌ ليس لديك صلاحية حذف التذكرة!", ephemeral=True)
            return
        
        ticket_data = tickets_by_channel.get(self.channel_id)
        
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("🗑️ جاري حذف التذكرة...", ephemeral=True)
        
        if ticket_data and ticket_data["owner_id"] in tickets_db:
            del tickets_db[ticket_data["owner_id"]]
        if self.channel_id in tickets_by_channel:
            del tickets_by_channel[self.channel_id]
        
        await asyncio.sleep(2)
        await interaction.channel.delete(reason=f"تم حذف التذكرة بواسطة {interaction.user}")

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

# ==================== Slash Commands ====================

@bot.tree.command(name="مستوى", description="عرض مستوى العضو")
@app_commands.describe(member="العضو الذي تريد عرض مستواه")
async def level_slash(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
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
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ترتيب", description="عرض ترتيب الأعضاء")
async def leaderboard_slash(interaction: discord.Interaction):
    sorted_users = sorted(levels_db.items(), key=lambda x: x[1]["xp"], reverse=True)[:10]
    
    embed = discord.Embed(title="🏆 ترتيب الأعضاء", color=0xFFD700)
    
    for idx, (user_id, data) in enumerate(sorted_users, 1):
        member = interaction.guild.get_member(int(user_id))
        if member:
            embed.add_field(
                name=f"{idx}. {member.name}",
                value=f"المستوى: {data['level']} | الخبرة: {data['xp']}",
                inline=False
            )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="فلوس", description="عرض رصيد العضو")
@app_commands.describe(member="العضو الذي تريد عرض رصيده")
async def balance_slash(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    user_id = str(member.id)
    
    if user_id not in economy_db:
        economy_db[user_id] = {"coins": 0, "bank": 0}
    
    data = economy_db[user_id]
    
    embed = discord.Embed(title=f"💰 رصيد {member.name}", color=0xFFD700)
    embed.add_field(name="المحفظة", value=f"🪙 {data['coins']}", inline=True)
    embed.add_field(name="البنك", value=f"🏦 {data['bank']}", inline=True)
    embed.add_field(name="الإجمالي", value=f"💎 {data['coins'] + data['bank']}", inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="يومي", description="الحصول على المكافأة اليومية")
async def daily_slash(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    
    if user_id not in economy_db:
        economy_db[user_id] = {"coins": 0, "bank": 0, "last_daily": None}
    
    if "last_daily" in economy_db[user_id] and economy_db[user_id]["last_daily"]:
        last = economy_db[user_id]["last_daily"]
        if (datetime.now() - datetime.fromisoformat(last)).days < 1:
            await interaction.response.send_message("❌ حصلت على مكافأتك اليومية! عد غداً.", ephemeral=True)
            return
    
    reward = random.randint(100, 500)
    economy_db[user_id]["coins"] += reward
    economy_db[user_id]["last_daily"] = datetime.now().isoformat()
    
    embed = discord.Embed(
        title="🎁 مكافأة يومية!",
        description=f"حصلت على **{reward}** 🪙",
        color=0x00FF00
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="قمار", description="لعبة القمار")
@app_commands.describe(amount="المبلغ الذي تريد المراهنة عليه")
async def gamble_slash(interaction: discord.Interaction, amount: int):
    user_id = str(interaction.user.id)
    
    if user_id not in economy_db:
        economy_db[user_id] = {"coins": 0, "bank": 0}
    
    if amount <= 0 or economy_db[user_id]["coins"] < amount:
        await interaction.response.send_message("❌ مبلغ غير صالح!", ephemeral=True)
        return
    
    win = random.choice([True, False])
    
    if win:
        economy_db[user_id]["coins"] += amount
        embed = discord.Embed(title="🎰 فزت!", description=f"ربحت **{amount}** 🪙", color=0x00FF00)
    else:
        economy_db[user_id]["coins"] -= amount
        embed = discord.Embed(title="💔 خسرت!", description=f"خسرت **{amount}** 🪙", color=0xFF0000)
    
    await interaction.response.send_message(embed=embed)

# ==================== أوامر الإدارة ====================

@bot.tree.command(name="تحذير", description="تحذير عضو")
@app_commands.describe(member="العضو المراد تحذيره", reason="سبب التحذير")
async def warn_slash(interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد سبب"):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ ليس لديك صلاحية!", ephemeral=True)
        return
    
    user_id = str(member.id)
    
    if user_id not in warnings_db:
        warnings_db[user_id] = []
    
    warnings_db[user_id].append({
        "reason": reason,
        "moderator": str(interaction.user.id),
        "date": datetime.now().isoformat()
    })
    
    embed = discord.Embed(title="⚠️ تحذير", description=f"{member.mention} تم تحذيرك", color=0xFFA500)
    embed.add_field(name="السبب", value=reason, inline=False)
    embed.add_field(name="عدد التحذيرات", value=len(warnings_db[user_id]), inline=False)
    
    await interaction.response.send_message(embed=embed)
    
    if len(warnings_db[user_id]) >= 3:
        await member.timeout(timedelta(hours=1), reason="3 تحذيرات")
        await interaction.followup.send(f"🔇 {member.mention} تم كتمه لمدة ساعة")

@bot.tree.command(name="كتم", description="كتم عضو لفترة محددة")
@app_commands.describe(member="العضو المراد كتمه", minutes="عدد الدقائق", reason="سبب الكتم")
async def mute_slash(interaction: discord.Interaction, member: discord.Member, minutes: int = 10, reason: str = "لا يوجد سبب"):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("❌ ليس لديك صلاحية!", ephemeral=True)
        return
    
    await member.timeout(timedelta(minutes=minutes), reason=reason)
    await interaction.response.send_message(f"🔇 تم كتم {member.mention} لمدة {minutes} دقيقة")

@bot.tree.command(name="مسح", description="مسح عدد من الرسائل")
@app_commands.describe(amount="عدد الرسائل المراد مسحها")
async def clear_slash(interaction: discord.Interaction, amount: int = 10):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ ليس لديك صلاحية!", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"✅ تم مسح {len(deleted)} رسالة", ephemeral=True)

# ==================== أوامر قفل وإخفاء القنوات ====================

@bot.tree.command(name="قفل", description="قفل القناة (فقط الإدارة يمكنهم الكتابة)")
async def lock_slash(interaction: discord.Interaction):
    admin_roles = ["👑 • المالك", "🔮 • المالك المشارك", "⚔️ • الإدارة", "🛡️ • المشرف"]
    user_roles = [role.name for role in interaction.user.roles]
    
    if not any(role in admin_roles for role in user_roles):
        await interaction.response.send_message("❌ ليس لديك صلاحية قفل القناة!", ephemeral=True)
        return
    
    channel = interaction.channel
    await channel.set_permissions(interaction.guild.default_role, send_messages=False)
    
    embed = discord.Embed(
        title="🔒 تم قفل القناة",
        description="يمكن للإدارة فقط الكتابة في هذه القناة",
        color=0xFF0000
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="فتح", description="فتح القناة المقفلة")
async def unlock_slash(interaction: discord.Interaction):
    admin_roles = ["👑 • المالك", "🔮 • المالك المشارك", "⚔️ • الإدارة", "🛡️ • المشرف"]
    user_roles = [role.name for role in interaction.user.roles]
    
    if not any(role in admin_roles for role in user_roles):
        await interaction.response.send_message("❌ ليس لديك صلاحية فتح القناة!", ephemeral=True)
        return
    
    channel = interaction.channel
    await channel.set_permissions(interaction.guild.default_role, send_messages=None)
    
    embed = discord.Embed(
        title="🔓 تم فتح القناة",
        description="يمكن للجميع الكتابة في هذه القناة الآن",
        color=0x00FF00
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="اخفاء", description="إخفاء القناة عن الأعضاء")
async def hide_slash(interaction: discord.Interaction):
    admin_roles = ["👑 • المالك", "🔮 • المالك المشارك", "⚔️ • الإدارة"]
    user_roles = [role.name for role in interaction.user.roles]
    
    if not any(role in admin_roles for role in user_roles):
        await interaction.response.send_message("❌ ليس لديك صلاحية إخفاء القناة!", ephemeral=True)
        return
    
    channel = interaction.channel
    await channel.set_permissions(interaction.guild.default_role, view_channel=False)
    
    embed = discord.Embed(
        title="👁️ تم إخفاء القناة",
        description="لا يمكن للأعضاء العاديين رؤية هذه القناة",
        color=0xFF0000
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="اظهار", description="إظهار القناة المخفية")
async def unhide_slash(interaction: discord.Interaction):
    admin_roles = ["👑 • المالك", "🔮 • المالك المشارك", "⚔️ • الإدارة"]
    user_roles = [role.name for role in interaction.user.roles]
    
    if not any(role in admin_roles for role in user_roles):
        await interaction.response.send_message("❌ ليس لديك صلاحية إظهار القناة!", ephemeral=True)
        return
    
    channel = interaction.channel
    await channel.set_permissions(interaction.guild.default_role, view_channel=None)
    
    embed = discord.Embed(
        title="👁️ تم إظهار القناة",
        description="يمكن للأعضاء رؤية هذه القناة الآن",
        color=0x00FF00
    )
    await interaction.response.send_message(embed=embed)

# ==================== أمر إعطاء الرتبة ====================

def get_role_rank(role_name):
    """الحصول على ترتيب الرتبة في التسلسل الهرمي (رقم أقل = رتبة أعلى)"""
    if role_name in ROLE_HIERARCHY:
        return ROLE_HIERARCHY.index(role_name)
    return 999

def get_highest_staff_role(user_roles):
    """الحصول على أعلى رتبة إدارية للمستخدم"""
    highest_rank = 999
    highest_role = None
    
    for role in user_roles:
        rank = get_role_rank(role.name)
        if rank < highest_rank:
            highest_rank = rank
            highest_role = role.name
    
    return highest_role, highest_rank

@bot.tree.command(name="اعطاء", description="إعطاء رتبة لعضو")
@app_commands.describe(member="العضو", role="الرتبة")
async def give_role_slash(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    user_highest_role, user_rank = get_highest_staff_role(interaction.user.roles)
    target_role_rank = get_role_rank(role.name)
    
    if user_rank == 999:
        await interaction.response.send_message("❌ ليس لديك صلاحية إعطاء رتب!", ephemeral=True)
        return
    
    if target_role_rank <= user_rank:
        await interaction.response.send_message(
            f"❌ لا يمكنك إعطاء رتبة {role.mention}!\n"
            f"رتبتك: **{user_highest_role}**\n"
            f"يمكنك فقط إعطاء الرتب الأقل من رتبتك.",
            ephemeral=True
        )
        return
    
    if target_role_rank == 999:
        await interaction.response.send_message("❌ هذه الرتبة غير موجودة في النظام الهرمي!", ephemeral=True)
        return
    
    roles_to_remove = []
    for member_role in member.roles:
        if member_role.name == "@everyone":
            continue
        
        if member_role.name not in ROLE_HIERARCHY:
            continue
        
        member_role_rank = get_role_rank(member_role.name)
        if member_role_rank > target_role_rank:
            roles_to_remove.append(member_role)
    
    removed_roles_names = [r.name for r in roles_to_remove]
    
    if roles_to_remove:
        await member.remove_roles(*roles_to_remove)
    
    await member.add_roles(role)
    
    embed = discord.Embed(
        title="✅ تم إعطاء الرتبة",
        description=f"تم إعطاء {member.mention} رتبة {role.mention}",
        color=0x00FF00
    )
    
    if removed_roles_names:
        embed.add_field(
            name="🗑️ الرتب المحذوفة",
            value="\n".join([f"• {name}" for name in removed_roles_names]),
            inline=False
        )
    
    embed.set_footer(text=f"بواسطة {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

# ==================== إعداد السيرفر ====================

@bot.tree.command(name="اعداد_السيرفر", description="إعداد السيرفر تلقائياً")
async def setup_server_slash(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ ليس لديك صلاحية!", ephemeral=True)
        return
    
    await interaction.response.defer()
    guild = interaction.guild
    
    await interaction.followup.send("🚀 **بدء إعداد السيرفر...**")
    
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
    
    if ticket_channel:
        ticket_embed = discord.Embed(
            title="🎫 نظام الدعم الفني",
            description="اختر نوع التذكرة من القائمة المنسدلة:",
            color=0x00FF00
        )
        view = TicketView()
        await ticket_channel.send(embed=ticket_embed, view=view)
    
    await interaction.followup.send("✅ **تم إعداد السيرفر بنجاح!**")

@bot.tree.command(name="مساعدة", description="عرض قائمة الأوامر")
async def help_slash(interaction: discord.Interaction):
    embed = discord.Embed(title="📚 أوامر البوت", color=0x3498DB, description="جميع الأوامر المتاحة:")
    
    embed.add_field(name="⚙️ إدارة السيرفر", value=(
        "`/اعداد_السيرفر` - إعداد السيرفر\n"
        "`/قفل` - قفل القناة\n"
        "`/فتح` - فتح القناة\n"
        "`/اخفاء` - إخفاء القناة\n"
        "`/اظهار` - إظهار القناة"
    ), inline=False)
    
    embed.add_field(name="👮 الإشراف", value=(
        "`/تحذير` - تحذير عضو\n"
        "`/كتم` - كتم عضو\n"
        "`/مسح` - مسح رسائل\n"
        "`/اعطاء` - إعطاء رتبة"
    ), inline=False)
    
    embed.add_field(name="🎮 المستويات والاقتصاد", value=(
        "`/مستوى` - عرض المستوى\n"
        "`/ترتيب` - عرض الترتيب\n"
        "`/فلوس` - عرض الرصيد\n"
        "`/يومي` - مكافأة يومية\n"
        "`/قمار` - لعبة القمار"
    ), inline=False)
    
    await interaction.response.send_message(embed=embed)

# ==================== الأحداث ====================

@bot.event
async def on_ready():
    print("=" * 50)
    print(f"🤖 البوت جاهز: {bot.user.name}")
    print("✅ متصل بالإنترنت")
    print(f"📊 متصل بـ {len(bot.guilds)} سيرفر")
    print("☁️ يعمل على السحابة")
    print("=" * 50)
    
    bot.add_view(TicketView())
    
    try:
        synced = await bot.tree.sync()
        print(f"✅ تم مزامنة {len(synced)} أمر Slash")
    except Exception as e:
        print(f"❌ خطأ في المزامنة: {e}")

@bot.event
async def on_member_join(member):
    welcome_channel = discord.utils.get(member.guild.text_channels, name="👋・الترحيب")
    if welcome_channel:
        embed = discord.Embed(
            title=f"🎉 مرحباً {member.name}!",
            description=f"أهلاً بك في **{member.guild.name}**!\n\nأنت العضو رقم **{member.guild.member_count}**",
            color=0x00FF00
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text=f"انضم في {datetime.now().strftime('%Y-%m-%d')}")
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
    
    keep_alive()
    
    print("🤖 بدء تشغيل البوت...")
    print("=" * 50)
    
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ خطأ: {e}")
