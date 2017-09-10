#!/usr/bin/env python3

from albion_api_client import AlbionAPI
import configparser
import requests
import pymysql.cursors
import json
import datetime
import time

config = configparser.ConfigParser()
config.read('config.ini')

albion = AlbionAPI()

# Connect to the MySQL Server using the data in the configfile
db = pymysql.connect(host=config['database']['hostname'],
  user=config['database']['username'],
  password=config['database']['password'],
  db=config['database']['database'],
  cursorclass=pymysql.cursors.DictCursor)
  # Because 2 spaces are better than one tab
db.autocommit(True)

cursor = db.cursor()

search = "abcdefghijklmnopqrstuvwxyz1234567890"
url = "https://gameinfo.albiononline.com/api/gameinfo/search?q="

## ---------------------- FUNCTIONS --------------------------------------------

# Generic functions
def converttimetoint(timestamp):
  split = timestamp.split(".")
  return int(time.mktime(datetime.datetime.strptime(split[0], "%Y-%m-%dT%H:%M:%S").timetuple()))

def nulltostr(string):
  if string != "null" or string != "None":
    return string
  else:
    return ""

def curr_time():
  return int(time.time())

# Specific aw functions

def aw_guild_exists(guild_id):
  sql_guild_exists = "SELECT count(*) as count FROM guilds WHERE Id=%s"
  ret = cursor.execute( sql_guild_exists, guild_id )
  retval = cursor.fetchone()
  return retval['count']

def aw_guild_insert(guild_id):
  # Fetch data
  sql_insert_guild = "INSERT INTO guilds (Id,Name,Founded,FounderId,Logo,KillFame,DeathFame,gvg_attacks_won,gvg_attacks_lost,gvg_defense_won,gvg_defense_lost,gvgDeaths,gvgKills,kills,ratio,fame,deaths) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
  sql_insert_history = "INSERT INTO guilds_history (Id,Name,Founded,FounderId,Logo,KillFame,DeathFame,gvg_attacks_won,gvg_attacks_lost,gvg_defense_won,gvg_defense_lost,gvgDeaths,gvgKills,kills,ratio,fame,deaths,seen,closed) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
  guild_data = requests.get("https://gameinfo.albiononline.com/api/gameinfo/guilds/"+guild_id+"/data")
  guild_data = json.loads(guild_data.text)

  guild = guild_data['guild']
  overall = guild_data['overall']
  gvg = guild_data['overall']['gvg']

  # Prep incoming data
  guild['Founded'] = converttimetoint(guild['Founded'])
  guild['Logo'] = nulltostr(guild['Logo'])

  # Insert new guild
  ret = cursor.execute( sql_insert_guild, ( guild['Id'], guild['Name'], guild['Founded'], guild['FounderId'], guild['Logo'], guild['killFame'], guild['DeathFame'], gvg['attacks_won'], gvg['attacks_lost'], gvg['defense_won'], gvg['defense_lost'], overall['gvgDeaths'], overall['gvgKills'], overall['kills'], overall['ratio'], overall['fame'], overall['deaths'] ) )

  # Insert into the History
  ret = cursor.execute( sql_insert_history, ( guild['Id'], guild['Name'], guild['Founded'], guild['FounderId'], guild['Logo'], guild['killFame'], guild['DeathFame'], gvg['attacks_won'], gvg['attacks_lost'], gvg['defense_won'], gvg['defense_lost'], overall['gvgDeaths'], overall['gvgKills'], overall['kills'], overall['ratio'], overall['fame'], overall['deaths'], curr_time(), 0) )

def aw_guild_close(guild_id):
  sql_insert_history = "INSERT INTO guilds_history (Id,Name,Founded,FounderId,Logo,KillFame,DeathFame,gvg_attacks_won,gvg_attacks_lost,gvg_defense_won,gvg_defense_lost,gvgDeaths,gvgKills,kills,ratio,fame,deaths,seen,closed) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

  guild_data = requests.get("https://gameinfo.albiononline.com/api/gameinfo/guilds/"+guild_id+"/data")
  guild_data = json.loads(guild_data.text)

  guild = guild_data['guild']
  overall = guild_data['overall']
  gvg = guild_data['overall']['gvg']

  # Prep incoming data
  guild['Founded'] = converttimetoint(guild['Founded'])
  guild['Logo'] = nulltostr(guild['Logo'])

  ret = cursor.execute( sql_insert_history, ( guild['Id'], guild['Name'], guild['Founded'], guild['FounderId'], guild['Logo'], guild['killFame'], guild['DeathFame'], gvg['attacks_won'], gvg['attacks_lost'], gvg['defense_won'], gvg['defense_lost'], overall['gvgDeaths'], overall['gvgKills'], overall['kills'], overall['ratio'], overall['fame'], overall['deaths'], curr_time(), 1) )

  sql_insert_close = "UPDATE guilds SET closed=1 WHERE Id=%s"
  ret = cursor.execute( sql_insert_close, guild['Id'] )

