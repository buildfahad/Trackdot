from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
import requests
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required


app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///tracker.db")
headers = {"Authorization": "YOUR HENRIK'S API HERE"}


@app.route('/', methods=['GET'])
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if "user_id" in session:
            flash('You are already logged in.')
            return redirect('/')
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Validate input and handle login logic here
        if not username or not password:
            flash('Please enter both username and password.')
            return render_template('login.html')
        if len(username) < 3:
            flash('Username must be at least 3 characters long.')
            return render_template('login.html')
        if len(password) < 8:
            flash('Password must be at least 8 characters long.')
            return render_template('login.html')
        if not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
            flash('Password must contain both letters and numbers.')
            return render_template('login.html')
        
        # Fetch user from database and verify password
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        user = rows[0] if rows else None
        if not user or not check_password_hash(user["hash"], password):
            flash('Invalid username or password.')
            return render_template('login.html')
        # Log the user in (e.g., set session variables)
        session["user_id"] = user["id"]
        flash('Login successful!')
        return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        if "user_id" in session:
            flash('You are already logged in.')
            return redirect('/')
        return render_template('register.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input and handle registration logic here
        if not username or not password or not confirm_password:
            flash('Please fill in all fields.')
            return render_template('register.html')
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long.')
            return render_template('register.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long.')
            return render_template('register.html')
        if not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
            flash('Password must contain both letters and numbers.')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.')
            return render_template('register.html')
        
        # Registration logic (e.g., save user to database) goes here
        hash_val = generate_password_hash(password)
        # Save username and hash to database
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_val)
        flash('Registration successful! Please log in.')
        return redirect('/login')
        
