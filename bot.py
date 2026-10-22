import os
import asyncio
import logging
from urllib.parse import quote

import aiohttp
import discord
import feedparser
from discord import app_commands
from discord.ext import commands, tasks

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("linkter-music")

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
ANNOUNCE_CHANNEL_ID = int(os.environ.get("ANNOUNCE_CHANNEL_ID", "0"))
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID", "UC6LtepCwB5hIf08JYCKewEQ")
YOUTUBE_CHANNEL_URL = os.getenv(
    "YOUTUBE_CHANNEL_URL", "https://www.youtube.com/@LinkterOfficial"
)
SPOTIFY_URL = os.getenv("SPOTIFY_URL", "").strip()
# Optional: one URL per line. Add specific Spotify tracks/albums/releases here.
EXTRA_MUSIC_LINKS = [
    line.strip()
    for line in os.getenv("EXTRA_MUSIC_LINKS", "").splitlines()
    if line.strip().startswith(("https://open.spotify.com/", "https://www.youtube.com/"))
]
# Upload titles/descriptions must contain one of these words to auto-announce.
# Set to empty to announce every upload from the channel.
KEYWORDS = [
    word.strip().lower()
    for word in os.getenv(
        "MUSIC_KEYWORDS",
        "music,musique,official audio,official video,lyrics,lyric video,phonk,funk,remix,prod,link cap label",
    ).split(",")
    if word.strip()
]
POLL_MINUTES = max(5, int(os.getenv("POLL_MINUTES", "10")))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
last_seen_video_id = None
seen_video_ids: set[str] = set()


def is_music(entry) -> bool:
    if not KEYWORDS:
        return True
    text = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
    return any(word in text for word in KEYWORDS)


def youtube_video_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def make_links_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Linkter Music",
        description="Listen to Linkter's music and releases using the links below.",
        color=discord.Color.blurple(),
    )
    embed.add_field(
        name="YouTube",
        value=(
            f"[Linkter Official channel]({YOUTUBE_CHANNEL_URL})\n"
            f"[All channel uploads](https://www.youtube.com/playlist?list=UU{YOUTUBE_CHANNEL_ID[2:]})\n"
            f"[Search Linkter music](https://www.youtube.com/results?search_query={quote('Linkter music')})"
        ),
        inline=False,
    )
    if SPOTIFY_URL:
        embed.add_field(name="Spotify", value=f"[Listen on Spotify]({SPOTIFY_URL})", inline=False)
    if EXTRA_MUSIC_LINKS:
        embed.add_field(
            name="More music",
            value="\n".join(f"[Release {i}]({url})" for i, url in enumerate(EXTRA_MUSIC_LINKS, 1)),
            inline=False,
        )
    embed.set_footer(text="Links open YouTube or Spotify. No audio is hosted by this bot.")
    return embed


async def announce(entry, channel=None):
    channel = channel or bot.get_channel(ANNOUNCE_CHANNEL_ID)
    if channel is None:
        log.warning("Announcement channel not found; set ANNOUNCE_CHANNEL_ID.")
        return
    video_id = entry.get("yt_videoid") or entry.get("id", "").split(":")[-1]
    title = entry.get("title", "New Linkter upload")
    link = entry.get("link") or youtube_video_url(video_id)
    embed = discord.Embed(
        title=title[:256],
        url=link,
        description=f"[Watch on YouTube]({link})",
        color=discord.Color.red(),
    )
    embed.set_author(name="Linkter Music", url=YOUTUBE_CHANNEL_URL)
    await channel.send(embed=embed)


@tasks.loop(minutes=POLL_MINUTES)
async def check_youtube_uploads():
    global last_seen_video_id
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(feed_url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                response.raise_for_status()
                xml = await response.text()
        feed = feedparser.parse(xml)
        entries = list(feed.entries)
        if not entries:
            return

        # On first run, remember current uploads without flooding the channel.
        if last_seen_video_id is None:
            last_seen_video_id = entries[0].get("yt_videoid")
            seen_video_ids.update(e.get("yt_videoid", "") for e in entries)
            return

        new_entries = []
        for entry in entries:
            video_id = entry.get("yt_videoid", "")
            if video_id == last_seen_video_id:
                break
            if video_id and video_id not in seen_video_ids:
                new_entries.append(entry)

        # Announce oldest-first, only when the title/description looks music-related.
        for entry in reversed(new_entries):
            video_id = entry.get("yt_videoid", "")
            seen_video_ids.add(video_id)
            if is_music(entry):
                await announce(entry)

        last_seen_video_id = entries[0].get("yt_videoid", last_seen_video_id)
    except Exception:
        log.exception("Could not check YouTube uploads")


@check_youtube_uploads.before_loop
async def before_upload_check():
    await bot.wait_until_ready()


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        log.info("Logged in as %s; synced %s slash commands", bot.user, len(synced))
    except Exception:
        log.exception("Slash-command sync failed")
    if not check_youtube_uploads.is_running():
        check_youtube_uploads.start()


@bot.tree.command(name="music", description="Show Linkter's official music links.")
async def music(interaction: discord.Interaction):
    await interaction.response.send_message(embed=make_links_embed())


@bot.tree.command(name="publish", description="Publish Linkter Music links in this channel.")
@app_commands.checks.has_permissions(manage_messages=True)
async def publish(interaction: discord.Interaction):
    await interaction.response.send_message(embed=make_links_embed())
    log.info("Music links published by %s in %s", interaction.user, interaction.channel_id)


@bot.tree.command(name="musicsearch", description="Find Linkter music on YouTube.")
@app_commands.describe(query="A song title, release, or keyword")
async def musicsearch(interaction: discord.Interaction, query: str):
    url = "https://www.youtube.com/results?search_query=" + quote(f"Linkter {query}")
    await interaction.response.send_message(f"[Search YouTube for Linkter: {discord.utils.escape_markdown(query)}]({url})")


@publish.error
async def publish_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        message = "You need the **Manage Messages** permission to publish the links."
    else:
        log.exception("Publish command failed", exc_info=error)
        message = "I couldn't publish the links. Check the bot logs."
    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)


bot.run(DISCORD_TOKEN)
