#!/usr/bin/env python3
"""
TermTunes (Compatible Edition)
==============================

✅ Fully works in restricted environments (no inquirer required)
✅ Lets you search songs from YouTube Music (via ytmusicapi)
✅ Shows top N results and lets you select one
✅ Plays audio using mpv (or just prints URL if --no-play)
✅ Has offline --mock mode for safe testing

Usage examples:
---------------
python term-tunes-compatible.py "shape of you"
python term-tunes-compatible.py --mock "perfect"
python term-tunes-compatible.py --mock --auto "believer"
python term-tunes-compatible.py --limit 10 --no-play "faded"

Dependencies:
-------------
pip install ytmusicapi yt-dlp
sudo apt install mpv   # (Linux)
"""

import sys
import argparse
import shutil
import subprocess

# Try optional imports
try:
    from ytmusicapi import YTMusic
except Exception:
    YTMusic = None


def search_with_ytmusic(query, limit=5):
    """Search YouTube Music for songs."""
    if YTMusic is None:
        raise RuntimeError("ytmusicapi not installed. Run: pip install ytmusicapi")

    ytm = YTMusic()
    results = ytm.search(query, filter="songs") or []
    songs = []
    for item in results[:limit]:
        title = item.get("title") or "Unknown Title"
        artists = item.get("artists") or []
        artist = (
            artists[0].get("name")
            if artists and isinstance(artists[0], dict) and artists[0].get("name")
            else "Unknown Artist"
        )
        video_id = item.get("videoId")
        if not video_id:
            continue
        url = f"https://www.youtube.com/watch?v={video_id}"
        songs.append({"title": title, "artist": artist, "url": url})
    return songs


def search_with_mock(query, limit=5):
    """Return fake results (offline testing)."""
    return [
        {
            "title": f"{query} (Mock {i+1})",
            "artist": f"Mock Artist {i+1}",
            "url": f"https://www.youtube.com/watch?v=mock{i+1}",
        }
        for i in range(limit)
    ]


def choose_song(songs, auto=False):
    """Show numbered list and let user choose one."""
    if not songs:
        return None
    if auto:
        return 0

    print("\nSelect a song:")
    for i, s in enumerate(songs, start=1):
        print(f"{i}. {s['title']} - {s['artist']}")

    while True:
        try:
            choice = input("Enter number (or blank to cancel): ").strip()
        except EOFError:
            return None
        if not choice:
            return None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(songs):
                return idx
            print("Invalid choice. Try again.")
        except ValueError:
            print("Please enter a valid number.")


def play_with_mpv(url):
    """Play a YouTube link using mpv."""
    if not shutil.which("mpv"):
        raise RuntimeError("mpv not found. Please install it to play songs.")

    try:
        subprocess.run(["mpv", "--no-video", url], check=True)
    except subprocess.CalledProcessError as e:
        print(f"mpv exited with error code {e.returncode}")
    except KeyboardInterrupt:
        print("\nStopped by user.")


def search_and_play(query, limit=5, use_mock=False, auto=False, no_play=False):
    """Main search and play logic."""
    if not query.strip():
        print("Empty query.")
        return None

    try:
        songs = search_with_mock(query, limit) if use_mock else search_with_ytmusic(query, limit)
    except Exception as e:
        print(f"Error while searching: {e}")
        return None

    if not songs:
        print("No results found.")
        return None

    print("\nTop Results:")
    for i, s in enumerate(songs, start=1):
        print(f"{i}. {s['title']} - {s['artist']}")

    idx = choose_song(songs, auto)
    if idx is None:
        print("No song selected.")
        return None

    selected = songs[idx]
    print(f"\n🎵 Selected: {selected['title']} - {selected['artist']}")
    print(f"🔗 URL: {selected['url']}\n")

    if no_play:
        print("--no-play enabled, not launching mpv.")
        return selected

    try:
        play_with_mpv(selected["url"])
    except Exception as e:
        print(f"Failed to play: {e}")
    return selected


def main(argv=None):
    parser = argparse.ArgumentParser(description="TermTunes (compatible): search & play YouTube Music songs.")
    parser.add_argument("query", nargs="?", help="Song name to search.")
    parser.add_argument("--mock", action="store_true", help="Use mock mode (offline testing).")
    parser.add_argument("--limit", type=int, default=5, choices=[1, 3, 5, 7, 10], help="Number of results to show.")
    parser.add_argument("--auto", action="store_true", help="Auto-select first result (non-interactive).")
    parser.add_argument("--no-play", action="store_true", help="Don't play, just print selection.")
    args = parser.parse_args(argv)

    if args.query:
        query = args.query
    else:
        try:
            query = input("Search for a song (or blank to quit): ").strip()
        except EOFError:
            return 0
        if not query:
            return 0

    search_and_play(query, limit=args.limit, use_mock=args.mock, auto=args.auto, no_play=args.no_play)
    return 0



def main_entry():
    raise SystemExit(main())

if __name__ == "__main__":
    main_entry()
