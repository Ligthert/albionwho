from flask import render_template, url_for, redirect, request, send_from_directory
from flask_cache import Cache
from app import app
import os
import time
import datetime
import pymysql.cursors
import configparser

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
def page_root():
  content = "Hello Worldie! :D"
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

  print(history)
  counter = 0
  for event in history:
    history[counter]['last_seen'] = datetime.datetime.fromtimestamp(event['last_seen']).strftime('%c')
    history[counter]['status'] = str(event['status']).title()
    counter = counter + 1

  status['status'] = str(status['status']).title()
  content = render_template("status.html", status=status, helper=helper, history=history)


  active = {'status':True}
  return render_template("template.html", content=content, active=active)

@app.route('/static/<path:path>')
def send_file(path):
  return send_from_directory('static', path)
