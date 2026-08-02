import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# إعدادات البوت
TOKEN = "8961025883:AAFY8fQjKdRBJIL3JCYRfjAfmu5KS_opwcw"
CHANNEL_USERNAME = "@ArabicRiwayat"
ADMIN_USERNAME = "TitanNebula"

logging.basicConfig(level=logging.INFO)

# قاعدة بيانات لحفظ ربط الرسائل
def init_db():
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS message_map
                 (admin_msg_id INTEGER PRIMARY KEY, user_id INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS admin_info
                 (username TEXT PRIMARY KEY, id INTEGER)''')
    conn.commit()
    conn.close()

def save_message_map(admin_msg_id, user_id):
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO message_map VALUES (?, ?)", (admin_msg_id, user_id))
    conn.commit()
    conn.close()

def get_user_id(admin_msg_id):
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM message_map WHERE admin_msg_id = ?", (admin_msg_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def save_admin_id(admin_id, username):
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO admin_info VALUES (?, ?)", (username, admin_id))
    conn.commit()
    conn.close()

def get_admin_id():
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute("SELECT id FROM admin_info WHERE username = ?", (ADMIN_USERNAME,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# دالة لعرض معلومات المستخدم بشكل واضح
def get_user_display_info(user):
    info_parts = []
    # الاسم الكامل
    full_name = user.first_name or ""
    if user.last_name:
        full_name += f" {user.last_name}"
    if full_name:
        info_parts.append(f"👤 الاسم: {full_name}")
    # اليوزرنيم
    if user.username:
        info_parts.append(f"🔗 اليوزر: @{user.username}")
    else:
        info_parts.append("🔗 اليوزر: لا يوجد")
    # المعرف
    info_parts.append(f"🆔 ID: {user.id}")
    return "\n".join(info_parts)

# تهيئة البوت والموزع
bot = Bot(token=TOKEN)
dp = Dispatcher()

# دالة التحقق من الاشتراك
async def check_subscription(user_id: int):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# لوحة مفاتيح الاشتراك
def get_sub_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📚 اشترك في القناة", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))
    builder.row(types.InlineKeyboardButton(text="✅ تحقق من الاشتراك", callback_data="check_sub"))
    return builder.as_markup()

# معالج أمر /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    # إذا كان المستخدم هو الأدمن، نحفظ معرفه
    if message.from_user.username and message.from_user.username.lower() == ADMIN_USERNAME.lower():
        save_admin_id(message.from_user.id, ADMIN_USERNAME)
        await message.answer("أهلاً بك يا أدمن! ✅\nتم التعرف عليك بنجاح.\nستصلك رسائل المستخدمين هنا ويمكنك الرد عليها بعمل Reply.")
        return

    is_sub = await check_subscription(message.from_user.id)
    if not is_sub:
        await message.answer(
            f"مرحباً بك! 👋\n\nللتمكن من استخدام البوت، يجب عليك الاشتراك في قناتنا أولاً:\n{CHANNEL_USERNAME}\n\nبعد الاشتراك اضغط على زر التحقق 👇",
            reply_markup=get_sub_keyboard()
        )
    else:
        await message.answer("أهلاً بك! ✅\n\nيمكنك الآن إرسال رسالتك وسيتم إيصالها للإدارة.\nيمكنك إرسال: نصوص، صور، فيديو، ملفات، صوتيات، ستيكرات.")

# معالج التحقق من الاشتراك عبر الزر
@dp.callback_query(F.data == "check_sub")
async def process_check_sub(callback: types.CallbackQuery):
    is_sub = await check_subscription(callback.from_user.id)
    if is_sub:
        await callback.message.edit_text("شكراً لاشتراكك! ✅\n\nيمكنك الآن إرسال رسائلك للإدارة.")
    else:
        await callback.answer("❌ لم تشترك بعد! يرجى الاشتراك في القناة ثم المحاولة مرة أخرى.", show_alert=True)

# معالج الرسائل من المستخدمين إلى الأدمن
@dp.message(F.chat.type == "private")
async def handle_messages(message: types.Message):
    # تجاهل رسائل الأدمن إذا لم تكن رداً
    if message.from_user.username and message.from_user.username.lower() == ADMIN_USERNAME.lower():
        if message.reply_to_message:
            user_id = get_user_id(message.reply_to_message.message_id)
            if user_id:
                try:
                    await bot.copy_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id)
                    await message.reply("✅ تم إرسال ردك للمستخدم.")
                except Exception as e:
                    await message.reply(f"❌ فشل إرسال الرد: {e}")
            else:
                await message.reply("❌ لم يتم العثور على المستخدم المرتبط بهذه الرسالة.")
        return

    # التحقق من الاشتراك للمستخدمين العاديين
    is_sub = await check_subscription(message.from_user.id)
    if not is_sub:
        await message.answer("⚠️ يجب عليك الاشتراك في القناة أولاً!", reply_markup=get_sub_keyboard())
        return

    admin_id = get_admin_id()
    if not admin_id:
        await message.answer("عذراً، الإدارة غير متاحة حالياً. يرجى المحاولة لاحقاً.")
        return

    # إرسال معلومات المستخدم ثم الرسالة للأدمن
    try:
        user_info = get_user_display_info(message.from_user)
        # إرسال معلومات المرسل
        await bot.send_message(chat_id=admin_id, text=f"📩 رسالة جديدة:\n{'─' * 20}\n{user_info}\n{'─' * 20}")
        # نسخ الرسالة الأصلية للأدمن
        sent_msg = await bot.copy_message(
            chat_id=admin_id,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
        save_message_map(sent_msg.message_id, message.from_user.id)
        await message.answer("✅ تم إرسال رسالتك بنجاح.")
    except Exception as e:
        await message.answer("❌ حدث خطأ أثناء إرسال الرسالة. حاول مرة أخرى.")
        logging.error(f"Error forwarding to admin: {e}")

async def main():
    init_db()
    print("✅ البوت يعمل الآن...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
