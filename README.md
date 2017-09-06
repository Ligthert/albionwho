# AlbionWho

## About
A collection of tools to collect, view and analyze data available via the public API of Albion Online. Site is running at http://albionwho.com.

## Requirements

1. Python v3.5+
1. Any recent MySQL version

( This was developed on Unix, might work on Windows? )

## Installation

1. Clone this repo to a suitable location
1. Install the required Python 3 modules ('pip install -r requirements.txt')
1. Create a database
1. Modify _config.ini_ to your needs
1. Prime the database by running _primer.py_
1. Schedule periodical executing of scripts in _periodicals/_
1. Start the application (`./run.py`)

Optionally you can:

+ To have the service managed by Upstart, place _albionwho.conf_ in _/etc/init/_ and start the service (`service albionwho start`).
+ Docker support is on its way (2lazy2fix)
+ Systemd support is on its way (2damned2fix)
