Dockerfile
import discord
import os
import redis
import json
import logging

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Config ---
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)

# Validate required environment variables
if not TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN environment variable is not set")

# --- Redis Connection ---
try:
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_keepalive=True
    )
    r.ping()
    logger.info(f"✓ Redis connected: {REDIS_HOST}:{REDIS_PORT}")
except Exception as e:
    logger.error(f"✗ Redis connection failed: {e}")
    raise

# --- Bot ID to Queue Mapping ---
# This maps Discord user IDs to their respective task queues
# Format: {"user_id": "task_queue_department"}
BOT_ID_TO_QUEUE = {}

def load_bot_mapping():
    """Load bot ID to queue mapping from Redis or environment"""
    global BOT_ID_TO_QUEUE
    try:
        # Try to load from Redis
        mapping_json = r.get("bot_id_to_queue_mapping")
        if mapping_json:
            BOT_ID_TO_QUEUE = json.loads(mapping_json)
            logger.info(f"✓ Loaded bot mapping from Redis: {BOT_ID_TO_QUEUE}")
        else:
            # Default mapping (can be updated via Redis)
            BOT_ID_TO_QUEUE = {}
            logger.info("Bot mapping is empty. Waiting for configuration...")
    except Exception as e:
        logger.error(f"✗ Failed to load bot mapping: {e}")
        BOT_ID_TO_QUEUE = {}

# --- Discord Client Setup ---
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
client = discord.Client(intents=intents)

# --- Event Handlers ---
@client.event
async def on_ready():
    logger.info(f"✓ Gateway Bot {client.user} is online!")
    load_bot_mapping()

@client.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return
    
    # Check if message mentions any registered bots
    for user_mention in message.mentions:
        queue = BOT_ID_TO_QUEUE.get(str(user_mention.id))
        if queue:
            logger.info(f"Routing message for {user_mention.name} to queue: {queue}")
            task = {
                "channel_id": message.channel.id,
                "author_id": message.author.id,
                "message_id": message.id,
                "content": message.content
            }
            try:
                r.publish(queue, json.dumps(task))
                logger.info(f"✓ Message published to {queue}")
            except Exception as e:
                logger.error(f"✗ Failed to publish message: {e}")
            return

# --- Main Entry Point ---
if __name__ == "__main__":
    try:
        logger.info("Starting Gateway Bot...")
        client.run(TOKEN)
    except Exception as e:
        logger.error(f"✗ Failed to start bot: {e}")
        raise