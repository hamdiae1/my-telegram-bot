# Telegram Admin Bot (aiogram)

هذا بوت تيليجرام مصمم للتواصل بين المستخدمين والأدمن، مع ميزة التحقق من الاشتراك في القناة.

## المميزات
- إرسال الرسائل (نصوص، صور، فيديو، ملفات) للأدمن.
- إمكانية رد الأدمن مباشرة على رسائل المستخدمين.
- التحقق التلقائي من الاشتراك في قناة معينة.
- يعمل 24/7 عند رفعه على استضافة.

## المتطلبات
- Python 3.8+
- توكن بوت من [@BotFather](https://t.me/BotFather).

## الإعداد المحلي
1. قم بتثبيت المكتبات المطلوبة:
   ```bash
   pip install -r requirements.txt
   ```
2. قم بإنشاء ملف `.env` وأضف بياناتك:
   ```env
   BOT_TOKEN=your_token_here
   CHANNEL_USERNAME=@your_channel
   ADMIN_USERNAME=your_username
   ```
3. شغل البوت:
   ```bash
   python bot.py
   ```

## النشر على الاستضافة (Render / Railway / Koyeb)

### Render
1. قم بإنشاء حساب على [Render](https://render.com).
2. أنشئ "New Web Service" أو "Background Worker" (يُفضل Background Worker للبوتات).
3. اربط مستودع GitHub الخاص بك.
4. في إعدادات البيئة (Environment Variables)، أضف `BOT_TOKEN` و `CHANNEL_USERNAME` و `ADMIN_USERNAME`.
5. سيقوم Render بتشغيل البوت تلقائياً باستخدام `Dockerfile` أو `Procfile`.

### Railway
1. قم بإنشاء حساب على [Railway](https://railway.app).
2. أنشئ مشروعاً جديداً واربطه بمستودع GitHub.
3. أضف متغيرات البيئة في تبويب "Variables".
4. سيتم النشر تلقائياً.

---
**ملاحظة:** يستخدم البوت قاعدة بيانات SQLite (`messages.db`). في الاستضافات المجانية، قد يتم مسح البيانات عند إعادة تشغيل الحاوية ما لم يتم استخدام "Persistent Volume".
