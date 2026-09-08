<div align="center">

<img src="https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/main/Arista/assets/images/logo.png" alt="AriataPanel Logo" width="260"/>

<h1>AriataPanel</h1>

<p>
سیستم متن‌باز استخراج، اعتبارسنجی، دسته‌بندی و انتشار خودکار کانفیگ‌های پروکسی از منابع عمومی
<b>Telegram</b> و <b>GitHub</b>
</p>

<p>
به‌روزرسانی خودکار، حذف کانفیگ‌های مرده، خروجی در فرمت‌های مختلف و انتشار آماده برای استفاده.
</p>

<p>
<a href="https://t.me/aristapanel">
<img src="https://img.shields.io/badge/Telegram-229ED9?style=for-the-badge&logo=telegram&logoColor=white">
</a>
<a href="https://arista-panel.arista-panel.workers.dev/">
<img src="https://img.shields.io/badge/Web%20Panel-F38020?style=for-the-badge&logo=cloudflare&logoColor=white">
</a>
<a href="https://youtube.com/@aristaproject-m3o?si">
<img src="https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white">
</a>
<a href="https://matrix.to/#/%23aristaproject:matrix.org">
<img src="https://img.shields.io/badge/Element-0DBD8B?style=for-the-badge&logo=element&logoColor=white">
</a>
<p align="center">
  <a href="https://t.me/AriataSub_Bot">
 <img src="https://img.shields.io/badge/Telegram_Bot-AriataSub-229ED9?style=for-the-badge&logo=telegram&logoColor=white">
  </a>
</p>
</p>

<p>

⚡ <b>به‌روزرسانی خودکار هر ۳ ساعت</b> •
🚀 <b>متن‌باز</b> •
💙 <b>رایگان</b>

</p>

</div>

---

## ✨ قابلیت‌های اصلی

- 📡 استخراج خودکار کانفیگ از **Telegram** و **GitHub**
- ✅ اعتبارسنجی ساختار کانفیگ‌ها قبل از انتشار
- 🩺 **TCP Health Check** برای حذف کانفیگ‌های مرده
- ⚡ پردازش همزمان با **AsyncIO** و سیستم کش هوشمند
- 🔄 حذف کانفیگ‌های تکراری و ترکیب خروجی منابع
- 📦 خروجی در فرمت‌های **TXT، JSON (Sing-box) و YAML (Clash Meta)**
- 🔢 تفکیک خودکار کانفیگ‌ها بر اساس پورت
- 🤖 به‌روزرسانی خودکار با **GitHub Actions**

---

## 🧩 معماری

| مؤلفه | وظیفه |
|-------|-------|
| 📡 **telegram_extractor.py** | استخراج کانفیگ از کانال‌های عمومی تلگرام |
| 🐙 **github_extractor.py** | استخراج کانفیگ از مخازن GitHub |
| 🔗 **combine_configs.py** | ادغام خروجی‌ها و حذف کانفیگ‌های تکراری |
| ⚙️ **GitHub Actions** | اجرای خودکار، Commit و انتشار خروجی |

---

## 🩺 TCP Health Check

کانفیگ‌ها پیش از انتشار، به‌صورت خودکار از نظر دسترسی شبکه بررسی می‌شوند.

**ویژگی‌ها:**

- 🔍 استخراج Host و Port از کانفیگ‌های قابل بررسی
- 📡 تست مستقیم اتصال TCP با IPv4
- ⚡ حداکثر ۲۰۰ اتصال همزمان
- 🔄 تشخیص وضعیت با ۳ شکست متوالی
- 💾 ذخیره و تداوم وضعیت سلامت بین اجراها
- 🛡️ حذف خودکار کانفیگ‌های Dead پس از تأیید خرابی
- ⚪ پروتکل‌های غیرقابل‌بررسی TCP به‌صورت Unchecked حفظ می‌شوند

**نتیجه:** کانفیگ‌های در دسترس و کانفیگ‌های Unchecked در چرخه انتشار باقی می‌مانند و کانفیگ‌های Dead حذف می‌شوند.