@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')
@app.route('/leaderboard', methods=['GET', 'POST'])
@login_required
def leaderboard():
    region = request.values.get("region", "eu")
    # Ensure cache schema includes all fields used by the template
    try:
        db.execute("ALTER TABLE leaderboard_cache ADD COLUMN rankImg TEXT")
    except Exception:
        pass
    try:
        db.execute("ALTER TABLE leaderboard_cache ADD COLUMN wins INTEGER DEFAULT 0")
    except Exception:
        pass
    try:
        db.execute("ALTER TABLE leaderboard_cache ADD COLUMN rating INTEGER DEFAULT 0")
    except Exception:
        pass
    try:
        db.execute("ALTER TABLE leaderboard_cache ADD COLUMN tag TEXT DEFAULT ''")
    except Exception:
        pass
    try:
        db.execute("ALTER TABLE leaderboard_cache ADD COLUMN position INTEGER DEFAULT 9999")
    except Exception:
        pass
    # Remove malformed cached rows that have no usable player id
    db.execute("DELETE FROM leaderboard_cache WHERE TRIM(COALESCE(gameName, '')) = '' AND TRIM(COALESCE(tag, '')) = ''")
    # Remove stale cached rows older than 1 day to keep the table small
    db.execute("DELETE FROM leaderboard_cache WHERE timestamp < datetime('now', '-1 day')")
    players = db.execute(
        "SELECT id, cardImage, gameName, tag, level, rankName, region, timestamp, rankImg, wins, rating AS rankedRating, position FROM leaderboard_cache WHERE region = ? AND timestamp >= datetime('now', '-1 day') ORDER BY timestamp DESC, position ASC, id ASC",
        region
    )
    if players:
        return render_template('leaderboard.html', players=players, region=region)
    response = requests.get(f"https://api.henrikdev.xyz/valorant/v3/leaderboard/{region}/pc", headers=headers)
    if response.status_code == 200:
        data = response.json()
        players = data.get("data", {}).get("players", [])
        players = players[:10]
        ranks = requests.get("https://valorant-api.com/v1/competitivetiers").json()
        tier_rows = ranks["data"][-1]["tiers"]
        for player in players:
            tier_index = player.get("tier")
            tier_info = tier_rows[tier_index] if tier_index is not None and tier_index < len(tier_rows) else {}
            
            
            player["gameName"] = player.get("name") or player.get("gameName") or ""
            player["tag"] = player.get("tag") or player.get("tagLine") or ""
            player["numberOfWins"] = player.get("wins", 0)
            player["rankedRating"] = player.get("rr", 0)
            player["CompetitiveTier"] = tier_index
            player["rankName"] = tier_info.get("tierName", "") or tier_info.get("divisionName", "")
            player["tierName"] = tier_info.get("tierName", "") or tier_info.get("divisionName", "")
            player["rankImg"] = tier_info.get("largeIcon", "") or tier_info.get("smallIcon", "")
            card_id = player.get("card")

            if card_id:
                card_response = requests.get(f"https://valorant-api.com/v1/playercards/{card_id}")
                if card_response.status_code == 200:
                    card_data = card_response.json().get("data", {})
                    player["cardImage"] = card_data.get("wideArt") or card_data.get("largeArt") or card_data.get("displayIcon", "")
                else:
                    player["cardImage"] = ""
            else:
                player["cardImage"] = ""
       
        from datetime import datetime
        ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        for index, player in enumerate(players, start=1):
            rank_img = player.get("rankImg", "")
            try:
                db.execute('''
                    INSERT OR REPLACE INTO leaderboard_cache 
                    (cardImage, gameName, tag, level, rankName, region, timestamp, rankImg, wins, rating, position)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                    player.get("cardImage", ""),
                    player.get("gameName", ""),
                    player.get("tag", "") or player.get("tagLine", ""),
                    player.get("accountLevel", 0),
                    player.get("rankName", ""),
                    region,
                    ts,
                    rank_img,
                    player.get("wins", player.get("numberOfWins", 0)),
                    player.get("rr", player.get("rankedRating", 0)),
                    index
                )
            except Exception:
                try:
                    db.execute("ALTER TABLE leaderboard_cache ADD COLUMN rankImg TEXT")
                except Exception:
                    pass
                try:
                    db.execute("ALTER TABLE leaderboard_cache ADD COLUMN wins INTEGER DEFAULT 0")
                except Exception:
                    pass
                try:
                    db.execute("ALTER TABLE leaderboard_cache ADD COLUMN rating INTEGER DEFAULT 0")
                except Exception:
                    pass
                try:
                    db.execute("ALTER TABLE leaderboard_cache ADD COLUMN tag TEXT DEFAULT ''")
                except Exception:
                    pass
                try:
                    db.execute("ALTER TABLE leaderboard_cache ADD COLUMN position INTEGER DEFAULT 9999")
                except Exception:
                    pass
                db.execute('''
                    INSERT OR REPLACE INTO leaderboard_cache 
                    (cardImage, gameName, tag, level, rankName, region, timestamp, rankImg, wins, rating, position)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                    player.get("cardImage", ""),
                    player.get("gameName", ""),
                    player.get("tag", "") or player.get("tagLine", ""),
                    player.get("accountLevel", 0),
                    player.get("rankName", ""),
                    region,
                    ts,
                    rank_img,
                    player.get("wins", player.get("numberOfWins", 0)),
                    player.get("rr", player.get("rankedRating", 0)),
                    index
                )
        return render_template('leaderboard.html', players=players, region=region)
    return redirect('/leaderboard')

