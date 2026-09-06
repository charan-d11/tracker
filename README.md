# 🪣 Shared Pot Tracker

A simple web app to track shared expenses between roommates. Add money to a shared pot, log purchases, and always know how much is left — from anywhere, on any device.

---

## 📱 Live Demo

Deployed on Railway — accessible from mobile browser and installable as a PWA.

---

## ✨ Features

- 💰 Add money to the shared pot
- 🛒 Log purchases and auto-subtract from the balance
- 📋 View full purchase history
- 🗑️ Clear purchase history
- 🔄 Reset balance to zero
- 📱 PWA support — install on your phone like a real app
- 🖥️ Sidebar for adding money (like Claude's UI)

---

## 🗂️ Project Structure

```
Tracker/
  app/
    static/
      style.css          # Styling
      manifest.json      # PWA manifest
      sw.js              # Service Worker
    templates/
      index.html         # Frontend
    database.py          # SQLite3 logic
    run.py               # Flask app
  requirements.txt       # Python dependencies
  Procfile               # Railway deployment config
  tracker.db             # SQLite database (auto-created)
```

---

## 🛠️ Tech Stack

| Layer     | Technology        |
|-----------|-------------------|
| Backend   | Python + Flask    |
| Database  | SQLite3           |
| Frontend  | HTML + CSS + JS   |
| Hosting   | Railway           |
| Mobile    | PWA               |

---

## 🚀 Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/charan-d11/tracker.git
cd tracker
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the app**
```bash
cd app
python run.py
```

**4. Open in browser**
```
http://127.0.0.1:5000
```

---

## 🌐 Deploy on Railway

1. Push your code to GitHub
2. Go to [railway.app](https://railway.app) and create a new project
3. Connect your GitHub repo
4. In Settings → Build, add build command:
   ```
   pip install -r requirements.txt
   ```
5. In Settings → Deploy, add start command:
   ```
   gunicorn --chdir app run:app
   ```
6. Generate a domain and share the URL!

---

## 📲 Install as Mobile App (PWA)

1. Open the live URL in **Chrome** on your phone
2. Tap the **3 dots menu**
3. Tap **"Add to Home Screen"**
4. Done — works like a native app! 🎉

---

## 🔌 API Endpoints

| Method   | Endpoint               | Description              |
|----------|------------------------|--------------------------|
| GET      | `/`                    | Load the main page       |
| GET      | `/api/balance`         | Get current pot balance  |
| POST     | `/api/add_money`       | Add money to the pot     |
| POST     | `/api/add_purchase`    | Log a purchase           |
| GET      | `/api/purchases`       | Get purchase history     |
| DELETE   | `/api/clear_history`   | Clear all history        |
| PUT      | `/api/reset_balance`   | Reset balance to zero    |

---

## 👨‍💻 Built By

**Durga Charan** — built with 🐍 Python and a lot of debugging! 😄
