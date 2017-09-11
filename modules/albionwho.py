from albion_api_client import AlbionAPI
import configparser
import requests
import pymysql.cursors
import json
import datetime
import time
import os

albion = AlbionAPI()

# Preptime
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)
os.chdir('..')
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

# Generic methods
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

# AlbionWho specific methods

## -------------- Guilds -----------------------------

def guild_import(guild_id):
  guild = albion.get_guild_info(guild_id)
  guild_data = albion.get_guild_data(guild_id)
  if guild_exists(guild_id) == 0:
    print("Guild "+guild['Name']+" doesn't exist.\nAdding to the database.")
    guild_insert(guild_id)
    # Check if Alliance exists
    if guild['AllianceId'] != "":
      print("Alliance found Checking")
      if alliance_exists(guild['AllianceId']) == 0:
        # Insert Alliance
        alliance_insert(guild_data['guild'])
    # Insert Members
    player_data = albion.get_guild_members(guild_id)
    if len(player_data) != 0:
      print(str(len(player_data))+" members in guild. Adding: ")
      for player in player_data:
        if player_exists(player['Id']) == 1:
          print("Player "+player['Name']+" exist. Skipping.")
        else:
          players_insert(player)
    else:
      print("No members. Closing guild.")
      guild_close(guild_id)
  else:
    print("Guild "+guild['Name']+" exists.\nSkipping.")

def guild_get(guild_id):
  ret = cursor.execute("SELECT * FROM guilds WHERE Id=%s", (guild_id) )
  return cursor.fetchone()

def guild_exists(guild_id):
  sql_guild_exists = "SELECT count(*) as count FROM guilds WHERE Id=%s"
  ret = cursor.execute( sql_guild_exists, guild_id )
  retval = cursor.fetchone()
  return retval['count']

def guild_insert(guild_id):
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

def guild_close(guild_id):
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

def guild_get_alliance(guild_id):
  ret = cursor.execute( "SELECT alliances_id FROM alliances_guilds WHERE guilds_id = %s", (guilds_id) )
  return cursor.fetchone()

def guild_remove_alliance( guild_id, closed):
  alliance = guild_get_alliance(guilds_id)
  sql_alliances_history = "INSERT INTO alliances_history ( Id, seen, guild_id, mutation, closed) VALUES ( %s, %s, -1, %s )"
  ret = cursor.execute( sql_alliances_history, ( alliance['alliances_id'], curr_time(), guild_id, closed) )

  sql_alliance_rel = "DELETE FROM alliances_guilds WHERE alliance_id = %s and guilds_id = %s"
  ret = cursor.execute( sql_alliance_rel, (alliance['alliances_id'], guild_id) )

## -------------- Alliances -----------------------------

def alliance_exists(alliance_id):
  sql_alliance_exists = "SELECT count(*) AS count FROM alliances WHERE Id=%s"
  ret = cursor.execute( sql_alliance_exists, alliance_id )
  retval = cursor.fetchone()
  return retval['count']

def alliance_insert(guild):
  print("Adding Alliance: "+guild['AllianceName']+" ["+guild['AllianceTag']+"]")
  sql_insert_alliance = "INSERT INTO alliances (Id, Name, Tag, seen, closed) VALUES (%s, %s, %s, %s, %s)"
  sql_insert_history = "INSERT INTO alliances_history (Id, seen, guilds_id, mutation, closed ) VALUES (%s, %s, %s, %s, %s)"
  sql_insert_link = "INSERT INTO alliances_guilds (alliances_id, guilds_id) VALUES (%s, %s)"

  ret = cursor.execute( sql_insert_alliance, ( guild['AllianceId'], guild['AllianceName'], guild['AllianceTag'], curr_time(), 0 ) )
  ret = cursor.execute( sql_insert_link, ( guild['AllianceId'], guild['Id'] ) )
  ret = cursor.execute( sql_insert_history, ( guild['AllianceId'], curr_time(), guild['Id'], 1, 0 ) )

def alliance_close(alliance):
  sql_insert_history = "INSERT INTO alliances_history (Id, seen, mutation, closed ) VALUES (%s, %s, %s, %s, %s)"
  ret = cursor.execute( sql_insert_history, ( guild['AllianceId'], curr_time(), 0, 1 ) )

## -------------- Players -----------------------------

def player_get(player_id):
  ret = cursor.execute( "SELECT * FROM players WHERE Id=%s", (player_id) )
  return cursor.fetchone()

def players_get_all():
  ret = cursor.execute( "SELECT * FROM players")
  return cursor.fetchall()

