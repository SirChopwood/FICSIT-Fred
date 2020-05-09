import json
import discord
import datetime
import Config


def push(data):
    repo_name = data["repository"]["full_name"]
    embed = discord.Embed(title=str("Pushed by __**" + data["sender"]["login"] + "**__"),
                          colour=Config.action_colours["Push"],
                          url=data["repository"]["url"], description=data["head_commit"]["message"],
                          timestamp=datetime.datetime.now())
    embed.set_thumbnail(url=data["sender"]["avatar_url"])
    embed.set_author(name=data["repository"]["name"], icon_url=Config.repo_pfps[repo_name])
    embed.set_footer(text="FICSIT Felix by Illya#5376",
                     icon_url="https://cdn.discordapp.com/avatars/110838934644211712/e486240daf6006f8de59bb866b74dcfc.png")

    for commit in data["commits"]:
        embed.add_field(name=commit["message"],
                        value=str("[Link to commit](" + commit["url"] + ")\n✅ " + str(len(commit["added"])) + " ❌ " + str(
                            len(commit["removed"])) + " 📝 " + str(len(commit["modified"]))), inline=False)

    return embed
