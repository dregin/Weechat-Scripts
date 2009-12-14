SCRIPT_NAME = "RB Online"
SCRIPT_AUTHOR = "Bernard McKeever <dregin@gmail.com>"
SCRIPT_VERSION = "0.1"
SCRIPT_LICENSE = "GLP3"
SCRIPT_DESC = "Colour nicks in #lobby depending on whether the user is logged into redbrick or not"

import os
import_ok = true
try:
	import weechat
except:
	print "This script must be run under Weechat"
	print "Get weechat @ http://www.weechat.org"
	import_ok = false

def lobby_users():

def users_online():

def colour_nicks():

if __name__ == "__main__" and import_ok:
	if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", ""):
		
