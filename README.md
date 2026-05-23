# 💸 FinFlow — Personal Finance Tracker

A mobile-first expense tracking app with a dark premium UI, multi-user support, rich analytics, and Google Sheets as a live database. No traditional backend — just a spreadsheet and Python.

---

## Features

### 🏠 Home Dashboard

- **Net Worth Hero Card** — total balance across all wallets, month's income, spending, and net savings at a glance
- **Month-End Forecast** — projects your spend to end of month based on current daily burn rate, with on-track / over-pace status
- **Burn Rate vs Required Spend Rate** — shows what you're averaging per day and what you need to average to stay within budget for the rest of the month
- **KPI Grid** — Month Spend, Month Income, This Week, and Today, with delta indicators vs the previous period
- **7-Day Sparkline** — area chart of daily expenses for the last 7 days
- **Streak Counter 🔥** — counts consecutive days you stayed under your daily budget target
- **Recurring Due Today** — surfaces any scheduled transactions due today with a one-tap Pay button that auto-advances the next due date
- **Quick Add Shortcuts** — 6 configurable one-tap expense buttons (Coffee ☕, Cab 🚕, Lunch 🍔, etc.) that instantly log and debit your default wallet
- **Budget Progress** — overall and per-category budget bars, color-coded green/amber/red, with a toggle between Monthly and Weekly view
- **Recent Transactions** — last 5 entries with type badges

### 💳 Wallets

- Multiple wallet types: Cash, UPI, Card, Bank
- **Savings Goals 🎯** — a special wallet type with a target amount and a progress bar; triggers a celebration when the goal is hit
- Set a **Default Wallet** that persists across sessions (used by Quick Add)
- Manual balance adjustment with a reason field — auto-logs a correction entry so the ledger stays accurate

### 📒 History

- Full transaction log with filters for type (Expense / Income / Transfer), period, and wallet
- Full-text search across title, category, notes, and amount
- Inline edit for title, amount, and notes — wallet balance is adjusted automatically on edits and deletes
- Delete with wallet balance reversal
- Export to CSV

### 📈 Insights & Analytics

Selectable periods — Today, This Week, This Month, Last Month, or a Custom date range.

- **Category Donut Chart** — spending split by category
- **Savings Rate Gauge** — percentage of income saved, with color-coded zones
- **Daily Spend Chart** — stacked bar chart by category
- **Week-on-Week (last 6 weeks)** — grouped bars to spot weekly trends
- **Month-on-Month (last 5 months)** — stacked bars for the bigger picture
- **Income vs Expense Trend** — line chart across months
- **Top 5 Transactions** — biggest expenses in the selected period
- KPI summary — total spent, top category, avg/day, transaction count
- Download CSV for any selected range

### 👤 Profile & Settings

- Edit display name and password
- Change default wallet
- Manage categories — edit name, monthly budget limit, icon; add or delete
- Manage wallets — rename, change type, delete
- Manage recurring templates — view and remove scheduled transactions
- Customize Quick Shortcuts — change icon, label, amount, and category for each slot
- **Delete Old Data** — permanently purge transactions older than 1 year, requires password confirmation

---

## Data & Storage

All data lives in a Google Spreadsheet named `ExpenseTrackerDB` with five sheets:

| Sheet | What it stores |
|---|---|
| `Users` | User accounts, hashed passwords, default wallet preference, last login |
| `Wallets` | Wallet name, type, current balance, goal target (encoded in name as `Name\|Target`) |
| `Expenses` | Every transaction — date, time, type, category, title, notes, amount, wallet, tags |
| `ExpenseCategories` | Category name, emoji icon, monthly budget limit, per-user or global |
| `RecurringTemplates` | Scheduled transaction templates with frequency, next due date, last paid date |

Data is fetched in a single batch API call and cached for 5 minutes. Any write (add, edit, delete, transfer) immediately invalidates the cache and triggers a refresh so the UI stays consistent. The main data load is scoped to the last 60 days for speed; the Insights page fetches the full range when a custom period is selected.

---

## Setup

Install dependencies, drop your Google service account credentials into `.streamlit/secrets.toml` in the standard TOML format, share the `ExpenseTrackerDB` spreadsheet with the service account email, and run with `streamlit run app.py`.

```toml
# .streamlit/secrets.toml
[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "..."
client_email = "..."
...
```

For Streamlit Cloud deployment, paste the same block into the Secrets section of your app settings.

---

## Stack

Streamlit · Plotly · gspread · Google Sheets API · Python 3.9+

---

## License

MIT — free to use and modify.
