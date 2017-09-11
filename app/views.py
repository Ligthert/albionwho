from flask import render_template, url_for, redirect, request, send_from_directory
from flask_cache import Cache
from app import app
import os
import time
import datetime
import pymysql.cursors
import configparser

from albion_api_client import AlbionAPI
import albionwho as aw

dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)
os.chdir('..')
config = configparser.ConfigParser()
config.read('config.ini')

# Connect to the MySQL Server using the data in the configfile
db = pymysql.connect(host=config['database']['hostname'],
  user=config['database']['username'],
  password=config['database']['password'],
  db=config['database']['database'],
  cursorclass=pymysql.cursors.DictCursor)
db.autocommit(True)
cursor = db.cursor()

# Kick in caching
cache = Cache(app)
# TODO: spam--> @cache.cached(timeout=config['cache']['timeout'])

@app.route('/')
@app.route('/search')
def page_root():
  content = render_template("search.html")
  active = {'search':True}
  return render_template("template.html", content=content, active=active)

@app.route('/search/<string:query>')
def page_search(query):
  content = render_template("search.html")

  players_local = aw.search_players_local(query)
  players_remote = aw.search_players_remote(query)
  players = aw.search_merge_lists( players_local, players_remote )

  guilds_local = aw.search_guilds_local(query)
  guilds_remote = aw.search_guilds_remote(query)
  guilds = aw.search_merge_lists( guilds_local, guilds_remote )

  alliances = aw.search_alliances_local(query)

  content = content + render_template("search_results.html", players=players, guilds=guilds, alliances=alliances)
  active = {'search':True}
  return render_template("template.html", content=content, active=active)

@app.route('/players')
def page_players():
  content = "player"
  active = {'players':True}
  return render_template("template.html", content=content, active=active)

@app.route('/player/<string:player>')
def page_player(player):
  content = render_template("player.html", player=player)
  active = {'players':True}
  return render_template("template.html", content=content, active=active)

@app.route('/guilds')
def page_guilds():
  active = {'guilds':True}
  return render_template("template.html", content='Hello Worldie! :D', active=active)

@app.route('/guild/<string:guild>')
def page_guild():
  active = {'guilds':True}
  return render_template("template.html", content='Hello Worldie! :D', active=active)

@app.route('/alliances')
def page_alliances():
  active = {'alliances':True}
  return render_template("template.html", content='Hello Worldie! :D', active=active)

@app.route('/alliance/<string:alliance>')
def page_alliance():
  active = {'alliances':True}
  return render_template("template.html", content='Hello Worldie! :D', active=active)

@app.route('/status')
def page_status():
  sql_last = "SELECT * FROM serverstatus ORDER BY last_seen DESC LIMIT 1"
  sql_history = "SELECT * FROM serverstatus ORDER BY last_seen DESC LIMIT 10"

  cursor.execute( sql_last )
  status = cursor.fetchone()

  helper = {}
  if status['status'] == "online":
    helper['green'] = True
    helper['red'] = False
  else:
    helper['green'] = False
    helper['red'] = True

  ret = cursor.execute( sql_history )
  history = cursor.fetchall()

  counter = 0
  for event in history:
    history[counter]['last_seen'] = datetime.datetime.fromtimestamp(event['last_seen']).strftime('%c')
    history[counter]['status'] = str(event['status']).title()
    counter = counter + 1

  status['status'] = str(status['status']).title()
  content = render_template("status.html", status=status, helper=helper, history=history)


  active = {'status':True}
  return render_template("template.html", content=content, active=active)

@app.route('/about')
def page_about():
  content = '<p>AlbionWho is written in Python 3 using Flask and the albion-api-client to gather publically information available about players, guilds and alliances. Due to the nature of Albion Online\'s public API the content of this side cannot be considered complete <small>(but I am trying my hardest to make sure it is!)</small> and with the things one can do with the data available nor will this be feature complete </small>(there are so many things I would like to do)</small>.</p><p>Things still on the todo/wishlist:</p><ul><li>Import GvG</li><li>Import kills</li><li>Graphs of captured metrics</li><li>Find relationships between players and or guilds based on captured data</li><li>Write a long forum post on how the API can be improved</li><li>Prevent Albion Online API from blacklisting my server boxes.</li></ul><p>As an EVE Online player Albion Online resonated with me when I started playing. While there are a lot of similarities, Albion Online lacks a long history of 3rd Party tools to assist the players in achieving bragging rights and help Alliance and Guild leaders and recruits to make an informed decisions about potential recruits and existing members... That and I needed a new hobby. ;)</p><hr><p>The following scripts run at the following times:<ul><li>Server status updater: every minute</li><li>Alliance/Guild/Player updater: every 6 hours</li><li>Background Alliance/Guild/Player adder: T.B.D.</li></ul></p>'
  active = {'about':True}
  return render_template("template.html", content=content, active=active)

@app.route( '/search_form', methods=['POST'] )
def page_searchform():
  query = request.form['query']
  return redirect("/search/"+query)

@app.route('/static/<path:path>')
def send_file(path):
  return send_from_directory('static', path)
