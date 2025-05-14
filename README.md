# 💰 Bandit.camp bot Setup Guide

Follow the steps below to get started.

---

## Prerequisites

#### The following have to be installed before running setup.bat

- `python3`
- `Google Chrome`

---

## ⚙️ Step 1 — Run the Setup Script

Double-click the `setup.bat` file.

This will:

- Set up your environment
- Download any necessary dependencies
- Create shortcuts for easy access

---

## 🧾 Step 2 — Configure Your Users

Open the generated `users.json` file in a text editor.

Here, you define your bandit.camp accounts.

Each user entry requires:

- `name` — a nickname for your reference
- `token` — the 'jwt' cookie found on bandit.camp in the inspector tools
- `cashout_limit` — the minimum gathered scrap for the script to stop

You can add **multiple users**, just separate them with a in the list comma.

### ✅ Example `users.json` file:

```json
[
  {
    "name": "Bob",
    "token": "eyJhbGciOi...your_token_here...",
    "cashout_limit": 3
  },
  {
    "name": "Mike",
    "token": "eyJhbGciOi...another_token...",
    "cashout_limit": 5
  }
]
```

### Additional arguments include:

- `collect_rain` — whether bot should automatically join rain **[true/false]**
- `autobet` — whether bot should automatically bet all your money until cashout limit has been reached **[true/false]**

🔒 `Important`: Keep this file private. Anyone with access to the tokens can use your bandit.camp accounts.

---

## 🚀 Step 3 — Run the Script

Once you've added your users,
run the script from the bandit.camp desktop shortcut created during setup.