def player_exists(player_id):
  sql_player_exists = "SELECT count(*) as count FROM players WHERE Id=%s"
  ret = cursor.execute( sql_player_exists, player_id )
  retval = cursor.fetchone()
  return retval['count']

def players_insert(player):
  print(" - adding player: "+player['Name'])
  player = albion.get_player_info(player['Id'])
  sql_player_insert = "INSERT INTO players ( Id, Name, Avatar, AvatarRing, AverageItemPower, KillFame, DeathFame, FameRatio ) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s)"
  sql_player_history = "INSERT INTO players_history ( Id, Name, Avatar, AvatarRing, AverageItemPower, KillFame, DeathFame, FameRatio, seen, guild) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )"
  sql_player_guild = "INSERT INTO guilds_players (guilds_Id,players_Id) VALUES (%s,%s)"


  if len(player['Inventory']) == 0:
    player['Inventory'] = "Null"

  ret = cursor.execute( sql_player_insert, ( player['Id'], (player['Name']), player['Avatar'], player['AvatarRing'], player['AverageItemPower'], player['KillFame'], player['DeathFame'], player['FameRatio'] ))
  ret = cursor.execute( sql_player_history, ( player['Id'], player['Name'], player['Avatar'], player['AvatarRing'], player['AverageItemPower'], player['KillFame'], player['DeathFame'], player['FameRatio'], curr_time(), player['GuildId']) )

  if player['GuildId'] != "":
    ret = cursor.execute( sql_player_guild, ( player['GuildId'], player['Id'] ) )

def players_update(player):
  print(" - updating player: "+player['Name'])

## ---------------------- Search ---------------------------

def search_players_local(player_name):
  player_name = player_name+"%"
  sql_search_players = "SELECT Name FROM players WHERE Name LIKE %s"
  ret = cursor.execute( sql_search_players, (player_name) )
  players = []
  for player in cursor.fetchall():
    players.append( player['Name'] )
  return players

def search_players_remote(player_name):
  req = requests.get("https://gameinfo.albiononline.com/api/gameinfo/search?q="+player_name)
  results = json.loads(req.text)
  players = []
  if len(results['players']) != 0:
    for player in results['players']:
      players.append( player['Name'] )
  return players

def search_guilds_local(guild_name):
  guild_name = guild_name+"%"
  sql_search_guilds = "SELECT Name FROM guilds WHERE Name LIKE %s"
  ret = cursor.execute( sql_search_guilds, (guild_name) )
  guilds = []
  for guild in cursor.fetchall():
    guilds.append( guild['Name'] )
  return guilds

def search_guilds_remote(guild_name):
  req = requests.get("https://gameinfo.albiononline.com/api/gameinfo/search?q="+guild_name)
  results = json.loads(req.text)
  guilds = []
  if len(results['guilds']) != 0:
    for guild in results['guilds']:
      guilds.append( guild['Name'] )
  return guilds

def search_alliances_local(alliance_name):
  alliance_name = alliance_name+"%"
  sql_search_alliance = "SELECT Name FROM alliances WHERE Name like %s"
  ret = cursor.execute( sql_search_alliance, (alliance_name) )
  alliances = []
  for alliance in cursor.fetchall():
    alliances.append( alliance )
  return alliances

def search_merge_lists(db_local, db_remote):
  items = []
  for item in db_local:
    items.append( {'Name':item} )
  for item in db_local:
    # Dirty, but it works. If it breaks... No one will care.
    try:
      db_remote.remove( item )
    except:
      pass
  for item in db_remote:
    items.append( {'Name':item,'untracked':1} )
  return items


# ------------------------- Update specific stuff ----------------------

# Fetch all active guilds
def update_fetch_guilds():
  # No need to update closed guilds
  sql_fetch_guilds = "SELECT * FROM guilds WHERE closed = 0"
  ret = cursor.execute( sql_fetch_guilds )
  guilds = []
  for guild in cursor.fetchall():
    guilds.append( guild )
  return guilds

# TODO
def update_guild_stats(guild_basic, guild_base, guild_overall, guild_gvg):
  print("Do something")

# TODO
def update_guild_history(guild_basic, guild_base, guild_overall, guild_gvg):
  print("Basically a CC of update_guild_stats()")

# TODO
# Returns a list
def update_guild_get_players_local(guild_id):
  print("SELECT ALL 'n shit yo!'")

# TODO
# Returns a list
def update_guild_get_players_remote(guild_id):
  print("SELECT ALL 'n shit yo!'")
