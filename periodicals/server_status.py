#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import pymysql.cursors
import configparser
import os
import json
import time
import re


# Load the config by finding it first...
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
  # Because 2 spaces are better than one tab
db.autocommit(True)

cursor = db.cursor()

sql_insert_status = "INSERT INTO serverstatus (last_seen,status,message) VALUES (%s,%s,%s)"
sql_select_status = "SELECT * FROM serverstatus ORDER BY last_seen DESC LIMIT 1"

url = "http://live.albiononline.com/status.txt"
error = 0
reasons = []

try:
  r = requests.get(url, timeout=5)
except:
  error = 1
  reasons.append("Error")

if r.ok != True:
  error = 1
  reasons.append("Status code is more than 400.")
if r.reason != "OK":
  error = 1
  reasons.append("Reason: "+str(r.reason))
if r.status_code != 200:
  error = 1
  reasons.append("Status code: "+r.status_code)

if error==0:
  # I need to do this because the API is weird.
  myContent = str(r.text)
  myContent = myContent.replace("\n"," ")
  myContent = myContent.replace("\r","")
  m = re.search( '{.*}', myContent )
  myContent = m.group(0)

  status_json = json.loads(myContent)
  status_status = status_json['status']
  status_message = status_json['message']
else:
  status_status = "Error"
  status_message = ""
  for reason in reasons:
    status_message = status_message + reason + " "

print(str(int(time.time())))
print(status_status)
print(status_message)

ret = cursor.execute( sql_select_status )
retval = cursor.fetchone()

if retval['status'] != status_status or retval['message'] != status_message:
  ret = cursor.execute( sql_insert_status, (str(int(time.time())), status_status, status_message) )
  db.commit()
