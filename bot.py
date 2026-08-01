import logging
import asyncio
import sqlite3
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest

# إعدادات البوت من متغيرات البيئة
TOKEN = os.getenv("BOT_TOKEN", "8961025883:AAEgw9oz_406jKnxsWQa95uFpWHkbNtH1mA")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@ArabicRiwayat")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "TitanNebula")  # بدون @ للتحقق

# إعداد السجلات
logging.basicConfig(level=logging.INFO)

# إعداد قاعدة البيانات لتخزين الرسائل (للرد)
def init_db():
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS message_map
                 (admin_msg_id INTEGER PRIMARY KEY, user_id INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS admin_info
                 (id INTEGER PRIMARY KEY, username TEXT)''')
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
    c.execute("INSERT OR REPLACE INTO admin_info VALUES (?, ?)", (admin_id, username))
    conn.commit()
    conn.close()

def get_admin_id():
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute("SELECT id FROM admin_info WHERE username = ?", (ADMIN_USERNAME,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

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
    builder.row(types.InlineKeyboardButton(text="قناة الروايات العربية 📚", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))
    builder.row(types.InlineKeyboardButton(text="تحقق من الاشتراك ✅", callback_data="check_sub"))
    return builder.as_markup()

# معالج أمر /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    # إذا كان المستخدم هو الأدمن، نحفظ معرفه
    if message.from_user.username == ADMIN_USERNAME:
        save_admin_id(message.from_user.id, ADMIN_USERNAME)
        await message.answer("أهلاً بك يا أدمن! تم التعرف عليك بنجاح. ستصلك رسائل المستخدمين هنا ويمكنك الرد عليها مباشرة.")
        return

    is_sub = await check_subscription(message.from_user.id)
    if not is_sub:
        await message.answer(
            f"عذراً! يجب عليك الاشتراك في قناة {CHANNEL_USERNAME} أولاً لتتمكن من استخدام البوت.",
            reply_markup=get_sub_keyboard()
        )
    else:
        await message.answer("أهلاً بك! يمكنك الآن إرسال رسالتك (نص، صور، فيديو، ملفات، إلخ) وسيتم إيصالها للأدمن.")

# معالج التحقق من الاشتراك عبر الزر
@dp.callback_query(F.data == "check_sub")
async def process_check_sub(callback: types.CallbackQuery):
    is_sub = await check_subscription(callback.from_user.id)
    if is_sub:
        await callback.message.edit_text("شكراً لاشتراكك! يمكنك الآن إرسال رسائلك للأدمن.")
    else:
        await callback.answer("لم تشترك بعد! يرجى الاشتراك ثم المحاولة مرة أخرى.", show_alert=True)

# معالج الرسائل من المستخدمين إلى الأدمن
@dp.message(F.chat.type == "private")
async def handle_messages(message: types.Message):
    # تجاهل رسائل الأدمن إذا لم تكن رداً
    if message.from_user.username == ADMIN_USERNAME:
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
        await message.answer("يجب عليك الاشتراك في القناة أولاً!", reply_markup=get_sub_keyboard())
        return

    admin_id = get_admin_id()
    if not admin_id:
        await message.answer("عذراً، الأدمن غير متاح حالياً. يرجى المحاولة لاحقاً.")
        return

    # إرسال الرسالة للأدمن
    try:
        # نستخدم copy_message لضمان وصول كل أنواع الوسائط
        sent_msg = await bot.copy_message(
            chat_id=admin_id,
            from_chat_id=message.chat.id,
            message_id=message.message_id,
            caption=f"👤 رسالة من: @{message.from_user.username or 'بدون يوزرنيم'}\n🆔 ID: {message.from_user.id}\n\n{message.caption or ''}"
        )
        save_message_map(sent_msg.message_id, message.from_user.id)
        await message.answer("✅ تم إرسال رسالتك للأدمن بنجاح.")
    except Exception as e:
        await message.answer("❌ حدث خطأ أثناء إرسال الرسالة.")
        logging.error(f"Error forwarding to admin: {e}")

async def main():
    init_db()
    print("البوت يعمل الآن...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
