import subprocess
import time
import os
from datetime import datetime
from tidalapi import Session, media
from pathlib import Path
import yaml

# === CONFIG ===

with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

STREAM_URL = config["stream_url"]
INVALID_TITLES = set(config["invalid_titles"])
PLAYLIST_NAME = f'{config["playlist_prefix"]} {datetime.now().strftime("%d.%m.%Y")}'
LOG_PATH = os.path.expanduser(config["log_path"])
FFPROBE_PATH = config.get("ffprobe_path", "ffprobe")

# === TIDAL LOGIN ===
TOKEN_PATH = Path("./tidal_session.pkl")

session = Session()

if TOKEN_PATH.exists():
    session.load_session_from_file(TOKEN_PATH)
    if session.check_login():
        print("✅ Restored previous session.")
    else:
        print("❌ Session expired. Logging in again...")
        session.login_oauth_simple()
        session.save_session_to_file(TOKEN_PATH)
else:
    session.login_oauth_simple()
    session.save_session_to_file(TOKEN_PATH)

print(f"🎧 Logged in as user ID: {session.user.id}")

# === GET OR CREATE PLAYLIST ===
existing = [p for p in session.user.playlists() if p.name == PLAYLIST_NAME]
if existing:
    playlist = existing[0]
    print(f"🎧 Using existing playlist: {playlist.name}")
else:
    playlist = session.user.create_playlist(PLAYLIST_NAME, "Auto-added from Radio Arabella")
    print(f"📀 Created new playlist: {playlist.name}")

# === TRACK STATE ===
last_title = None
added_titles = set()


# === LOGGING FUNCTION ===
def log(title):
    with open(LOG_PATH, "a") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {title}\n")


# === FUNCTION TO GET STREAM TITLE ===
def get_stream_title():
    try:
        result = subprocess.run([
            FFPROBE_PATH, "-v", "quiet",
            "-show_entries", "format_tags=StreamTitle",
            "-of", "default=nw=1:nk=1",
            STREAM_URL
        ], capture_output=True, timeout=10)

        return result.stdout.decode("UTF-8").strip()
    except subprocess.TimeoutExpired:
        return None


# === FUNCTION TO ADD SONG TO TIDAL ===
def add_to_tidal(title):
    searchres = session.search(query=title, models=[media.Track])
    top_hit = searchres.get("top_hit")
    if top_hit is None:
        print(f"{title} not found in Tidal")
        return
    try:
        playlist.add([top_hit.id])
        print(f"✅ Added to Tidal: {top_hit.artist.name} – {top_hit.name}")
        log(f"Added: {top_hit.artist.name} – {top_hit.name}")
    except Exception as e:
        print(f"🛑 ERROR: {title} produced error: {e}")
        time.sleep(3)
        playlist.add([top_hit.id])


# ⚠️ Clears all tracks in the playlist
def clear_playlist():
    playlists = session.user.playlists()

    for pl in playlists:
        if pl.name == PLAYLIST_NAME:
            print(f"🧹 Clearing playlist: {pl.name}")
            pl.clear()
            return

    print(f"⚠️ Playlist '{PLAYLIST_NAME}' not found.")


# === MAIN LOOP ===
print("🎙 Watching Radio Arabella...")
#clear_playlist()

while True:
    title = get_stream_title()

    if not title or title in INVALID_TITLES or title.isspace():
        time.sleep(1)
        continue

    if title != last_title and title not in added_titles:
        print(f"🎶 New song detected: {title}")
        add_to_tidal(title)
        added_titles.add(title)
        last_title = title
    else:
        print(f"🔁 Still playing: {title}")

    time.sleep(30)
