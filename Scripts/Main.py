import WebhookListener
import discord
import os
import asyncio
import CreateEmbed
import json
import threading

class Bot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.git_listener = threading.Thread(target=WebhookListener.start_listener, args=[self])
        self.git_listener.daemon = True
        self.git_listener.start()
        self.queue_checker = self.loop.create_task(self.check_queue())

    async def on_ready(self):
        print('We have logged in as {0.user}'.format(self))

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')

    async def send_embed(self, embed_item):
        channel = self.get_channel(708420623310913628)
        await channel.send(content=None, embed=embed_item)

    def my_excepthook(self, type, value, traceback):
        print('Unhandled error:', type, value, traceback)

    async def check_queue(self):
        await self.wait_until_ready()
        while True:
            if os.path.exists("queue.txt"):
                with open("queue.txt", "r+") as file:
                    data = json.load(file)
                    try:
                        embed = CreateEmbed.run(data)
                    except:
                        self.my_excepthook()
                    await self.send_embed(embed)
                os.remove("queue.txt")
            else:
                await asyncio.sleep(1)


client = Bot()
client.run('NzA4NDU0NjE0MzgyNjc0MDYy.XrXl0g.zAIStFSBMU_y2NzBPwH6xy_3Y3Y')