@app.route('/player', methods=['GET'])
@login_required
def player():
    if not request.args.get('idtag'):
        flash('Please enter your ID tag.')
        return redirect('/')
    idtag = request.args.get('idtag')
    if not idtag or '#' not in idtag:
        flash('Invalid ID tag format. Please use the format "Name#Tag".')
        return redirect('/')
    
    session["idtag"] = idtag
    id, tag = idtag.split('#')

    response = requests.get(f"https://api.henrikdev.xyz/valorant/v1/account/{id}/{tag}", headers=headers)
    if response.status_code == 200:
        data = response.json()
        player_info = data.get("data", {})
        puuid = player_info.get("puuid", "")
        rank_rows = db.execute(
            "SELECT rankName, rankImg FROM leaderboard_cache WHERE gameName = ? AND tag = ? ORDER BY timestamp DESC LIMIT 1",
            id, tag
        )
        if rank_rows:
            player_info["rankName"] = rank_rows[0].get("rankName", "")
            player_info["rankImg"] = rank_rows[0].get("rankImg", "")
        matches = recent_matches(id, tag, player_info.get("region", "eu"), puuid)
        if matches is None:
            matches = []
            flash('Could not retrieve matches for this player.')
            return render_template('player.html', player=player_info, matches=matches)
        return render_template('player.html', player=player_info, matches=matches)
    flash('Player not found.')
    return render_template('index.html')

def recent_matches(id, tag, region, puuid=""):
    response = requests.get(f"https://api.henrikdev.xyz/valorant/v3/matches/{region}/{id}/{tag}", headers=headers)
    if response.status_code != 200:
        return []

    def clean(value):
        return str(value or "").strip().lower()

    matches = []
    for match in response.json().get("data", [])[:10]:
        metadata = match.get("metadata", {})
        mode = clean(metadata.get("mode"))
        players = match.get("players", {}).get("all_players", [])
        player = next(
            (
                p for p in players
                if (puuid and clean(p.get("puuid")) == clean(puuid))
                or (clean(p.get("game_name") or p.get("name")) == clean(id)
                and clean(p.get("tag_line") or p.get("tag")) == clean(tag))
            ),
            players[0] if players else {}
        )

        result = "Unknown"
        if mode == "deathmatch":
            score = player.get("stats", {}).get("score", 0)
            top_score = max((p.get("stats", {}).get("score", 0) for p in players), default=0)
            result = "Win" if score >= top_score else "Loss"
        else:
            team_name = clean(player.get("team") or player.get("team_id") or "")
            team = match.get("teams", {}).get(team_name, {})
            if team:
                result = "Win" if team.get("has_won") else "Loss"
            elif player.get("won") is True or player.get("win") is True:
                result = "Win"
            elif player.get("won") is False or player.get("win") is False:
                result = "Loss"

        stats = player.get("stats", {}) if isinstance(player, dict) else {}
        kda = f"{stats.get('kills', player.get('kills', 0))}/{stats.get('deaths', player.get('deaths', 0))}/{stats.get('assists', player.get('assists', 0))}"

        matches.append({
            "map": metadata.get("map"),
            "mode": metadata.get("mode"),
            "agent": player.get("character") or player.get("agent") or player.get("character_name", ""),
            "result": result,
            "kda": kda,
            "game_start_patched": metadata.get("game_start_patched"),
        })

    return matches


@app.context_processor
def inject_user():
    if "user_id" in session:
        row = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
        if row:
            return {"username": row[0]["username"]}
    return {"username": None}       

if __name__ == '__main__':
    app.run(debug=True)


#scraped functions

"""@app.route('/pp', methods=['GET'])
@login_required
def pp():
    full = request.args.get('idtag')
    id, tag = full.split('#')

    response = requests.get(f"{url}riot/account/v1/accounts/by-riot-id/{id}/{tag}", headers=riotheader)
    if response.status_code == 200:
        player_info = response.json()
        return render_template('player.html', player=player_info)
    flash('Player not found.')
    return render_template('index.html')"""


#was trying to implement the official riot api but realized I could cache the henrik data to not waste time and avoid rate limit.
"""@app.route('/leaderboard', methods=['GET'])
@login_required
def leaderboard():
    region = request.args.get('region', 'eu')
    act_id = "ce2783e8-44fc-dd48-3da3-33b5ba6c4a22"
    response = requests.get(f"https://{url}riot/val/ranked/v1/leaderboards/by-act/{act_id}/pc/{region}", headers=riotheader)
    if response.status_code == 200:
        data = response.json()
        players = data.get("players", [])[:10]
        return render_template('leaderboard.html', players=players, region=region.upper())"""
