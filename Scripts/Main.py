import WebhookListener
import discord
import os
import asyncio
import CreateEmbed
import json
import threading

with open("Config.json", "r") as file:
    Config = json.load(file)


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
        if message.author.bot:
            return

        # Run all automation tasks
        for automation in Config["automated responses"]:
            responded = False
            if len(message.author.roles) > 1 and automation["ignore members"] is False or len(message.author.roles) == 1:

                for keyword in automation["keywords"]:
                    if keyword in message.content.lower() and responded is False:

                        for word in automation["additional words"]:
                            if word in message.content.lower() and responded is False:
                                responded = True
                                await message.channel.send(
                                    str(automation["response"].format(user=message.author.mention)))

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

        elif message.content.startswith(">generator"):
            await message.channel.send(content=None, file=discord.File("../Images/Generators.png"))

        elif message.content.startswith(">redirector"):
            await message.channel.send(content=None, file=discord.File("../Images/Redirectors.png"))

        elif message.content.startswith(">install"):
            await message.channel.send(content=None, file=discord.File("../Images/Install.png"))

        elif message.content.startswith(">docs"):
            await message.channel.send("https://docs.ficsit.app/")

        elif message.content.startswith(">add response"):
            access = False
            for role in message.author.roles:
                if role.name == "T3 Member" or role.name == "Moderator":
                    access = True

            if access == False:
                return

            await message.channel.send("What would you like to name this automation? e.g. ``CommandDave``")
            name = await self.wait_for('message', timeout=30.0)
            name = name.content

            await message.channel.send("What keywords would you like to add? e.g. ``apple banana carrot``")
            keywords = await self.wait_for('message', timeout=60.0)
            keywords = keywords.content.split(" ")

            await message.channel.send("What additional words would you like to add? e.g. ``apple banana carrot``")
            additional_words = await self.wait_for('message', timeout=60.0)
            additional_words = additional_words.content.split(" ")

            await message.channel.send("What response do you want it to provide? e.g. ``Thanks for saying my keywords {user}`` (use {user} to ping the user)")
            response = await self.wait_for('message', timeout=60.0)
            response = response.content

            await message.channel.send("Do you want it to ignore members (and only target non-members)? e.g. ``True`` or ``False``")
            ignore_members = await self.wait_for('message', timeout=10.0)
            ignore_members = ignore_members.content

            Config["automated responses"].append({"name": name, "keywords": keywords, "additional words": additional_words, "response": response, "ignore members": ignore_members})
            json.dump(Config, open("Config.json", "w"))
            await message.channel.send("Automated Response '" + name + "' added.")

        elif message.content.startswith(">remove response"):
            access = False
            for role in message.author.roles:
                if role.name == "T3 Member" or role.name == "Moderator":
                    access = True

            if access == False:
                return

            await message.channel.send("Which Automated Response do you want to remove?")
            name = await self.wait_for('message', timeout=30.0)
            name = name.content

            index = 0
            for response in Config["automated responses"]:
                if response["name"] == name:
                    del Config["automated responses"][index]
                    json.dump(Config, open("Config.json", "w"))
                    await message.channel.send("Response Removed!")
                    return
                else:
                    index += 1
            await message.channel.send("Response could not be found!")


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

"""
        if "kronos" in message.content.lower() and len(message.author.roles) == 1 \
                or "110838934644211712" in message.content.lower() and len(message.author.roles) == 1:

            for word in Config[]:
                if word in message.content.lower():
                    await message.channel.send(
                        "Hi " + message.author.mention +
                        ", the Kronos Mod hasn't been updated for update 3 yet. Kronos is working on it, "
                        "but no release date has been announced. You might be interested in the Pak Utility Mod "
                        "instead, which does a lot of the same things.")"""