### پروتکل‌های پشتیبانی‌شده

- VMess
- VLESS
- Trojan
- Shadowsocks
- Hysteria
- Hysteria2
- TUIC
- WireGuard

---

## 📌 ویژگی‌های تکمیلی

- 🚦 مدیریت خودکار کانال‌های غیرفعال
- 🔍 اعتبارسنجی اختصاصی برای هر پروتکل
- 🧹 حذف خودکار کانفیگ‌های تکراری
- 📊 دسته‌بندی بر اساس منبع، پروتکل و پورت
- 🌐 پشتیبانی از IPv4 و IPv6
- ⚡ بهینه‌سازی شده برای سرعت و مصرف منابع

## 🔢 تفکیک کانفیگ‌ها بر اساس پورت

سیستم **تفکیک خودکار** کانفیگ‌ها بر اساس پورت‌های معروف و متداول.

### 🎯 پورت‌های پشتیبانی‌شده

| پورت | کاربرد |
|:---:|:---|
| **80** | HTTP |
| **443** | HTTPS / TLS |
| **8080** | HTTP Proxy |
| **8443** | HTTPS Proxy |
| **2096** | Cloudflare CDN |
| **2087** | Cloudflare CDN |
| **2053** | Cloudflare CDN |
| **8880** | HTTP Proxy |
| **2083** | Cloudflare CDN |
| **2086** | Cloudflare CDN |
| **2095** | Cloudflare CDN |
| **2052** | Cloudflare CDN |
| **9443** | HTTPS Proxy |

---

<div align="center">

# 🤖 AriataSub Bot

### دستیار هوشمند دریافت سابسکریپشن‌های AriataPanel

برای دسترسی سریع‌تر و حرفه‌ای‌تر به سرویس‌های **AriataPanel** از ربات تلگرام استفاده کنید.

🚀 دریافت سابسکریپشن اختصاصی  
📦 انتخاب فرمت‌های TXT • Sing-box • Clash Meta  
🔍 فیلتر بر اساس پروتکل، منبع و پورت  
⚙️ ساخت لینک‌های سفارشی  
🔄 دریافت آخرین خروجی‌های به‌روزرسانی‌شده

<br>

<a href="https://t.me/AriataSub_Bot">
    <img src="https://img.shields.io/badge/Open_AriataSub_Bot-229ED9?style=for-the-badge&logo=telegram&logoColor=white">
</a>

</div>

---

## 📥 لینک‌های دسترسی به کانفیگ‌ها

<details>
<summary>📱 <b>V2rayNG • Hiddify • NekoBox • ...</b></summary>

<br/>

| منبع | ۵۰ | ۱۰۰ | ۱۵۰ | ۲۰۰ | ۲۵۰ | ۳۰۰ | ۴۰۰ | ۵۰۰ | ALL |
|:-----|:---:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:---:|
| **تلگرام** | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/telegram/ALL/50.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/telegram/ALL/100.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/telegram/ALL/150.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/telegram/ALL/200.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/telegram/ALL/250.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/telegram/ALL/300.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/telegram/ALL/400.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/telegram/ALL/500.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/telegram/ALL/ALL.txt) |
| **گیت‌هاب** | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/github/ALL/50.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/github/ALL/100.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/github/ALL/150.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/github/ALL/200.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/github/ALL/250.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/github/ALL/300.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/github/ALL/400.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/github/ALL/500.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/github/ALL/ALL.txt) |
| **ترکیبی** | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/combined/ALL/50.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/combined/ALL/100.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/combined/ALL/150.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/combined/ALL/200.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/combined/ALL/250.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/combined/ALL/300.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/combined/ALL/400.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/combined/ALL/500.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/configs.txt/combined/ALL/ALL.txt) |

</details>

<details>
<summary>🔷 <b>SingBox</b></summary>

<br/>

