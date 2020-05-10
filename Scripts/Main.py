import WebhookListener
import discord
import os
import asyncio
import CreateEmbed
import json
import threading
import Config


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
        if "kronos" in message.content.lower() and len(message.author.roles) == 1 \
                or "110838934644211712" in message.content.lower() and len(message.author.roles) == 1:

            for word in Config.kronos_keywords:
                if word in message.content.lower():
                    await message.channel.send(
                        "Hi " + message.author.mention +
                        ", the Kronos Mod hasn't been updated for update 3 yet. Kronos is working on it, "
                        "but no release date has been announced. You might be interested in the Pak Utility Mod "
                        "instead, which does a lot of the same things.")

        if message.content.startswith(">mod"):
            result, desc = CreateEmbed.mod(message.content.lstrip(">mod "))
            if isinstance(result, str):
                await message.channel.send("Multiple mods found: ```" + result + "```")
            elif result is None:
                await message.channel.send("No mods found!")
            else:
                newmessage = await message.channel.send(content=None, embed=result)
                await newmessage.add_reaction("📋")
                await asyncio.sleep(2)
                def check(reaction, user):
                    if reaction.emoji == "📋":
                        raise InterruptedError

                try:
                    await self.wait_for('reaction_add', timeout=60.0, check=check)
                except asyncio.TimeoutError:
                    print("User didnt react")
                except InterruptedError:
                    await message.channel.send(content=None, embed=CreateEmbed.desc(desc))




    async def send_embed(self, embed_item):
        channel = self.get_channel(708420623310913628)
        await channel.send(content=None, embed=embed_item)

    async def check_queue(self):
        await self.wait_until_ready()
        while True:
            if os.path.exists("queue.txt"):
                with open("queue.txt", "r+") as file:
                    data = json.load(file)
                    try:
                        embed = CreateEmbed.run(data)
                    except:
                        print("Failed to create embed")
                    if embed == "Debug":
                        print("Unknown Payload received")
                    else:
                        await self.send_embed(embed)
                os.remove("queue.txt")
            else:
                await asyncio.sleep(1)


client = Bot()
client.run('NzA4NDU0NjE0MzgyNjc0MDYy.XrXl0g.zAIStFSBMU_y2NzBPwH6xy_3Y3Y')
