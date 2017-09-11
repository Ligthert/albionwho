#!/usr/bin/env python3

from albion_api_client import AlbionAPI
import albionwho as aw
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
# Main body
#
# Please note: this is a crude and API hammering approach. If it sees a guild:
#  Add it and all its players. See a player with a guild? Dito.
#
## -----------------------------------------------------------------------------

for x in range(0,(len(search))):
  for y in range(0,len(search)):
    search_key = search[x]+search[y]
    print("Importing from: "+url+search_key)

    req = requests.get(url+search[x])
    req_json = json.loads(req.text)

    for guild in req_json['guilds']:
      aw.guild_import(guild['Id'])
    for player in req_json['players']:
      if aw.player_exists(player['Id']) == 1:
        print("Player "+player['Name']+" exist. Skipping.")
      else:
        if player['GuildId'] == "":
          aw.players_insert(player)
        else:
          aw.guild_import(player['GuildId'])