| منبع | ۵۰ | ۱۰۰ | ۱۵۰ | ۲۰۰ | ۲۵۰ | ۳۰۰ | ۴۰۰ | ۵۰۰ | ALL |
|:-----|:---:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:---:|
| **تلگرام** | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/telegram/ALL/50.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/telegram/ALL/100.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/telegram/ALL/150.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/telegram/ALL/200.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/telegram/ALL/250.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/telegram/ALL/300.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/telegram/ALL/400.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/telegram/ALL/500.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/telegram/ALL/ALL.json) |
| **گیت‌هاب** | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/github/ALL/50.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/github/ALL/100.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/github/ALL/150.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/github/ALL/200.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/github/ALL/250.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/github/ALL/300.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/github/ALL/400.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/github/ALL/500.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/github/ALL/ALL.json) |
| **ترکیبی** | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/combined/ALL/50.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/combined/ALL/100.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/combined/ALL/150.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/combined/ALL/200.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/combined/ALL/250.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/combined/ALL/300.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/combined/ALL/400.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/combined/ALL/500.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.json/combined/ALL/ALL.json) |

</details>

<details>
<summary>🔶 <b>ClashMeta</b></summary>

<br/>

| منبع | ۵۰ | ۱۰۰ | ۱۵۰ | ۲۰۰ | ۲۵۰ | ۳۰۰ | ۴۰۰ | ۵۰۰ | ALL |
|:-----|:---:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:---:|
| **تلگرام** | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/telegram/ALL/50.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/telegram/ALL/100.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/telegram/ALL/150.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/telegram/ALL/200.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/telegram/ALL/250.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/telegram/ALL/300.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/telegram/ALL/400.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/telegram/ALL/500.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/telegram/ALL/ALL.yaml) |
| **گیت‌هاب** | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/github/ALL/50.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/github/ALL/100.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/github/ALL/150.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/github/ALL/200.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/github/ALL/250.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/github/ALL/300.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/github/ALL/400.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/github/ALL/500.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/github/ALL/ALL.yaml) |
| **ترکیبی** | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/combined/ALL/50.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/combined/ALL/100.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/combined/ALL/150.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/combined/ALL/200.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/combined/ALL/250.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/combined/ALL/300.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/combined/ALL/400.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/combined/ALL/500.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/config.yaml/combined/ALL/ALL.yaml) |

</details>

---

## 🔢 لینک‌های دسترسی به کانفیگ‌های تفکیک‌شده بر اساس پورت

<details>
<summary>📱 <b>کانفیگ‌های TXT</b></summary>

<br/>

| منبع | ۸۰ | ۴۴۳ | ۸۰۸۰ | ۸۴۴۳ | ۲۰۹۶ | ۲۰۸۷ | ۲۰۵۳ | ۸۸۸۰ | ۲۰۸۳ | ۲۰۸۶ | ۲۰۹۵ | ۲۰۵۲ | ۹۴۴۳ | سایر | ALL |
|:-----|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **تلگرام** | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/telegram/port_80.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/telegram/port_443.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/telegram/port_8080.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/telegram/port_8443.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/telegram/port_2096.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/telegram/port_2087.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/telegram/port_2053.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/telegram/port_8880.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/telegram/port_2083.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/telegram/port_2086.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/telegram/port_2095.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/telegram/port_2052.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/telegram/port_9443.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/telegram/other_ports.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/telegram/all_ports.txt) |
| **گیت‌هاب** | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/github/port_80.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/github/port_443.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/github/port_8080.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/github/port_8443.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/github/port_2096.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/github/port_2087.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/github/port_2053.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/github/port_8880.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/github/port_2083.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/github/port_2086.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/github/port_2095.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/github/port_2052.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/github/port_9443.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/github/other_ports.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/github/all_ports.txt) |
| **ترکیبی** | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/combined/port_80.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/combined/port_443.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/combined/port_8080.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/combined/port_8443.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/combined/port_2096.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/combined/port_2087.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/combined/port_2053.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/combined/port_8880.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/combined/port_2083.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/combined/port_2086.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/combined/port_2095.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/combined/port_2052.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/combined/port_9443.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/combined/other_ports.txt) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.txt/combined/all_ports.txt) |

</details>

