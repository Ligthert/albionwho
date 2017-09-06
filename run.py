#!/usr/bin/env python3
from app import app
import os
import configparser

# Find the configuration file and load it in
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)
config = configparser.ConfigParser()
config.read('config.ini')

# Fire off Flask
app.run( debug=config['server']['debug'], host=config['server']['ipaddress'], port=int(config['server']['port']))
