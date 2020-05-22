import WebhookListener
import discord
import os
import asyncio
import CreateEmbed
import json
import threading

# server = 192.168.0.4:6969 | computer = 192.168.0.30:7000

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

    async def on_message(self, message):
        if message.author.bot:
            return

        # Run all automation tasks

        # Automated Responses
        for automation in Config["automated responses"]:
            responded = False
            if len(message.author.roles) > 1 and automation["ignore members"] is False or len(
                    message.author.roles) == 1:

                for keyword in automation["keywords"]:
                    if keyword in message.content.lower() and responded is False:

                        for word in automation["additional words"]:
                            if word in message.content.lower() and responded is False:
                                responded = True
                                await message.channel.send(
                                    str(automation["response"].format(user=message.author.mention)))

        # Media Only Channels
        for automation in Config["media only channels"]:
            if message.channel.id == int(automation["id"]) and len(message.embeds) == 0 and len(
                    message.attachments) == 0:
                await message.author.send("Hi, " + message.author.name + " the channel '" + automation["name"]
                                          + "' you just tried to message in has been flagged as a 'Media Only' "
                                            "channel. This means you must post an embed or attach a file in order to "
                                            "post there. (we do not accept links)")
                await message.delete()

        # Normal Commands
        for automation in Config["commands"]:
            if message.content.startswith(automation["command"]):
                if automation["media"]:
                    await message.channel.send(content=None, file=discord.File(automation["response"]))
                else:
                    await message.channel.send(automation["response"])

        for automation in Config["role assignments"]:
            if message.content.startswith(automation["command"]):
                if automation["mod assignable"]:
                    authorised = False
                    for role in message.author.roles:
                        if role.name in Config["mod roles"]:
                            authorised = True
                    if authorised:
                        target = message.content.lstrip(str(automation["command"] + " <@!"))
                        target = int(target.rstrip(">"))
                        try:
                            target = message.guild.get_member(target)
                        except TypeError:
                            await message.channel.send("Invalid User, please Ping (@) the user or type their ID.")
                            return
                        if target is None:
                            await message.channel.send("User could not be found.")
                            return
                        else:
                            for role in message.guild.roles:
                                if role.name == automation["role"]:
                                    await target.add_roles(role)
                                    await message.channel.send(str(target.mention + automation["response"]))
                else:
                    for role in message.guild.roles:
                        if role.name == automation["role"]:
                            await message.author.add_roles(role)
                            await message.channel.send(automation["response"])

        # Special Commands
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
                    if reaction.emoji == "📋" and user == message.author and reaction.message.id == newmessage.id:
                        raise InterruptedError

                try:
                    await self.wait_for('reaction_add', timeout=60.0, check=check)
                except asyncio.TimeoutError:
                    print("User didnt react")
                except InterruptedError:
                    await message.channel.send(content=None, embed=CreateEmbed.desc(desc))

        elif message.content.startswith(">help"):
            newmessage = await message.channel.send(content=None, embed=CreateEmbed.command_list())

        elif message.content.startswith(">pirate"):
            authorised = False
            for role in message.author.roles:
                if role.name in Config["mod roles"]:
                    authorised = True
            if authorised:
                target = message.content.lstrip(">pirate <@!")
                target = int(target.rstrip(">"))
                try:
                    target = message.guild.get_member(target)
                except TypeError:
                    await message.channel.send("Invalid User, please Ping (@) the user or type their ID.")
                    return
                if target is None:
                    await message.channel.send("User could not be found.")
                    return
                else:
                    await target.send(
                        "***Yarr Harr, Fiddle dee dee... You are a pirate, who stole the game for free!***\n That "
                        "aint cool dude, so as a token of our dis-satisfactory we are banning you from the Discord. "
                        "If you find enough gold coins in your dirty pocket, feel free to pickup a copy of the game. "
                        "Send us proof and we will unban you!\n *- The Satisfactory Modding Discord Staff Team*")
                    await message.guild.ban(target, reason=str("Pirate - Banned by: " + message.author.name))
                    await message.channel.send(content=None, file=discord.File("../Images/Ban.gif"))


        # Config Commands
        elif message.content.startswith(">add response"):
            access = False
            for role in message.author.roles:
                if role.name in Config["mod roles"]:
                    access = True

            if access == False:
                return

            await message.channel.send("What would you like to name this automation? e.g. ``CommandDave``")
            name = await self.wait_for('message', timeout=30.0)
            name = name.content

            await message.channel.send(
                "What keywords would you like to add? e.g. ``apple banana 110838934644211712`` (The last is a Discord User ID to grab pings)")
            keywords = await self.wait_for('message', timeout=60.0)
            keywords = keywords.content.split(" ")

            await message.channel.send(
                "What additional words would you like to add? e.g. ``apple banana carrot 110838934644211712`` (The last is a Discord User ID to grab pings)")
            additional_words = await self.wait_for('message', timeout=60.0)
            additional_words = additional_words.content.split(" ")

            await message.channel.send(
                "What response do you want it to provide? e.g. ``Thanks for saying my keywords {user}`` (use {user} to ping the person saying the command (required))")
            response = await self.wait_for('message', timeout=60.0)
            response = response.content

            await message.channel.send(
                "Do you want it to ignore members (and only target non-members)? e.g. ``True`` or ``False``")
            ignore_members = await self.wait_for('message', timeout=10.0)
            ignore_members = ignore_members.content

            Config["automated responses"].append(
                {"name": name, "keywords": keywords, "additional words": additional_words, "response": response,
                 "ignore members": ignore_members})
            json.dump(Config, open("Config.json", "w"))
            await message.channel.send("Automated Response '" + name + "' added.")

        elif message.content.startswith(">remove response"):
            access = False
            for role in message.author.roles:
                if role.name in Config["mod roles"]:
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

        elif message.content.startswith(">add media only"):
            access = False
            for role in message.author.roles:
                if role.name in Config["mod roles"]:
                    access = True

            if access == False:
                return

            await message.channel.send("What is the name of the channel? e.g. ``Screenshots``")
            name = await self.wait_for('message', timeout=30.0)
            name = name.content

            await message.channel.send("What is the ID for the channel? e.g. ``709509235028918334``")
            id = await self.wait_for('message', timeout=60.0)
            id = id.content

            Config["media only channels"].append(
                {"name": name, "id": id})
            json.dump(Config, open("Config.json", "w"))
            await message.channel.send("Media Only Channel '" + name + "' added.")

        elif message.content.startswith(">remove media only"):
            access = False
            for role in message.author.roles:
                if role.name in Config["mod roles"]:
                    access = True

            if access == False:
                return

            await message.channel.send("Which Media Only Channel do you want to remove?")
            name = await self.wait_for('message', timeout=30.0)
            name = name.content

            index = 0
            for response in Config["media only channels"]:
                if response["name"] == name:
                    del Config["media only channels"][index]
                    json.dump(Config, open("Config.json", "w"))
                    await message.channel.send("Media Only Channel Removed!")
                    return
                else:
                    index += 1
            await message.channel.send("Media Only Channel could not be found!")

        elif message.content.startswith(">add command"):
            access = False
            for role in message.author.roles:
                if role.name in Config["mod roles"]:
                    access = True

            if access == False:
                return

            await message.channel.send("What is the command? e.g. ``>install``")
            command = await self.wait_for('message', timeout=30.0)
            command = command.content

            await message.channel.send("What is the response? e.g. ``Hello there`` or ``../Images/Install.png``")
            response = await self.wait_for('message', timeout=60.0)
            response = response.content

            await message.channel.send("Is the response a file? e.g. ``True`` or ``False``")
            media = await self.wait_for('message', timeout=60.0)
            media = json.loads(media.content.lower())

            Config["commands"].append(
                {"command": command, "response": response, "media": media})
            json.dump(Config, open("Config.json", "w"))
            await message.channel.send("Command '" + command + "' added.")

        elif message.content.startswith(">remove command"):
            access = False
            for role in message.author.roles:
                if role.name in Config["mod roles"]:
                    access = True

            if access == False:
                return

            await message.channel.send("Which Command do you want to remove? e.g. ``>install``")
            command = await self.wait_for('message', timeout=30.0)
            command = command.content

            index = 0
            for response in Config["commands"]:
                if response["command"] == command:
                    del Config["commands"][index]
                    json.dump(Config, open("Config.json", "w"))
                    await message.channel.send("Command Removed!")
                    return
                else:
                    index += 1
            await message.channel.send("Command could not be found!")


client = Bot()
client.run('NzA4NDU0NjE0MzgyNjc0MDYy.XrXl0g.zAIStFSBMU_y2NzBPwH6xy_3Y3Y')
