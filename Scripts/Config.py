# Local Server Connection Details
server_ip = '192.168.0.30'
server_port = 6969

# Embed Message Configs
action_colours = {"Push": 16098851,
                  "PR": 9442302,
                  "Misc": 16777215,
                  "Issue": 13632027,
                  "Mod": 852223}

repo_pfps = {
    "SirChopwood/test": "https://media.discordapp.net/attachments/562121682538594314/707549568182779924/pack101.png",
    "SirChopwood/FICSIT-PR": "https://media.discordapp.net/attachments/695978034930647050/708456415517343774/ficsitfelix.png"}


# Answer Back Promps
kronos_keywords = ["update", "release", "progress", "broken", "crash", "news", "issue", "version", "problem", "finish",
                   "work", "alternative", "new", "overhaul"]


# GraphQL Queries
def mod_query(name):
    return str('''{
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