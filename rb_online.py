SCRIPT_NAME = "rb_online"
SCRIPT_AUTHOR = "Bernard McKeever <dregin@gmail.com>"
SCRIPT_VERSION = "0.1"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC = "Colour nicks in #lobby depending on whether the user is logged into redbrick or not"

import re
import os
import_ok = True
PRINT_CMD = "rbusers"
cmd_buffer = ""
users_rb_dict = {}
buff_ptr = "NULL"
nick_ptr = "NULL"

try:
	import weechat
except:
	print "This script must be run under Weechat"
	print "Get weechat @ http://www.weechat.org"
	import_ok = False

def set_colors(users_logged_in):
	# Compare real nicks in #lobby to those in users_rb_dict
		# if real nick exists in user_rb_dict
			# remove nick
			# color nick (online color)
			# re-add nick
		# else
			# remove nick
			# color nick (offline color)
			# re-add nick

	# TO-DO keep track of current nick colors to save removing and re-adding nicks that don't need changing

	nicks = weechat.infolist_get('irc_nick', '', 'redbrick,#lobby')
	buff_ptr = weechat.buffer_search("irc","redbrick.#lobby")
	if nicks != None:
		if nicks == {}:
			weechat.prnt("No nicks")
		else:
			while weechat.infolist_next(nicks):
				name = weechat.infolist_string(nicks, 'name')
				host = weechat.infolist_string(nicks, 'host')
				if ("@Redbrick.dcu.ie" in host):
					rnick = re.sub("@Redbrick.dcu.ie","",host)	# Strip real nick from host
					if (rnick in users_logged_in):				# Check to see if that user is currently online
						color = "green"							# Color online users green
						nick_ptr = weechat.nicklist_search_nick(buff_ptr, "", name)	# Find nick pointer
						if(buff_ptr and nick_ptr):
							weechat.prnt(cmd_buffer, "nick_ptr: %s buff_ptr: %s" % (nick_ptr, buff_ptr)) # DEBUG == Checking pointer values
							# weechat.nicklist_remove_nick(buff_ptr, nick_ptr)
							# weechat.nicklist_add_nick(buff_ptr, "", name, color, "", "", 1)
					else:
						color = ""
				else:
					rnick = 'NOT A REDBRICK HOST'
					color = 'red'
				weechat.prnt(cmd_buffer,"Nick: %s Host: %s\t Real Nick: %s %s" % (name, host, weechat.color(color), rnick))
		return weechat.WEECHAT_RC_OK

def users_online():
	# Return list of users online
	value = 0
	pipe = os.popen('users')
	pipeout = pipe.read()	
	for item in pipeout.split():
		key = item
		if users_rb_dict.get( key ):
			users_rb_dict[ key ] += int( value )
		else:
			users_rb_dict[ key ] = int( value )
	pipe.close()
	# users_online = users_rb_dict
	return users_rb_dict			# users_online is a dictionary

def print_users(data, buffer, args):
	# Prints a list of users in #lobby
	users = users_online()
	cmd_buffer = buffer
	for name in users:
		weechat.prnt(cmd_buffer, "%s" % name)
	# lobby_users()
	return weechat.WEECHAT_RC_OK

def update_colors(data, buffer, args):
	# main function.... shouldn't this actually be part of the "main" function? oh well. Fix later.
	users_logged_in = users_online()# Get a dictionary of all users logged into the same redbrick server as the current user
	set_colors(users_logged_in)	
	return weechat.WEECHAT_RC_OK

if __name__ == "__main__" and import_ok:
	if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", ""):
		weechat.hook_command("rbusers", "Print all Redbrick users logged in.", "", "", "", "update_colors", "" )
