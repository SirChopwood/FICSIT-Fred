import json
import discord
import datetime
import Config


def run(data):
    if "commits" in data:
        embed = push(data)
    elif "action" in data:
        if data["action"] == "added":
            embed = contributer_added(data)
    else:
        print(data)

    if embed:
        return embed
    else:
        return


def push(data):
    repo_name = data["repository"]["full_name"]
    repo_full_name = str(data["repository"]["name"] + data["ref"].strip("refs/heads"))
    embed = discord.Embed(title=str("Pushed by __**" + data["sender"]["login"] + "**__"),
                          colour=Config.action_colours["Push"],
                          url=data["repository"]["url"], description=data["head_commit"]["message"],
                          timestamp=datetime.datetime.now())
    embed.set_thumbnail(url=data["sender"]["avatar_url"])
    embed.set_author(name=repo_full_name, icon_url=Config.repo_pfps[repo_name])
    embed.set_footer(text="FICSIT Felix by Illya#5376",
                     icon_url="https://cdn.discordapp.com/avatars/110838934644211712/e486240daf6006f8de59bb866b74dcfc.png")

    commits = data["commits"]
    commit = commits[0]
    embed.add_field(name=" ",
                    value="[Link to commit](" + commit["url"] + ")\n"
                          "✅Added:        " + str(len(commit["added"])) + "\n"
                          "❌Removed:   " + str(len(commit["removed"])) + "\n"
                          "📝Edited:         " + str(len(commit["modified"])) + "\n ", inline=False)
    commits = commits[1:]


    for commit in commits:
        embed.add_field(name=commit["message"],
                    value="[Link to commit](" + commit["url"] + ")\n"
                          "✅Added:        " + str(len(commit["added"])) + "\n"
                          "❌Removed:   " + str(len(commit["removed"])) + "\n"
                          "📝Edited:         " + str(len(commit["modified"])) + "\n ", inline=False)

    return embed

def contributer_added(data):
    repo_name = data["repository"]["full_name"]
    repo_full_name = str(data["repository"]["name"] + data["ref"].strip("refs/heads"))
    embed = discord.Embed(title=str("__**" + data["member"]["login"] + "**__ has been added to the Repository."),
                          colour=Config.action_colours["Misc"],
                          url=data["repository"]["url"], description=" ",
                          timestamp=datetime.datetime.now())
    embed.set_thumbnail(url=data["member"]["avatar_url"])
    embed.set_author(name=repo_full_name, icon_url=Config.repo_pfps[repo_name])
    embed.set_footer(text="FICSIT Felix by Illya#5376",
                     icon_url="https://cdn.discordapp.com/avatars/110838934644211712/e486240daf6006f8de59bb866b74dcfc.png")

    return embed