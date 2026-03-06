# 网关代码
import discord
import os
import redis
import json

# --- Config ---
TOKEN = os.environ.get("DISCORD_BOT_TOKEN") # The main gateway bot's token
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = int(os.environ.get("REDIS_PORT"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
# --- Redis Connection ---
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)

# --- Department Bot Mapping (User ID to Queue Name) ---
# This maps the Discord User ID of the bot to its task queue
BOT_ID_TO_QUEUE = {
    "1477663752047427759": "task_queue_eng", # 工程
    "1477648158057041982": "task_queue_scm", # 采购
    "1477643295407603872": "task_queue_sal", # 销售
    "1477662763600838796": "task_queue_fin", # 财务
    "1477541170682007645": "task_queue_qc",  # 品管
    "1477665278228697234": "task_queue_whs"  # 仓储
}
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Gateway Bot {client.user} is online!')

@client.event
async def on_message(message):
    # Don't respond to ourselves
    if message.author == client.user:
         return

    # Check for mentions
    for user_mention in message.mentions:
        queue = BOT_ID_TO_QUEUE.get(str(user_mention.id))
        if queue:
            print(f"Routing message for {user_mention.name} to queue: {queue}")
            task = {
                "channel_id": message.channel.id,
                "author_id": message.author.id,
                "message_id": message.id,
                "content": message.content
            }
            r.publish(queue, json.dumps(task))
            return # Stop after routing to the first mentioned bot
            client.run(TOKEN)       