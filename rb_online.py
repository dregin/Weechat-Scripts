SCRIPT_NAME = "rb_online"
SCRIPT_AUTHOR = "Bernard McKeever <dregin@gmail.com>"
SCRIPT_VERSION = "0.1"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC = "Colour nicks in #lobby depending on whether the user is logged into redbrick or not"

import os
import_ok = True
PRINT_CMD = "rbusers"

try:
	import weechat
except:
	print "This script must be run under Weechat"
	print "Get weechat @ http://www.weechat.org"
	import_ok = False

def lobby_users():
	print ""

def users_online():
	pipe = os.popen('users')
	pipeout = pipe.read()
	users_online = pipeout.split(" ")	# Splitting output of 'users' into a list:	
	pipe.close()				# Optimize list - remove duplicates? Performance?
	return users_online			# users_online is a list

def colour_nicks():
	return weechat.WEECHAT_RC_OK

def print_users(data, buffer, args):
	users = users_online()
	weechat.prnt("", "Users online: %s" % users)
	return weechat.WEECHAT_RC_OK

if __name__ == "__main__" and import_ok:
	if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", ""):
		weechat.hook_command("rbusers", "Print all Redbrick users logged in.", "", "", "", "print_users", "" )		
