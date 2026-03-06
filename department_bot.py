# 部门AI模板
import discord
import os
import redis
import json
import threading
import time

# --- Config ---
TOKEN = os.environ.get("DISCORD_BOT_TOKEN") # The specific department bot's token
DEPARTMENT_ID = os.environ.get("DEPARTMENT_ID") # e.g., "ENG", "SAL"
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = int(os.environ.get("REDIS_PORT"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")

QUEUE_NAME = f"task_queue_{DEPARTMENT_ID.lower()}"

# --- Redis Connection ---
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)

# --- Discord Client ---
intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)
def worker():
    pubsub = r.pubsub()
    pubsub.subscribe(QUEUE_NAME)
    print(f"Worker for {DEPARTMENT_ID} subscribed to {QUEUE_NAME}")
    for raw_message in pubsub.listen():
        if raw_message['type'] == 'message':
            task = json.loads(raw_message['data'])
            # --- AI LOGIC GOES HERE ---
            # This is where you would call your language model or ERP tools
            # For now, we'll just echo back
            print(f"Processing task for {DEPARTMENT_ID}: {task['content']}")
            
            # Formulate reply
            response_content = f"【{DEPARTMENT_ID} AI】: 收到指令 '{task['content']}'。正在处理..."
                        
            # Send reply
            channel = client.get_channel(task['channel_id'])
            if channel:
                # We need to run this in the main thread's event loop
                client.loop.create_task(channel.send(response_content))

@client.event
async def on_ready():
    print(f'Department Bot {client.user} ({DEPARTMENT_ID}) is online!')
    # Start the redis worker in a separate thread
    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
    client.run(TOKEN)