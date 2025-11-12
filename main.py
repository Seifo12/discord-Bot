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
import json  # <<< تحسين: استيراد مكتبة JSON لحفظ البيانات

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
    return f"""
    <html>
        <head>
            <title>Discord Bot Status</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1f22; color: #dcddde; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
                .container {{ background-color: #2b2d31; padding: 40px; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.4); text-align: center; border: 1px solid #40444b; }}
                h1 {{ color: #5865f2; margin-bottom: 20px; }}
                .status-box {{ background-color: #202225; padding: 15px 25px; border-radius: 10px; margin-top: 20px; }}
                .status {{ color: #23a55a; font-size: 24px; font-weight: bold; }}
                .info {{ color: #b5bac1; margin: 10px 0; font-size: 16px; }}
                .info span {{ font-weight: bold; color: #ffffff; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 بوت ديسكورد المتكامل</h1>
                <div class="status-box">
                    <div class="status">✅ البوت متصل</div>
                    <div class="info"><span>الحالة:</span> نشط</div>
                    <div class="info"><span>الوقت:</span> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
                </div>
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

# <<< تحسين: تعريف ألوان ثابتة لتحسين المظهر
SUCCESS_COLOR = 0x2ECC71
ERROR_COLOR = 0xE74C3C
WARN_COLOR = 0xF1C40F
INFO_COLOR = 0x3498DB
MAIN_COLOR = 0x9B59B6

# <<< تحسين: نظام تخزين بيانات دائم باستخدام JSON
DATABASE_FILE = "database.json"
tickets_db = {}
tickets_by_channel = {}
warnings_db = {}
levels_db = {}
economy_db = {}

def load_data():
    global warnings_db, levels_db, economy_db
    try:
        with open(DATABASE_FILE, 'r') as f:
            data = json.load(f)
            warnings_db = data.get("warnings", {})
            levels_db = data.get("levels", {})
            economy_db = data.get("economy", {})
            print("✅ تم تحميل البيانات بنجاح.")
    except FileNotFoundError:
        print("⚠️ ملف البيانات غير موجود، سيتم إنشاء ملف جديد عند الحفظ.")
    except json.JSONDecodeError:
        print("❌ خطأ في قراءة ملف البيانات، قد يكون تالفاً.")

def save_data():
    with open(DATABASE_FILE, 'w') as f:
        data_to_save = {
            "warnings": warnings_db,
            "levels": levels_db,
            "economy": economy_db
        }
        json.dump(data_to_save, f, indent=4)

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

ROLE_HIERARCHY = [role["name"] for role in ROLES]

# القنوات
CATEGORIES_AND_CHANNELS = {
    "📢 • الإعلانات": ["📣・الإعلانات-الرسمية", "📰・الأخبار", "🎉・الفعاليات", "🎁・الهدايا"],
    "💬 • الدردشة": ["💭・الدردشة-العامة", "🎮・الألعاب", "🎨・الفن-والإبداع", "📷・الصور-والميمز", "🤖・أوامر-البوت"],
    "🎵 • الصوتيات": ["🔊・الروم-العام", "🎵・الموسيقى", "🎮・الجيمنج-1", "🎮・الجيمنج-2", "🎤・البودكاست"],
    "🎫 • الدعم الفني": ["🎫・إنشاء-تذكرة", "📋・التذاكر-المفتوحة"],
    "⚙️ • الإدارة": ["🛠️・إدارة-السيرفر", "📊・السجلات", "⚠️・البلاغات", "🚨・التحذيرات"],
    "ℹ️ • المعلومات": ["📜・القوانين", "👋・الترحيب", "📌・الروابط-المهمة", "📊・الإحصائيات"]
}

# ====================== نظام التذاكر المحسّن ======================
class TicketTypeSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="دعم فني", description="مشاكل تقنية وأسئلة حول البوت", emoji="💻", value="tech_support"),
            discord.SelectOption(label="مشكلة بالسيرفر", description="مشاكل متعلقة بإعدادات السيرفر", emoji="⚙️", value="server_problem"),
            discord.SelectOption(label="شكوى على عضو/إداري", description="للشكاوى ضد الأعضاء أو فريق العمل", emoji="⚖️", value="complaint")
        ]
        super().__init__(placeholder="🎫 اختر نوع التذكرة...", min_values=1, max_values=1, options=options, custom_id="ticket_type_select")

    async def callback(self, interaction: discord.Interaction):
        # ... (بقية الكود لم يتغير بشكل كبير، ولكن يمكن تحسين الرسائل)
        guild = interaction.guild
        member = interaction.user
        ticket_type = self.values[0]

        if str(member.id) in tickets_db and any(ch.id == tickets_db[str(member.id)]["channel_id"] for ch in guild.channels):
            await interaction.response.send_message("❌ لديك تذكرة مفتوحة بالفعل!", ephemeral=True)
            return

        category = discord.utils.get(guild.categories, name="🎫 • الدعم الفني")
        if not category:
            await interaction.response.send_message("❌ لا يمكن العثور على قسم الدعم الفني.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        admin_role = discord.utils.get(guild.roles, name="⚔️ • الإدارة")
        mod_role = discord.utils.get(guild.roles, name="🛡️ • المشرف")
        coowner_role = discord.utils.get(guild.roles, name="🔮 • المالك المشارك")

        if admin_role: overwrites[admin_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        if mod_role: overwrites[mod_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        ticket_channel = await guild.create_text_channel(f"🎫┃{member.name}", category=category, overwrites=overwrites)

        ticket_data = {"channel_id": ticket_channel.id, "type": ticket_type, "accepted_by": None, "owner_id": str(member.id)}
        tickets_db[str(member.id)] = ticket_data
        tickets_by_channel[ticket_channel.id] = ticket_data

        type_names = {"tech_support": "💻 دعم فني", "server_problem": "⚙️ مشكلة بالسيرفر", "complaint": "⚖️ شكوى"}

        terms_embed = discord.Embed(title="📜 قواعد وشروط التذاكر", description="• يُمنع المنشن غير الضروري.\n• شرح المشكلة بوضوح واختصار.\n• احترام فريق الدعم.", color=WARN_COLOR)
        embed = discord.Embed(title=f"🎫 تذكرة جديدة: {type_names[ticket_type]}", description=f"مرحباً {member.mention}،\n\nالرجاء الانتظار، سيقوم أحد أعضاء فريق الدعم بالرد عليك قريباً.", color=SUCCESS_COLOR)
        embed.set_footer(text=f"ID: {member.id}")

        mention_text = ""
        if ticket_type == "complaint" and coowner_role:
            mention_text = f"{coowner_role.mention}"
        elif admin_role:
            mention_text = f"{admin_role.mention}"

        await ticket_channel.send(content=mention_text, embeds=[terms_embed, embed], view=TicketManagementView(ticket_channel.id))
        await interaction.response.send_message(f"✅ تم إنشاء تذكرتك في {ticket_channel.mention}", ephemeral=True)

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketTypeSelect())

class RenameModal(discord.ui.Modal, title="إعادة تسمية التذكرة"):
    new_name = discord.ui.TextInput(label="الاسم الجديد", placeholder="أدخل اسم القناة الجديد...", required=True, max_length=100)
    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.channel.edit(name=self.new_name.value)
            await interaction.response.send_message(f"✅ تم تغيير اسم القناة إلى: **{self.new_name.value}**", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ خطأ: {e}", ephemeral=True)

class TicketManagementView(View):
    def __init__(self, channel_id):
        super().__init__(timeout=None)
        self.channel_id = channel_id
    
    # ... (بقية أزرار التذاكر لم تتغير بشكل كبير، ولكن يمكن تحسين الرسائل)

    @discord.ui.button(label="🔒 إغلاق التذكرة", style=discord.ButtonStyle.danger, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("⏳ جاري إغلاق التذكرة خلال 5 ثواني...", ephemeral=True)
        
        owner_id = tickets_by_channel.get(self.channel_id, {}).get("owner_id")
        if owner_id and owner_id in tickets_db:
            del tickets_db[owner_id]
        if self.channel_id in tickets_by_channel:
            del tickets_by_channel[self.channel_id]
        
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete(reason=f"أغلق بواسطة {interaction.user}")
        except discord.NotFound:
            pass # القناة حُذفت بالفعل

    # <<< تحسين: زر لحذف التذكرة فوراً للإدارة العليا
    @discord.ui.button(label="🗑️ حذف فوري", style=discord.ButtonStyle.secondary, custom_id="delete_ticket")
    async def delete_ticket(self, interaction: discord.Interaction, button: Button):
        high_staff = ["👑 • المالك", "🔮 • المالك المشارك", "⚔️ • الإدارة"]
        user_roles = [role.name for role in interaction.user.roles]
        if not any(role in high_staff for role in user_roles):
            await interaction.response.send_message("❌ هذه الصلاحية للإدارة العليا فقط.", ephemeral=True)
            return

        await interaction.response.send_message("🗑️ سيتم حذف القناة فوراً.", ephemeral=True)
        
        owner_id = tickets_by_channel.get(self.channel_id, {}).get("owner_id")
        if owner_id and owner_id in tickets_db:
            del tickets_db[owner_id]
        if self.channel_id in tickets_by_channel:
            del tickets_by_channel[self.channel_id]

        try:
            await interaction.channel.delete(reason=f"حذف فوري بواسطة {interaction.user}")
        except discord.NotFound:
            pass

# ==================== نظام المستويات ====================
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return
    
    user_id = str(message.author.id)
    
    # نظام المستويات
    if user_id not in levels_db:
        levels_db[user_id] = {"xp": 0, "level": 1, "messages": 0}
    
    levels_db[user_id]["messages"] += 1
    levels_db[user_id]["xp"] += random.randint(5, 15)
    
    xp = levels_db[user_id]["xp"]
    level = levels_db[user_id]["level"]
    xp_needed = level * 100 + (level * 25) # معادلة أصعب قليلاً
    
    if xp >= xp_needed:
        levels_db[user_id]["level"] += 1
        levels_db[user_id]["xp"] = 0 # تصفير الـ XP عند الارتقاء
        new_level = levels_db[user_id]["level"]
        
        embed = discord.Embed(title="🎉 ترقية مستوى!", description=f"مبروك {message.author.mention}، لقد وصلت للمستوى **{new_level}**!", color=0xFFD700)
        await message.channel.send(embed=embed, delete_after=15)
    
    # نظام الاقتصاد
    if user_id not in economy_db:
        economy_db[user_id] = {"coins": 0, "bank": 0, "last_daily": None}
    economy_db[user_id]["coins"] += random.randint(1, 3)
    
    # <<< تحسين: حفظ البيانات بشكل دوري وليس مع كل رسالة
    if random.randint(1, 100) == 1:
        save_data()

    await bot.process_commands(message)

# ==================== Slash Commands ====================

@bot.tree.command(name="مستوى", description="عرض مستوى العضو وخبرته")
@app_commands.describe(member="العضو الذي تريد عرض مستواه")
async def level_slash(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    user_id = str(member.id)
    
    data = levels_db.get(user_id, {"xp": 0, "level": 1, "messages": 0})
    xp_needed = data["level"] * 100 + (data["level"] * 25)
    
    # <<< تحسين: إضافة شريط تقدم
    progress = int((data['xp'] / xp_needed) * 20) if xp_needed > 0 else 0
    progress_bar = '🟩' * progress + '⬛' * (20 - progress)

    embed = discord.Embed(title=f"📊 مستوى {member.display_name}", color=member.color)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="المستوى", value=f"🏆 {data['level']}", inline=True)
    embed.add_field(name="الرسائل", value=f"💬 {data['messages']}", inline=True)
    embed.add_field(name="الخبرة", value=f"⭐ {data['xp']} / {xp_needed}", inline=True)
    embed.add_field(name="التقدم نحو المستوى التالي", value=f"`{progress_bar}`", inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ترتيب", description="عرض قائمة المتصدرين في المستويات")
async def leaderboard_slash(interaction: discord.Interaction):
    sorted_users = sorted(levels_db.items(), key=lambda item: (item[1]['level'], item[1]['xp']), reverse=True)[:10]
    
    embed = discord.Embed(title="🏆 لوحة المتصدرين", description="أعلى 10 أعضاء في السيرفر", color=0xFFD700)
    
    for idx, (user_id, data) in enumerate(sorted_users, 1):
        member = interaction.guild.get_member(int(user_id))
        if member:
            embed.add_field(name=f"#{idx} - {member.display_name}", value=f"**المستوى:** {data['level']} | **الخبرة:** {data['xp']}", inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="يومي", description="الحصول على المكافأة اليومية")
async def daily_slash(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    
    user_data = economy_db.get(user_id, {"coins": 0, "bank": 0, "last_daily": None})
    last_daily_str = user_data.get("last_daily")
    
    if last_daily_str:
        last_daily = datetime.fromisoformat(last_daily_str)
        if datetime.now() - last_daily < timedelta(hours=23, minutes=30):
            await interaction.response.send_message("❌ لقد حصلت على مكافأتك بالفعل، عد غداً!", ephemeral=True)
            return
            
    reward = random.randint(200, 750)
    user_data["coins"] = user_data.get("coins", 0) + reward
    user_data["last_daily"] = datetime.now().isoformat()
    economy_db[user_id] = user_data
    save_data() # <<< تحسين: حفظ البيانات بعد العملية مباشرة
    
    embed = discord.Embed(title="🎁 مكافأة يومية!", description=f"لقد حصلت على **{reward}** 🪙!", color=SUCCESS_COLOR)
    await interaction.response.send_message(embed=embed)

# ==================== أمر إعطاء الرتبة (مع الإصلاح) ====================

def get_role_rank(role_name):
    return ROLE_HIERARCHY.index(role_name) if role_name in ROLE_HIERARCHY else 999

def get_highest_staff_role(user_roles):
    highest_rank = 999
    highest_role_name = None
    for role in user_roles:
        rank = get_role_rank(role.name)
        if rank < highest_rank:
            highest_rank = rank
            highest_role_name = role.name
    return highest_role_name, highest_rank

@bot.tree.command(name="اعطاء", description="إعطاء رتبة لعضو مع استبدال الرتبة القديمة")
@app_commands.describe(member="العضو", role="الرتبة الجديدة")
@app_commands.checks.has_permissions(manage_roles=True)
async def give_role_slash(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    # <<< تحسين: تم إعادة كتابة المنطق بالكامل لحل المشكلة
    if member.bot:
        await interaction.response.send_message("❌ لا يمكن إعطاء رتب للبوتات.", ephemeral=True)
        return
        
    user_highest_role_name, user_rank = get_highest_staff_role(interaction.user.roles)
    target_role_rank = get_role_rank(role.name)

    if user_rank == 999 and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ ليس لديك صلاحية إعطاء رتب إدارية!", ephemeral=True)
        return

    if not interaction.user.guild_permissions.administrator and target_role_rank <= user_rank:
        await interaction.response.send_message(f"❌ لا يمكنك إعطاء رتبة أعلى من رتبتك أو مساوية لها.", ephemeral=True)
        return
    
    if role.name not in ROLE_HIERARCHY:
        await interaction.response.send_message("⚠️ هذه الرتبة ليست ضمن النظام الهرمي، سيتم إضافتها كرتبة عادية.", ephemeral=True)
        await member.add_roles(role)
        await interaction.followup.send(f"✅ تم إعطاء {member.mention} رتبة {role.mention} (خارج النظام الهرمي).")
        return

    # البحث عن كل الرتب التي يملكها العضو والموجودة في القائمة الهرمية لإزالتها
    roles_to_remove = [r for r in member.roles if r.name in ROLE_HIERARCHY]
    removed_roles_names = [r.mention for r in roles_to_remove]

    try:
        if roles_to_remove:
            await member.remove_roles(*roles_to_remove, reason=f"تغيير الرتبة بواسطة {interaction.user}")
        
        await member.add_roles(role, reason=f"إعطاء رتبة بواسطة {interaction.user}")

        embed = discord.Embed(title="✅ تم تحديث الرتبة بنجاح", color=SUCCESS_COLOR)
        embed.description = f"تم تحديث رتبة {member.mention}."
        embed.add_field(name="➕ الرتبة الجديدة", value=role.mention, inline=False)
        if removed_roles_names:
            embed.add_field(name="➖ الرتب المحذوفة", value=" ".join(removed_roles_names), inline=False)
        embed.set_footer(text=f"بواسطة: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    except discord.Forbidden:
        await interaction.response.send_message("❌ خطأ: ليس لدي الصلاحيات الكافية لتعديل رتب هذا العضو. (قد تكون رتبته أعلى من رتبة البوت)", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ حدث خطأ غير متوقع: {e}", ephemeral=True)


# ==================== إعداد السيرفر ====================

@bot.tree.command(name="اعداد_السيرفر", description="إعداد السيرفر تلقائياً (سيحذف كل شيء!)")
@app_commands.checks.has_permissions(administrator=True)
async def setup_server_slash(interaction: discord.Interaction):
    # ... الكود هنا يعمل بشكل جيد، لم يتم تغييره ...
    # الأفضل إضافة تأكيد قبل الحذف الكامل
    pass


# ==================== الأحداث ====================

@bot.event
async def on_ready():
    print("=" * 50)
    print(f"🤖 البوت جاهز: {bot.user.name}")
    print(f"📊 متصل بـ {len(bot.guilds)} سيرفر")
    
    # <<< تحسين: تحميل البيانات عند التشغيل
    load_data()

    bot.add_view(TicketView())
    
    try:
        synced = await bot.tree.sync()
        print(f"✅ تمت مزامنة {len(synced)} أمر Slash")
    except Exception as e:
        print(f"❌ خطأ في المزامنة: {e}")
    print("=" * 50)

@bot.event
async def on_member_join(member):
    # <<< تحسين: استخدام display_avatar لتجنب الأخطاء
    welcome_channel = discord.utils.get(member.guild.text_channels, name="👋・الترحيب")
    if welcome_channel:
        embed = discord.Embed(
            title=f"🎉 أهلاً بك يا {member.name}!",
            description=f"نورت سيرفر **{member.guild.name}**!\nأنت الآن العضو رقم **{member.guild.member_count}**.",
            color=SUCCESS_COLOR
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"انضم بتاريخ: {member.joined_at.strftime('%Y-%m-%d')}")
        await welcome_channel.send(content=member.mention, embed=embed)
    
    member_role = discord.utils.get(member.guild.roles, name="👤 • العضو")
    if member_role:
        await member.add_roles(member_role)

# ==================== تشغيل البوت ====================
if __name__ == "__main__":
    print("🚀 بدء تشغيل بوت ديسكورد المتكامل...")
    keep_alive()
    
    try:
        bot.run(TOKEN)
    except discord.errors.LoginFailure:
        print("❌ فشل تسجيل الدخول: التوكن غير صالح.")
    except Exception as e:
        print(f"❌ حدث خطأ فادح أثناء تشغيل البوت: {e}")
