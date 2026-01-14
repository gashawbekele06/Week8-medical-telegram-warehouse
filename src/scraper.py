"""
Telegram Medical Channels Scraper
---------------------------------
Extracts messages + images from public Ethiopian medical Telegram channels
Stores raw data in partitioned JSON + images in folder structure

Usage:
    uv run python src/scraper.py
    # or after activation: python src/scraper.py

Environment variables needed (.env):
    TELEGRAM_API_ID
    TELEGRAM_API_HASH
    TELEGRAM_PHONE          # optional - for first time login
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import (
    FloodWaitError,
    SessionPasswordNeededError,
)
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import MessageMediaPhoto
from tqdm import tqdm

# ─── CONFIGURATION

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", ""))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
PHONE = os.getenv("TELEGRAM_PHONE")  # optional

SESSION_NAME = "medical_scraper_session"

# Channels (usernames without @)
CHANNELS = [
    "chemed123",              # CheMed (most common spelling)
    "lobelia4cosmetics",
    "tikvahpharma",
    # Very popular additional medical/pharma channels in Ethiopia 2025-2026:
    "ethiopharmacy",
    "ethio_medical",
    "pharmacyethiopia",
]

# Where to save everything
DATA_ROOT = Path("data/raw")
IMAGES_DIR = DATA_ROOT / "images"
MESSAGES_DIR = DATA_ROOT / "telegram_messages"
LOGS_DIR = Path("logs")

# How many messages to fetch per request
LIMIT_PER_REQUEST = 100

# ─── LOGGING SETUP ──────────────────────────────────────────────────────────────

LOGS_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "scraper.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


async def get_client():
    """Create and authenticate Telegram client"""
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

    await client.start(phone=PHONE)

    if not await client.is_user_authorized():
        if PHONE is None:
            raise ValueError("TELEGRAM_PHONE is required for first login")

        logger.info("Sending code request...")
        await client.send_code_request(PHONE)

        code = input("Enter the code you received: ").strip()
        try:
            await client.sign_in(PHONE, code)
        except SessionPasswordNeededError:
            password = input("Two-step verification enabled. Enter password: ")
            await client.sign_in(password=password)

    logger.info("Client authenticated successfully")
    return client


async def scrape_channel(client: TelegramClient, channel: str):
    """Scrape one channel - messages + download photos"""

    try:
        entity = await client.get_entity(channel)
        channel_title = getattr(entity, "title", channel)

        logger.info(f"Starting scrape of {channel} ({channel_title})")

        offset_id = 0
        total_saved = 0

        while True:
            try:
                history = await client(
                    GetHistoryRequest(
                        peer=entity,
                        offset_id=offset_id,
                        offset_date=None,
                        add_offset=0,
                        limit=LIMIT_PER_REQUEST,
                        max_id=0,
                        min_id=0,
                        hash=0,
                    )
                )

                if not history.messages:
                    break

                messages_batch = []

                for message in tqdm(
                    history.messages,
                    desc=f"{channel} (offset {offset_id})",
                    leave=False,
                ):
                    if message.id <= offset_id and offset_id != 0:
                        continue  # safety

                    msg_dict = {
                        "message_id": message.id,
                        "channel_username": channel,
                        "channel_title": channel_title,
                        "date": message.date.isoformat(),
                        "text": message.message or "",
                        "views": message.views or 0,
                        "forwards": message.forwards or 0,
                        "has_media": bool(message.media),
                        "image_path": None,
                    }

                    # Download photo if exists
                    if isinstance(message.media, MessageMediaPhoto):
                        image_dir = IMAGES_DIR / channel
                        image_dir.mkdir(parents=True, exist_ok=True)

                        filename = f"{message.id}.jpg"
                        path = image_dir / filename

                        await client.download_media(
                            message=message.media,
                            file=path,
                            progress_callback=lambda rec, tot: None,  # silent
                        )

                        msg_dict["image_path"] = str(
                            path.relative_to(DATA_ROOT.parent))

                    messages_batch.append(msg_dict)

                # Save batch by date (partitioned)
                for msg in messages_batch:
                    date_str = datetime.fromisoformat(
                        msg["date"]).strftime("%Y-%m-%d")
                    target_dir = MESSAGES_DIR / date_str
                    target_dir.mkdir(parents=True, exist_ok=True)

                    file_path = target_dir / f"{channel}.jsonl"

                    with open(file_path, "a", encoding="utf-8") as f:
                        json.dump(msg, f, ensure_ascii=False)
                        f.write("\n")

                total_saved += len(messages_batch)
                offset_id = history.messages[-1].id

                if len(history.messages) < LIMIT_PER_REQUEST:
                    break

            except FloodWaitError as e:
                logger.warning(
                    f"Rate limit hit! Waiting {e.seconds} seconds...")
                await asyncio.sleep(e.seconds)

        logger.info(f"Finished {channel} → {total_saved:,} messages saved")

    except Exception as e:
        logger.error(f"Error scraping {channel}: {str(e)}", exc_info=True)


async def main():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    MESSAGES_DIR.mkdir(parents=True, exist_ok=True)

    async with await get_client() as client:
        for channel in CHANNELS:
            await scrape_channel(client, channel)


if __name__ == "__main__":
    asyncio.run(main())