<details>
<summary>🔷 <b>کانفیگ‌های JSON (SingBox)</b></summary>

<br/>

| منبع | ۸۰ | ۴۴۳ | ۸۰۸۰ | ۸۴۴۳ | ۲۰۹۶ | ۲۰۸۷ | ۲۰۵۳ | ۸۸۸۰ | ۲۰۸۳ | ۲۰۸۶ | ۲۰۹۵ | ۲۰۵۲ | ۹۴۴۳ | سایر | ALL |
|:-----|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **تلگرام** | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/telegram/port_80.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/telegram/port_443.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/telegram/port_8080.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/telegram/port_8443.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/telegram/port_2096.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/telegram/port_2087.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/telegram/port_2053.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/telegram/port_8880.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/telegram/port_2083.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/telegram/port_2086.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/telegram/port_2095.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/telegram/port_2052.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/telegram/port_9443.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/telegram/other_ports.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/telegram/all_ports.json) |
| **گیت‌هاب** | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/github/port_80.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/github/port_443.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/github/port_8080.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/github/port_8443.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/github/port_2096.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/github/port_2087.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/github/port_2053.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/github/port_8880.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/github/port_2083.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/github/port_2086.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/github/port_2095.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/github/port_2052.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/github/port_9443.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/github/other_ports.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/github/all_ports.json) |
| **ترکیبی** | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/combined/port_80.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/combined/port_443.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/combined/port_8080.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/combined/port_8443.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/combined/port_2096.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/combined/port_2087.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/combined/port_2053.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/combined/port_8880.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/combined/port_2083.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/combined/port_2086.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/combined/port_2095.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/combined/port_2052.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/combined/port_9443.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/combined/other_ports.json) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.json/combined/all_ports.json) |

</details>

<details>
<summary>🔶 <b>کانفیگ‌های YAML (ClashMeta)</b></summary>

<br/>

