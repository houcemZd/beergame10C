# 🍺 Beer Game — Django Supply Chain Simulation

A full-stack implementation of the **MIT Beer Game** supply chain simulation,
built with Django + Django Channels (WebSockets) for real-time multiplayer.

---

## Features

| Feature | Details |
|---|---|
| **Single-player mode** | Control all 4 roles, simulate any number of weeks |
| **Multiplayer mode** | 4 players, each with an isolated role view via WebSockets |
| **2-week pipeline delays** | Both orders AND shipments are delayed — the core mechanic |
| **AI fallback** | Pipeline-aware base-stock policy fills in for any missing player |
| **Real-time updates** | Week advances automatically when all players submit |
| **Charts** | Inventory, orders, backlog, cost — powered by Chart.js |
| **Bullwhip Effect Index** | σ(orders) / σ(demand) ratio per player on results page |
| **Information hiding** | Each player sees ONLY their own inventory (multiplayer) |

---

## Project Structure

```
beer_game/
├── manage.py
├── requirements.txt
├── README.md
│
├── beer_game/               ← Django project config
│   ├── settings.py          ← Channels + Redis config
│   ├── urls.py
│   ├── asgi.py              ← ASGI entry point (required for WebSockets)
│   └── wsgi.py
│
└── game/                    ← Main app
    ├── models.py            ← GameSession, Player, PlayerSession, Pipeline models
    ├── services.py          ← Game engine: process_week(), AI policy, chart data
    ├── consumers.py         ← WebSocket consumer (real-time multiplayer brain)
    ├── views.py             ← HTTP views: home, lobby, join, play, dashboard
    ├── routing.py           ← WebSocket URL routing
    ├── urls.py              ← HTTP URL routing
    └── templates/game/
        ├── base.html        ← Dark design system (Space Mono + DM Sans)
        ├── home.html        ← Session list
        ├── new_game.html    ← Create game (single/multi toggle)
        ├── lobby.html       ← Host view: share invite links
        ├── join.html        ← Player joins with their name
        ├── play.html        ← Real-time multiplayer game screen
        ├── dashboard.html   ← Single-player game screen
        └── results.html     ← End-game KPIs + bullwhip analysis
```

---

## Installation & Setup

### 1. Clone / download the project

```bash
cd beer_game
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Redis

Redis is required for Django Channels' channel layer (real-time messaging).

**Option A — Docker (recommended):**
```bash
docker run -p 6379:6379 redis:alpine
```

**Option B — Local install:**
```bash
# Ubuntu/Debian
sudo apt install redis-server && redis-server

# Mac (Homebrew)
brew install redis && brew services start redis
```

**Option C — No Redis (local dev only):**
Change `settings.py` channel layer to in-memory:
```python
CHANNEL_LAYERS = {
    "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}
}
```
⚠️ InMemoryChannelLayer only works if all players are on the same server process.
   Do NOT use in production.

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Start the server

```bash
# Development (Daphne handles both HTTP + WebSocket)
pip install daphne
daphne beer_game.asgi:application

# OR use Django's built-in runserver (works with Channels in dev mode)
python manage.py runserver
```

Open: **http://127.0.0.1:8000**

---

## How to Play (Multiplayer)

1. Click **New Game** → choose **Multiplayer** mode
2. The **Lobby** page shows 4 unique invite links — one per role
3. Share each link with a player (or open all 4 in separate browser tabs for testing)
4. Each player enters their name on the **Join** page
5. Every player sees only their own inventory and pipeline
6. Each week: enter your order quantity → click **Submit Order**
7. The week advances **automatically** once all 4 players submit
8. After all weeks complete, the **Results** page shows:
   - Total cost per player
   - Bullwhip Effect Index per role
   - Full history charts

---

## Game Mechanics

### Supply Chain Structure
```
Customer → Retailer ⇄ Wholesaler ⇄ Distributor ⇄ Factory
```

### Delays
- **Order delay:** 2 weeks (your order takes 2 weeks to reach your upstream supplier)
- **Shipment delay:** 2 weeks (goods take 2 weeks to arrive after being shipped)

### Costs (per unit, per week)
- **Holding cost:** $0.50 (for each unit sitting in inventory)
- **Backlog cost:** $1.00 (for each unit of unfilled demand)

### Demand Pattern (classic MIT pattern)
- Weeks 1–4: 4 units/week (steady state)
- Week 5+: ~8 units/week (demand shock)
- Small ±1 random noise added for realism

### AI Policy
Players who don't submit an order get the AI base-stock policy:
```
order = max(0, target - inventory - in_transit + backlog)
target = 16 units
```
This is pipeline-aware (counts goods already in transit) to avoid
artificial bullwhip amplification from the AI itself.

---

## WebSocket Message Protocol

### Client → Server
```json
{ "type": "submit_order", "quantity": 8 }
{ "type": "set_name",     "name": "Alice" }
```

### Server → Client
```json
{ "type": "state_update",   "role": "retailer", "week": 5, "own": {...}, "pipeline": [...], "history": [...] }
{ "type": "ready_status",   "submitted": ["retailer", "wholesaler"], "connected": [...], "total": 4 }
{ "type": "player_joined",  "role": "wholesaler", "name": "Bob" }
{ "type": "player_left",    "role": "wholesaler", "name": "Bob" }
{ "type": "game_over",      "results_url": "/game/1/results/" }
{ "type": "error",          "message": "Order must be between 0 and 200" }
```

---

## Bullwhip Effect

The Bullwhip Effect Index measures how much each role **amplifies** demand variability:

```
BWE = σ(orders placed by role) / σ(customer demand)
```

| Score | Interpretation |
|---|---|
| ~1.0 | Perfect — no amplification |
| 1.5–3.0 | Typical — mild bullwhip |
| 3.0–6.0 | Severe bullwhip effect |
| >6.0 | Extreme panic ordering |

In a well-run game, the Factory typically has the highest BWE score —
demonstrating how information asymmetry causes amplification up the chain.

---

## Deployment (Production)

For a demo on a server:

```bash
pip install daphne
daphne -b 0.0.0.0 -p 8000 beer_game.asgi:application
```

Make sure Redis is running and accessible. Update `settings.py`:
```python
SECRET_KEY = 'your-real-secret-key'
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [("127.0.0.1", 6379)]},
    }
}
```

Free hosting options:
- **Railway.app** — supports Redis + WebSockets natively
- **Render.com** — add a Redis service alongside the web service
- **Fly.io** — Docker-based, full WebSocket support

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend framework | Django 4.2+ |
| Real-time / WebSockets | Django Channels 4.0+ |
| Channel layer / pub-sub | Redis via channels-redis |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Frontend charts | Chart.js 4.4 |
| Fonts | Space Mono + DM Sans (Google Fonts) |
| Deployment server | Daphne (ASGI) |

---

## Academic Context

This project implements the supply chain simulation originally developed at MIT's
Sloan School of Management. The Beer Game is used to demonstrate:

- The **Bullwhip Effect** — demand variability amplification upstream
- The cost of **information asymmetry** in supply chains
- The benefit of **pipeline-aware ordering policies**
- How **delays** create instability even with rational actors
