# استخدام صورة Python الرسمية
FROM python:3.11-slim

# إعداد دليل العمل
WORKDIR /app

# نسخ ملف المتطلبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات المشروع
COPY . .

# تشغيل البوت
CMD ["python", "bot.py"]