| منبع | ۸۰ | ۴۴۳ | ۸۰۸۰ | ۸۴۴۳ | ۲۰۹۶ | ۲۰۸۷ | ۲۰۵۳ | ۸۸۸۰ | ۲۰۸۳ | ۲۰۸۶ | ۲۰۹۵ | ۲۰۵۲ | ۹۴۴۳ | سایر | ALL |
|:-----|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **تلگرام** | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/telegram/port_80.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/telegram/port_443.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/telegram/port_8080.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/telegram/port_8443.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/telegram/port_2096.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/telegram/port_2087.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/telegram/port_2053.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/telegram/port_8880.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/telegram/port_2083.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/telegram/port_2086.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/telegram/port_2095.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/telegram/port_2052.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/telegram/port_9443.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/telegram/other_ports.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/telegram/all_ports.yaml) |
| **گیت‌هاب** | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/github/port_80.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/github/port_443.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/github/port_8080.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/github/port_8443.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/github/port_2096.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/github/port_2087.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/github/port_2053.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/github/port_8880.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/github/port_2083.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/github/port_2086.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/github/port_2095.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/github/port_2052.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/github/port_9443.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/github/other_ports.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/github/all_ports.yaml) |
| **ترکیبی** | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/combined/port_80.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/combined/port_443.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/combined/port_8080.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/combined/port_8443.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/combined/port_2096.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/combined/port_2087.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/combined/port_2053.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/combined/port_8880.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/combined/port_2083.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/combined/port_2086.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/combined/port_2095.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/combined/port_2052.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/combined/port_9443.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/combined/other_ports.yaml) | [📥](https://raw.githubusercontent.com/aristapanell-cell/AriataPanel/refs/heads/main/port.yaml/combined/all_ports.yaml) |

</details>

---

## 🌐 پنل‌ها

### 🌍 پنل عمومی

برای **شخصی‌سازی خروجی‌ها**، **فیلتر بر اساس پروتکل، پورت و منبع** و **دریافت سابسکریپشن‌های سفارشی** از پنل عمومی استفاده کنید.

<p align="center">
  <a href="https://arista-panel.arista-panel.workers.dev/">
    <img src="Arista/assets/images/panel.png" alt="AristaPanel Public Panel">
  </a>
</p>

---

### 🔐 پنل اختصاصی

برای ساخت **پنل اختصاصی شخصی بر بستر Cloudflare**، ابتدا فایل **`worker.js`** را از مخزن دریافت کنید. 
راهنمای کامل نصب، پیکربندی و استقرار پنل در آموزش‌های رسمی آریستا در کانال تلگرام و یوتیوب ارائه شده است.

<p align="center">
  <a href="https://t.me/aristapanel/1255">
    <img src="https://img.shields.io/badge/📖_Private_Panel_Setup_Guide-229ED9?style=for-the-badge&logo=telegram&logoColor=white" alt="Private Panel Setup Guide">
  </a>
</p>

---

## 📱 کلاینت‌های پشتیبانی‌شده

برای استفاده از خروجی‌های AriataPanel می‌توانید از کلاینت‌های زیر استفاده کنید:

| نام کلاینت | سیستم‌عامل | لینک دانلود |
|:-----------|:-----------|:-----------:|
| **V2rayNG** | Android | [📥](https://github.com/2dust/v2rayNG/releases) |
| **Hiddify** | Android • iOS • Windows • macOS • Linux | [📥](https://github.com/hiddify/hiddify-app/releases) |
| **NekoBox** | Android | [📥](https://github.com/MatsuriDayo/NekoBoxForAndroid/releases) |
| **SingBox** | Android • iOS • Windows • macOS • Linux | [📥](https://github.com/SagerNet/sing-box/releases) |
| **ClashMeta** | Android • iOS • Windows • macOS • Linux | [📥](https://github.com/MetaCubeX/Clash.Meta/releases) |
| **v2rayN** | Windows | [📥](https://github.com/2dust/v2rayN/releases) |
| **Nekoray** | Windows • macOS • Linux | [📥](https://github.com/MatsuriDayo/nekoray/releases) |
| **Streisand** | Windows • macOS • Linux | [📥](https://github.com/SagerNet/Streisand/releases) |
| **Shadowrocket** | iOS | [📥](https://apps.apple.com/app/shadowrocket/id932747118) |
| **FairVPN** | iOS • macOS | [📥](https://apps.apple.com/app/fairvpn/id1533888676) |
| **V2Box** | iOS | [📥](https://apps.apple.com/app/v2box-v2ray-client/id6446814690) |
| **FoXray** | iOS | [📥](https://apps.apple.com/app/foxray/id6448898396) |

---

<div align="center">

# 📡 بانک اطلاعات IPهای برتر

### ⚡ آخرین نتایج اسکن به‌صورت زنده در دسترس است

<br>

<a href="https://raw.githubusercontent.com/aristapanell-cell/ARISTA-MATRIX-PIPELINE/main/output/best_ips.txt">
    <img src="https://img.shields.io/badge/⚡_BEST_IPS-LIVE-00C853?style=for-the-badge&logo=github&logoColor=white&labelColor=111827" alt="BEST IPS">
</a>

<br><br>

⭐ **مشاهده لیست کامل IPهای رتبه‌بندی‌شده**  
🚀 **Score • TTFB • Protocol • CDN • Domain • Country • City • Provider**

</div>

---

<div align="center">

<table border="0" cellpadding="20" style="background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 20px; border: 2px solid #e94560; margin: 0 auto;">
  <tr>
    <td align="center" style="padding: 25px 40px;">
      <span style="font-size: 1.8em; color: #e94560;">❤️</span>
      <span style="font-size: 1.5em; color: #ffffff; font-weight: bold;"> ساخته شده توسط تیم آریستا </span>
      <span style="font-size: 1.8em; color: #e94560;">❤️</span>
      <br>
      <span style="font-size: 1.2em; color: #ffd700;">🇲‌🇲‌🇩‌</span>
    </td>
  </tr>
</table>

<br>

## ⭐ حمایت

اگر این پروژه برای شما مفید بود، لطفاً با ⭐ در GitHub از ما حمایت کنید.

</div>
