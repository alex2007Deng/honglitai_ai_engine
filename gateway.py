@client.event
async def on_ready():
    print(f'Gateway Bot {client.user} is online!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
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
            return

# 这行应该在所有事件处理器之外
client.run(TOKEN)
