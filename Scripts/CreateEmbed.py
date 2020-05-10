import discord
import datetime
import requests
import json

with open("Config.json", "r") as file:
    Config = json.load(file)

def run(data):
    embed = "Debug"
    if "commits" in data:
        print(
            "Push Notification posted for " + str(data["repository"]["name"] + "/" + data["ref"].lstrip("refs/heads")))
        embed = push(data)
    elif "pull_request" in data:
        embed = pull_request(data)
    elif "action" in data:
        if data["action"] == "added":
            embed = contributer_added(data)
    else:
        print(data)

    return embed


def push(data):
    repo_name = data["repository"]["full_name"]
    repo_full_name = str(data["repository"]["name"] + "/" + data["ref"].lstrip("refs/heads"))

    embed = discord.Embed(title=str("Push created by __**" + data["sender"]["login"] + "**__"),
                          colour=Config["action_colours"]["Push"], url=data["repository"]["url"],
                          description=data["head_commit"]["message"],
                          timestamp=datetime.datetime.now())

    embed.set_thumbnail(url=data["sender"]["avatar_url"])
    embed.set_author(name=repo_full_name, icon_url=Config["repo pfps"][repo_name])
    embed.set_footer(text="FICSIT PR Dept. by Illya#5376",
                     icon_url="https://cdn.discordapp.com/avatars/110838934644211712/e486240daf6006f8de59bb866b74dcfc.png")

    commits = data["commits"]

    embed.add_field(name=commits[0]["message"],
                    value=str(
                        "[Link to commit](" + commits[0]["url"] + ")\n✅ " + str(len(commits[0]["added"])) + " ❌ " + str(
                            len(commits[0]["removed"])) + " 📝 " + str(len(commits[0]["modified"]))), inline=False)
    commits = commits[1:]

    for commit in commits:
        embed.add_field(name=commit["message"],
                        value=str(
                            "[Link to commit](" + commit["url"] + ")\n✅ " + str(len(commit["added"])) + " ❌ " + str(
                                len(commit["removed"])) + " 📝 " + str(len(commit["modified"]))), inline=False)

    return embed


def contributer_added(data):
    repo_name = data["repository"]["full_name"]
    repo_full_name = str(data["repository"]["name"] + data["ref"].lstrip("refs/heads"))

    embed = discord.Embed(title=str("__**" + data["member"]["login"] + "**__ has been added to the Repository."),
                          colour=Config["action_colours"]["Misc"], url=data["repository"]["url"], description=" ",
                          timestamp=datetime.datetime.now())

    embed.set_thumbnail(url=data["member"]["avatar_url"])
    embed.set_author(name=repo_full_name, icon_url=Config["repo pfps"][repo_name])
    embed.set_footer(text="FICSIT PR Dept. by Illya#5376",
                     icon_url="https://cdn.discordapp.com/avatars/110838934644211712/e486240daf6006f8de59bb866b74dcfc.png")
    return embed


def pull_request(data):
    repo_name = data["repository"]["full_name"]
    repo_full_name = str(data["repository"]["name"] + "/" + data["pull_request"]["head"]["ref"])

    embed = discord.Embed(title=str("Pull Request " + data["action"] + " by __**" + data["sender"]["login"] + "**__"),
                          colour=Config["action_colours"]["PR"], url=data["repository"]["url"],
                          description=data["pull_request"]["title"],
                          timestamp=datetime.datetime.now())

    embed.set_thumbnail(url=data["sender"]["avatar_url"])
    embed.set_author(name=repo_full_name, icon_url=Config["repo pfps"][repo_name])
    embed.set_footer(text="FICSIT PR Dept. by Illya#5376",
                     icon_url="https://cdn.discordapp.com/avatars/110838934644211712/e486240daf6006f8de59bb866b74dcfc.png")

    stats = str("[Link to PR](" + data["pull_request"]["url"] +
                ")\n📋 " + str(data["pull_request"]["commits"]) +
                "\n✅ " + str(data["pull_request"]["additions"]) +
                " ❌ " + str(data["pull_request"]["deletions"]) +
                " 📝 " + str(data["pull_request"]["changed_files"]))

    direction = str(data["pull_request"]["head"]["ref"] + " -> " + data["pull_request"]["base"]["ref"])
    embed.add_field(name=direction, value=stats)

    return embed


def mod(name):
    # GraphQL Queries

    query = str('''{
      getMods(filter: { search: "''' + name + '''", order_by: last_version_date, order:desc}) {
        mods {
          name
          authors {
            user {
              username
            }
          }
          logo
          short_description
          full_description
          last_version_date
          id
        }
      }
    }''')
    data = requests.post("https://api.ficsit.app/v2/query", json={'query': query})
    data = json.loads(data.text)
    data = data["data"]["getMods"]["mods"]

    for mod in data:
        if mod["name"] == name:
            data = mod
            break
    if isinstance(data, list):
        if len(data) > 1:
            mod_list = ""
            for mod in data:
                mod_list = str(mod_list + mod["name"] + "\n")
            return mod_list, None
        elif len(data) == 0:
            return None, None
        else:
            data = data[0]
    date = str(data["last_version_date"][0:10] + " " + data["last_version_date"][11:19])

    embed = discord.Embed(title=data["name"],
                          colour=Config["action_colours"]["Mod"], url=str("https://ficsit.app/mod/" + data["id"]),
                          description=str(data["short_description"] +
                                          "\n\n Last Updated: " + date +
                                          "\nCreated by: " + data["authors"][0]["user"]["username"]),
                          timestamp=datetime.datetime.now())

    embed.set_thumbnail(url=data["logo"])
    embed.set_author(name="ficsit.app Mod Lookup")
    embed.set_footer(text="FICSIT PR Dept. by Illya#5376",
                     icon_url="https://cdn.discordapp.com/avatars/110838934644211712/e486240daf6006f8de59bb866b74dcfc.png")
    return embed, data["full_description"]


def desc(full_desc):
    if len(full_desc) > 1800:
        full_desc = full_desc[:1800]
    embed = discord.Embed(title="Description",
                          colour=Config["action_colours"]["Mod"],
                          description=full_desc,
                          timestamp=datetime.datetime.now())
    embed.set_author(name="ficsit.app Mod Description")
    embed.set_footer(text="FICSIT PR Dept. by Illya#5376",
                     icon_url="https://cdn.discordapp.com/avatars/110838934644211712/e486240daf6006f8de59bb866b74dcfc.png")
    return embed
