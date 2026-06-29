# 🛡️ Farzand Nazorati — Telegram Bot

O'zbekistondagi ota-onalarga 7–16 yoshli farzandlarining internet xavfsizligini nazorat qilish imkonini beruvchi Telegram bot.

## ✨ Funksiyalar

- 👨‍👩‍👧 **Rol tanlash** — Ota-ona yoki farzand sifatida ro'yxatdan o'tish
- 🔗 **Farzand ulash** — 6 raqamli kod orqali ota-ona va farzandni bog'lash
- 📊 **Kunlik hisobot** — Ekran vaqti, ogohlantirishlar, test natijalari
- 🔍 **Kontent tekshirish** — Skrinshot yuborib AI tahlil qilish
- ⚠️ **Xavfli so'zlar filtri** — 5 kategoriya bo'yicha real-time monitoring
- 📝 **Qaramlik testi** — 8 savollik test
- 💡 **Kunlik maslahatlar** — Har kuni ertalab xavfsizlik maslahati
- 📚 **O'quv materiallar** — Farzandlar uchun xavfsizlik darsliklari

## 🚀 Ishga tushirish

### 1. Repozitoriyani klonlash

```bash
git clone https://github.com/username/farzand-nazorat.git
cd farzand-nazorat
```

### 2. Virtual muhit yaratish

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

### 4. .env faylini sozlash

```bash
cp .env.example .env
```

`.env` faylini tahrirlang:
```env
BOT_TOKEN=your_telegram_bot_token    # @BotFather dan oling
OPENAI_API_KEY=your_openai_key       # Ixtiyoriy (kontent tahlili uchun)
ADMIN_IDS=123456789                  # Admin Telegram ID
```

### 5. Botni ishga tushirish

```bash
python -m bot.main
```

### Docker bilan

```bash
docker build -t farzand-nazorat .
docker run -d --env-file .env farzand-nazorat
```

## 📁 Loyiha tuzilmasi

```
farzand_nazorat/
├── bot/
│   ├── main.py                  # Asosiy ishga tushirish
│   ├── config.py                # Sozlamalar
│   ├── handlers/
│   │   ├── parent/              # Ota-ona komandlari
│   │   │   ├── start.py         # /start, rol tanlash
│   │   │   ├── link_child.py    # /link — farzand ulash
│   │   │   ├── reports.py       # /report — hisobot
│   │   │   └── content_check.py # /check — kontent tekshirish
│   │   └── child/               # Farzand komandlari
│   │       ├── start.py         # Darsliklar, statistika
│   │       ├── connect.py       # /connect — ulanish
│   │       └── tests.py         # /test — qaramlik testi
│   ├── middlewares/
│   │   ├── activity_tracker.py  # Ekran vaqti kuzatish
│   │   └── keyword_filter.py    # Xavfli so'zlar filtri
│   ├── services/
│   │   ├── ai_analyzer.py       # GPT-4o kontent tahlil
│   │   ├── scheduler.py         # Kunlik hisobot/maslahat
│   │   ├── notifier.py          # Xabar yuborish
│   │   └── report_generator.py  # Hisobot yaratish
│   └── keyboards/
│       ├── parent_kb.py         # Ota-ona klaviaturalari
│       └── child_kb.py          # Farzand klaviaturalari
├── database/
│   ├── models.py                # SQLAlchemy modellari
│   └── crud.py                  # Database operatsiyalar
├── .env.example
├── requirements.txt
├── Dockerfile
└── README.md
```

## 🤖 Bot komandalar

### Ota-ona uchun
| Buyruq | Tavsif |
|--------|--------|
| `/start` | Botni ishga tushirish |
| `/link` | Farzand ulash kodi |
| `/report` | Kunlik hisobot |
| `/check` | Kontent tekshirish |
| `/tips` | Bugungi maslahat |
| `/help` | Yordam |

### Farzand uchun
| Buyruq | Tavsif |
|--------|--------|
| `/start` | Botni ishga tushirish |
| `/connect` | Ota-onaga ulanish |
| `/test` | Qaramlik testi |
| `/help` | Yordam |

## 🔧 Texnologiyalar

- **aiogram 3.x** — Async Telegram bot framework
- **SQLite + SQLAlchemy** — Ma'lumotlar bazasi
- **APScheduler** — Rejalashtirilgan vazifalar
- **OpenAI GPT-4o** — Kontent tahlili (ixtiyoriy)

## 📄 Litsenziya

MIT License