def aw_alliance_exists(alliance_id):
  sql_alliance_exists = "SELECT count(*) AS count FROM alliances WHERE Id=%s"
  ret = cursor.execute( sql_alliance_exists, alliance_id )
  retval = cursor.fetchone()
  return retval['count']

def aw_alliance_insert(guild):
  sql_insert_alliance = "INSERT INTO alliances (Id, Name, Tag, seen, closed) VALUES (%s, %s, %s, %s, %s)"
  sql_insert_history = "INSERT INTO alliances_history (Id, seen, guilds_id, mutation, closed ) VALUES (%s, %s, %s, %s, %s)"
  sql_insert_link = "INSERT INTO alliances_guilds (alliances_id, guilds_id) VALUES (%s, %s)"

  ret = cursor.execute( sql_insert_alliance, ( guild['AllianceId'], guild['AllianceName'], guild['AllianceTag'], curr_time(), 0 ) )
  ret = cursor.execute( sql_insert_link, ( guild['AllianceId'], guild['Id'] ) )
  ret = cursor.execute( sql_insert_history, ( guild['AllianceId'], curr_time(), guild['Id'], 1, 0 ) )

def aw_alliance_close(alliance):
  sql_insert_history = "INSERT INTO alliances_history (Id, seen, mutation, closed ) VALUES (%s, %s, %s, %s, %s)"
  ret = cursor.execute( sql_insert_history, ( guild['AllianceId'], curr_time(), 0, 1 ) )

def aw_players_insert(player):
  print(" - adding player: "+player['Name'])
  sql_player_insert = "INSERT INTO players ( Id, Name, Avatar, AvatarRing, AverageItemPower, KillFame, DeathFame, FameRatio ) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s)"
  sql_player_history = "INSERT INTO players_history ( Id, Name, Avatar, AvatarRing, AverageItemPower, KillFame, DeathFame, FameRatio, seen, guild) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )"
  if len(player['Inventory']) == 0:
    player['Inventory'] = "Null"
  ret = cursor.execute( sql_player_insert, ( player['Id'], (player['Name']), player['Avatar'], player['AvatarRing'], player['AverageItemPower'], player['KillFame'], player['DeathFame'], player['FameRatio'] ))
  ret = cursor.execute( sql_player_history, ( player['Id'], player['Name'], player['Avatar'], player['AvatarRing'], player['AverageItemPower'], player['KillFame'], player['DeathFame'], player['FameRatio'], curr_time(), player['GuildId']) )



## -----------------------------------------------------------------------------

for x in range(0,(len(search)-1)):
  for y in range(0,len(search)):
    print(url+search[x]+search[y])

req = requests.get("https://gameinfo.albiononline.com/api/gameinfo/search?q=b")
req_json = json.loads(req.text)

for guild in req_json['guilds']:
  guild_id = guild['Id']
  guild_data = albion.get_guild_data(guild_id)
  if aw_guild_exists(guild_id) == 0:
    print("Guild "+guild['Name']+" doesn't exist.\nAdding to the database.")
    aw_guild_insert(guild_id)
    # Check if Alliance exists
    if guild['AllianceId'] != "":
      print("Alliance found Checking")
      if aw_alliance_exists(guild['AllianceId']) == 0:
        # Insert Alliance
        aw_alliance_insert(guild_data['guild'])
    # Insert Members
    player_data = requests.get("https://gameinfo.albiononline.com/api/gameinfo/guilds/"+guild_id+"/members")
    player_data = json.loads(player_data.text)
    if len(player_data) != 0:
      print(str(len(player_data))+" members in guild. Adding: ")
      for player in player_data:
        aw_players_insert(player)
    else:
      print("No members. Closing guild.")
      aw_guild_close(guild_id)
  else:
    print("Guild "+guild['Name']+" exists.\nSkipping.")

# api:search
# Per guild
  # Check if exists ( guildID )
  # Get Guild Data - get_guild_data()
  # Get Guild stats - get_guild_stats()
  # Get Guild members - get_guild_members()
  # Do player stuff
  # Check ALliance exists
  # Do ALliance stuff
  # Add guild ot ALliance
# Per player
  # check if exists
  # get player info get_player_info()
  # get player topkills
  # get player solokills
# Per Alliance
  # Get data present
