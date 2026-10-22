# Linkter Music — Discord bot

A Discord bot that publishes clickable links to Linkter's YouTube channel and Spotify music, and can announce new music-related YouTube uploads.

Repository: https://github.com/LinkterOfficial/Linkter-Music  
YouTube: https://www.youtube.com/@LinkterOfficial

## Features

- `/music` — show YouTube channel, all uploads playlist, YouTube music search, configured Spotify link, and optional release links.
- `/publish` — publish the same link embed in the current channel (requires **Manage Messages**).
- `/musicsearch query:` — clickable YouTube search for a Linkter track.
- Polls the YouTube channel RSS feed and announces new uploads whose title/description matches the configured music keywords.
- No Spotify API key is required for the profile/release links; Spotify links are normal clickable links.

## 1. Create a Discord application and bot

1. Open https://discord.com/developers/applications and create an application named **Linkter Music**.
2. Open **Bot** and create/reset the bot token. Keep it secret.
3. Under **OAuth2 → URL Generator**, select scopes `bot` and `applications.commands`.
4. Give it permission to **View Channels**, **Send Messages**, **Embed Links**, and **Read Message History**. Open the generated URL and invite it to your server.
5. Enable **Message Content Intent** is not required for these slash commands.

## 2. Configure environment variables

Copy `.env.example` to `.env` and fill in the values. Never commit `.env` or your bot token.

- `DISCORD_TOKEN`: token from the Discord Developer Portal.
- `ANNOUNCE_CHANNEL_ID`: numeric ID of the channel where new music uploads should be announced. Enable Developer Mode in Discord, then right-click the channel → Copy Channel ID.
- `SPOTIFY_URL`: your Spotify artist profile URL, or a public Spotify playlist/album link.
- `EXTRA_MUSIC_LINKS`: optional list of direct Spotify track/album URLs or YouTube URLs, one per line.
- `MUSIC_KEYWORDS`: comma-separated words to identify music uploads. Use an empty value to announce every channel upload (not recommended if the channel also posts gaming videos).
- `POLL_MINUTES`: RSS polling interval, minimum 5 minutes.

The default YouTube channel ID is Linkter's channel. You can override it if needed.

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

- The YouTube RSS feed only exposes recent uploads; the all-uploads playlist link is included so members can browse the full channel history.
- Keyword matching is a best-effort filter, not a perfect music classifier. Adjust `MUSIC_KEYWORDS` to match your upload titles/descriptions.
- The bot shares links; it does not download or re-upload music.
