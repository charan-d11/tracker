# 🪣 Shared Pot Tracker

A simple web app for people who live together to manage a shared pool of money and log everyday purchases. Each account gets its own private pot, so anyone can sign up and use it with their own group.

It is installable as a PWA, so it can be added to a phone's home screen and opened like an app.

## Features

- **Accounts:** register, log in and log out (passwords are stored hashed)
- **Your own group:** choose how many people share the pot and enter their names
- **Add money** to the pot and see the **current balance**
- **Log purchases** with an item name, amount and who bought it
- **Purchase history** with date and time
- **Reset balance** and **clear history**
- **Private data:** every account only sees its own pot, members and purchases
- **PWA:** installable on Android, iOS and desktop

## Tech stack

- Python 3 and Flask
- PostgreSQL (via `psycopg2`)
- Plain HTML, CSS and JavaScript
- Gunicorn for production

## Project structure

```
Tracker/
├── requirements.txt
├── Procfile
├── .gitignore
└── app/
    ├── run.py            # Flask app: routes, login, API
    ├── database.py       # PostgreSQL tables and queries
    ├── templates/
    │   ├── index.html    # Main tracker page
    │   ├── login.html
    │   ├── register.html
    │   └── setup.html    # Choose people in the group
    └── static/
        ├── style.css
        ├── manifest.json # PWA manifest
        ├── sw.js         # Service worker
        ├── pwa.js        # Registers the service worker
        ├── offline.html
        └── icons/
```

## Run locally

**1. Requirements:** Python 3 and a PostgreSQL database (for example, one created in pgAdmin).

**2. Install dependencies**

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

**3. Create a `.env` file** in the project root:

```dotenv
DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@localhost:5432/tracker"
SECRET_KEY="a-long-random-string"
```

**4. Start the app**

```bash
python app/run.py
```

Open http://localhost:5000, create an account and choose the people in your group. The tables are created automatically on first start.

## Environment variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string. The app will not start without it. |
| `SECRET_KEY` | Long random string used to sign login sessions. The app will not start without it. |
| `PORT` | Optional. Port to listen on (hosting platforms usually set this). |

Never commit your `.env` file. It is listed in `.gitignore`.

## Deploy (Render)

1. Create a **PostgreSQL** database on Render and copy its **Internal Database URL**.
2. Create a **Web Service** from this GitHub repository (same region as the database).
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn --chdir app run:app`
3. In the service's **Environment** tab, add `DATABASE_URL` (the internal URL) and `SECRET_KEY`.
4. Deploy, then open `/login` on your service URL.

The same setup works on other hosts such as Railway: add a Postgres database, set the two environment variables, and use the same start command.

> Free tiers may put the app to sleep after inactivity, and free databases can expire. Check your host's current limits.

## Install as an app (PWA)

- **Android (Chrome):** menu → *Install app*
- **iPhone (Safari):** Share → *Add to Home Screen*
- **Desktop (Chrome/Edge):** click the install icon in the address bar

The service worker only caches static files. Pages and data are never cached, so one person's pot can't show up for another user on a shared device.

## API overview

All routes require login and only touch the logged-in user's data.

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/members` | List people in the group |
| GET | `/api/balance` | Current balance |
| POST | `/api/add_money` | Add money to the pot |
| POST | `/api/add_purchase` | Log a purchase (deducts from the pot) |
| GET | `/api/purchases` | Purchase history |
| DELETE | `/api/clear_history` | Clear history |
| PUT | `/api/reset_balance` | Reset balance to 0 |

## Notes

- A purchase is rejected if the pot doesn't have enough money.
- Item names are escaped before display, so they can't inject HTML.

## Author:
**DURGA CH. MALLICK.**
