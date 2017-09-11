#!/usr/bin/env python3

import requests
import pymysql.cursors
import configparser
import os
import json
import time

from albion_api_client import AlbionAPI
import albionwho as aw
albion = AlbionAPI()

# Load the config by finding it first...
#dir_path = os.path.dirname(os.path.realpath(__file__))
#os.chdir(dir_path)
#os.chdir('..')
#print(os.getcwd())
config = configparser.ConfigParser()
config.read('config.ini')

# Connect to the MySQL Server using the data in the configfile
db = pymysql.connect(host=config['database']['hostname'],
  user=config['database']['username'],
  password=config['database']['password'],
  db=config['database']['database'],
  cursorclass=pymysql.cursors.DictCursor)
  # Because 2 spaces are better than one tab
db.autocommit(True)

cursor = db.cursor()

#Select all guilds not closed
guilds = aw.update_fetch_guilds()

#  if no players
for guild in guilds:
  # Get the latest of data from the API
  guild_data = albion.get_guild_data(guild['Id'])

  guild_basic = guild_data['basic']
  guild_base = guild_data['guild']
  guild_overall = guild_data['overall']
  guild_gvg = guild_data['overall']['gvg']

  if guild_basic['memberCount'] == 0:
    print("Guild "+guild['Name']+" has no members anymore. Closing.")
#    update alliance_guilds history
    aw.guild_remove_alliance(guild['Id'],1) # guild_remove_alliance( alliance_id, guild_id, closed)
#    close guild
    aw.guild_close(guild)
  else:
    print("Guild "+guild['Name']+" still has "+str(guild_basic['memberCount'])+" members.")
#    Update history
    update_guild_history(guild_basic, guild_base, guild_overall, guild_gvg)
#    Update guild
    update_guild_stats(guild_basic, guild_base, guild_overall, guild_gvg)
#    select members list
    guild_members_local = update_guild_get_players_local(guild['Id'])
    guild_members_remote = update_guild_get_players_remote(guild['Id'])
#    steal code from sgmon
#      find added members
    guild_members_added = []
    guild_members_removed = []
    for member in guild_members_local:
      # Dirty, but it works. If it breaks... No one will care.
      try:
        guild_members_remote.remove( member )
      except:
        guild_members_added.append( member )
      guild_members_removed = guild_members_remote

      for member in guild_members_added:
        print("TODO")
#        insert member if it doesn't exist
#        update member if it exists
#        update guilds_players

#      find removed members
      for member in guild_members_removed:
        print("TODO")
#        update player history
#        update guild history
#        update guilds_players
#        check for new guilds
#          if guild doesn't exist add it
          if guild_exists(guild_id) == 0:
            aw.guild_import(guild['Id'])

#  Check alliance
#  if alliance not the same
#    update guilds/alliance history
#
#Select all players
players = players_get_all()
#  Check for score updates
#    update players
#    update history
#  Check for guild updates
#    update players
#    update guild history
#    update guilds_players
