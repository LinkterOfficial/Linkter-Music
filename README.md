# Linkter Music — Discord bot

A Discord bot that publishes clickable links to Linkter's YouTube channel and Spotify music, and announces new music-related YouTube uploads.

Repository: https://github.com/LinkterOfficial/Linkter-Music  
YouTube: https://www.youtube.com/@LinkterOfficial

## Features

- `/music` — show the YouTube channel, all-uploads playlist, YouTube music search, Spotify search/profile, and optional release links.
- `/publish` — publish the same link embed in the current channel (requires **Manage Messages**).
- `/musicsearch query:` — clickable YouTube search for a Linkter track.
- Checks the YouTube RSS feed every 10 minutes and announces new uploads whose title/description matches the configured music keywords.
- Does not announce the existing latest upload on first startup.
- No Spotify API key is required for clickable Spotify profile/release links.

## 1. Create a Discord application and bot

1. Open https://discord.com/developers/applications and create an application named **Linkter Music**.
2. Open **Bot** and create/reset the bot token. Keep it secret.
3. Under **OAuth2 → URL Generator** (or **Installation**), select scopes `bot` and `applications.commands`.
4. Give it **View Channels**, **Send Messages**, and **Embed Links** permissions. Invite it to your server.
5. Message Content Intent is not required for these slash commands.

## 2. Configure environment variables

Copy `.env.example` to `.env` and fill in the values. Never commit `.env` or your bot token.

- `DISCORD_TOKEN`: token from the Discord Developer Portal.
- `ANNOUNCE_CHANNEL_ID`: numeric ID of the Discord channel where new music uploads should be announced. Enable Developer Mode in Discord, then right-click the channel → Copy Channel ID.
- `SPOTIFY_URL`: optional Spotify artist profile, playlist, album, or track URL. If omitted, `/music` links to a Spotify search for Linkter.
- `EXTRA_MUSIC_LINKS`: optional direct Spotify track/album URLs or YouTube URLs, one per line.
- `MUSIC_KEYWORDS`: comma-separated words used to identify music uploads. Set this to an empty value to announce every upload (not recommended if the channel also posts non-music videos).
- `POLL_MINUTES`: RSS polling interval, minimum 5 minutes.

The default YouTube channel ID is set for Linkter's channel. If `ANNOUNCE_CHANNEL_ID` is missing or invalid, the bot cannot send automatic announcements until a valid channel ID is configured.

## 3. Run locally

Python 3.10+ is recommended.

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows:
# .venv\\Scripts\\activate
pip install -r requirements.txt
python bot.py
```

Keep the process running for automatic announcements. For 24/7 announcements, deploy it to a Python-capable host and set the same environment variables there.

## Important notes

- The YouTube RSS feed only exposes recent uploads; the all-uploads playlist link is included so members can browse the channel history.
- Keyword matching is a best-effort filter, not a perfect music classifier. Tune `MUSIC_KEYWORDS` to match your music titles/descriptions.
- The bot shares links; it does not download or re-upload music.
