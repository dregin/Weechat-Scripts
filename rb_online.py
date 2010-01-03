SCRIPT_NAME = "rb_online"
SCRIPT_AUTHOR = "Bernard McKeever <dregin@gmail.com>"
SCRIPT_VERSION = "0.1"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC = "Colour nicks in #lobby depending on whether the user is logged into redbrick or not"

import os
import_ok = True
PRINT_CMD = "rbusers"
cmd_buffer = ""
my_dict = {}

try:
	import weechat
except:
	print "This script must be run under Weechat"
	print "Get weechat @ http://www.weechat.org"
	import_ok = False

def lobby_users():
	# Should return a list/dictionary of nick pointers and related ident nick
	nicks = weechat.infolist_get('irc_nick', '', 'redbrick,#lobby')
	if nicks != None:
		if nicks == {}:
			weechat.prnt("No nicks")
		else:
			while weechat.infolist_next(nicks):
				name = weechat.infolist_string(nicks, 'name')
				host = weechat.infolist_string(nicks, 'host')
				if ("@Redbrick.dcu.ie" in host):
					rnick = host.strip('@')
					weechat.prnt(cmd_buffer,"Nick: %s - Host: %s - Real Nick: %s" % (name, host, rnick))
				else:
					rnick = 'NOT A REDBRICK HOST'
					weechat.prnt(cmd_buffer,"Nick: %s - Host: %s - Real Nick:%s %s" % (name, host, weechat.color("red"), rnick))
		return weechat.WEECHAT_RC_OK

def users_online():
	# Return list of users online
	value = 0
	pipe = os.popen('users')
	pipeout = pipe.read()	
	for item in pipeout.split():
		key = item
		if my_dict.get( key ):
			my_dict[ key ] += int( value )
		else:
			my_dict[ key ] = int( value )
	pipe.close()				# Optimize list - remove duplicates? Performance?
	users_online = my_dict
	return users_online			# users_online is a list

def colour_nicks():
	# Remove nicks from nicklist in #lobby
	# Re-add nicks with color set to green
	return weechat.WEECHAT_RC_OK

def print_users(data, buffer, args):
	# Prints a list of users in #lobby
	users = users_online()
	cmd_buffer = buffer
	for name in users:
		weechat.prnt(cmd_buffer, "%s" % name)
	lobby_users()
	return weechat.WEECHAT_RC_OK

if __name__ == "__main__" and import_ok:
	if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", ""):
		weechat.hook_command("rbusers", "Print all Redbrick users logged in.", "", "", "", "print_users", "" )
