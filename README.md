# Trackdot 🎯

A Valorant stat tracker web app built with Python and Flask. Search any player by their Riot ID, view their profile, recent match history, and browse top-ranked players across EU, NA, and APAC leaderboards.

**[▶ Watch Demo](https://youtu.be/uoPrd7w4RK4)**

---

## Features

- **Player Lookup** — search any Valorant account by Riot ID (e.g. `PlayerName#TAG`) and view their rank, level, region, and player card
- **Match History** — see the 10 most recent matches with map, game mode, agent played, KDA, result (Win/Loss), and match date
- **Leaderboards** — browse top 10 ranked players from EU, NA, and APAC with rank icons, win counts, and rated points
- **Smart Caching** — leaderboard data is cached in SQLite for 24 hours so repeat visits load instantly without burning API quota
- **User Accounts** — register, log in, and log out with hashed passwords and session management
- **Win/Loss Styling** — match cards are color-coded green or red based on match result

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | SQLite (via cs50 SQL) |
| Frontend | HTML, CSS, Bootstrap, Jinja2 |
| Auth | Werkzeug password hashing, Flask-Session |
| Data | Henrik's Valorant API, valorant-api.com |
| Language | JavaScript (typewriter effect) |

---

## How It Works

```
User searches "PlayerName#TAG"
        ↓
Flask sends GET to Henrik's API → fetches account info + PUUID
        ↓
Second API call fetches 10 recent matches → parsed per-player
        ↓
Rank info pulled from valorant-api.com competitive tiers
        ↓
Everything rendered via Jinja2 templates
```

Leaderboard requests check the SQLite cache first. If cached data is less than 24 hours old it's served immediately. Otherwise a fresh API call is made, parsed, and stored before rendering.

---

## Getting Started

**Prerequisites:** Python 3.10+, pip

**1. Clone the repo**
```bash
git clone https://github.com/buildfahad/Trackdot.git
cd Trackdot
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add your API key**

Open `app.py` and replace the placeholder with your [Henrik's API](https://docs.henrikdev.xyz/) key:
```python
headers = {"Authorization": "YOUR_API_KEY_HERE"}
```

**4. Run the app**
```bash
flask run
```

Visit `http://localhost:5000` in your browser. Register an account and start searching players.

---

## Project Structure

```
Trackdot/
├── app.py              # Flask routes and application logic
├── helpers.py          # login_required decorator
├── tracker.db          # SQLite database (users + leaderboard cache)
├── requirements.txt
├── static/             # CSS, JS, images
└── templates/          # Jinja2 HTML templates
    ├── index.html
    ├── player.html
    ├── leaderboard.html
    ├── login.html
    └── register.html
```

---

## Design Decisions

**Caching leaderboard data** — fetching 10 players from the leaderboard requires multiple API calls per player (rank icons, card art). Without caching, each page load took several seconds. Storing results in SQLite and reusing them for 24 hours makes subsequent loads near-instant.

**Henrik's API over official Riot API** — the official Riot API restricts match data access significantly for personal projects. Henrik's API aggregates the same data with a much more practical developer experience.

**Context processor for username** — Flask's `render_template` only passes data to the template it's called with. Using `@app.context_processor` injects the logged-in username into every template globally, removing repetitive code from every route.

---

## Known Limitations

- Not deployed yet (runs locally)
- Rank info for players not on the leaderboard relies on match data as a fallback
- API key is hardcoded (should move to `.env`)

---

## Built By

Fahad — CS50 Final Project  
Self-taught developer learning backend engineering via [Boot.dev](https://boot.dev)
