SCRIPT_NAME = "rb_online"
SCRIPT_AUTHOR = "Bernard McKeever <dregin@gmail.com>"
SCRIPT_VERSION = "1.5"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC = "Colour nicks in #lobby depending on whether the user is logged into redbrick or not"

rb_online_settings = {
	"color_nick_online"			: "green",
	"color_nick_offline"		: "darkgray"
}
import re
import os
import time
import_ok = True

PRINT_CMD = "rbusers"
cmd_buffer = ""

users_rb_dict = {}
users_logged_in = {}

buff_ptr = "NULL"
nick_ptr = "NULL"

first_run = 1

# online_list = []
# offline_list = []

online_dict = {}
offline_dict = {}

outgoing_list = []
incoming_list = []

try:
	import weechat
except:
	print "This script must be run under Weechat"
	print "Get weechat @ http://www.weechat.org"
	import_ok = False

def pop_outgoing(data, remaining_calls):
	weechat.prnt('', 'OUTgoing callback called at %s' % time.time())
	global outgoing_list
	global offline_dict
	global online_dict

	if (outgoing_list):
		rnick  = outgoing_list.pop()
		offline_dict[rnick] = ""
		if (rnick in online_dict):
			del online_dict[rnick]
	return weechat.WEECHAT_RC_OK

def pop_incoming(data, remaining_calls):
	weechat.prnt('', 'INcoming callback called at %s' % time.time())			
	global incoming_list
	global offline_dict
	global online_dict

	if (incoming_list):
		rnick = incoming_list.pop()
		online_dict[rnick] = ""			#	Moving from incoming to online
		if rnick in offline_dict:
		#	weechat.prnt("", "REMOVING %s from offline_list" % rnick)
			del offline_dict[rnick]
	return weechat.WEECHAT_RC_OK

def set_colors(users_logged_in):
	global first_run

	global online_dict
	global offline_dict
	global outgoing_list
	global incoming_list

	nicks = weechat.infolist_get('irc_nick', '', 'redbrick,#lobby')
	buff_ptr = weechat.buffer_search("irc","redbrick.#lobby")
	if (nicks == "" and buff_ptr == ""):
		nicks = weechat.infolist_get('irc_nick', '', 'irc.redbrick.dcu.ie,#lobby')
		buff_ptr = weechat.buffer_search("irc","irc.redbrick.dcu.ie.#lobby")

	group_normal_ptr = weechat.nicklist_search_group(buff_ptr, "", "08|normal")
	group_op_ptr = weechat.nicklist_search_group(buff_ptr, "", "04|op")
	color_nick_online = weechat.config_get_plugin("color_nick_online")
	if nicks != None:
		if nicks == {}:
			weechat.prnt("No nicks")
		else:
			while weechat.infolist_next(nicks):											# Stepping through each nick in #lobby
				name = weechat.infolist_string(nicks, 'name')
				host = weechat.infolist_string(nicks, 'host')
				flag = weechat.infolist_integer(nicks, 'flags')
				if ("@Redbrick.dcu.ie" in host):
					rnick = re.sub('@Redbrick.dcu.ie', '', host)						# Strip real nick from host
					nick_ptr = weechat.nicklist_search_nick(buff_ptr, "", name)         # Find nick pointer

					#
					# - Incoming/Outgoing lists won't be populated if at least one iteration of the list hasn't happened.
					#		first_run set false at the end of first iteration
					# - Set outgoing if - user is offline, user WAS online on the last iter, user is not currently outgoing
					# - Set incoming if - user is online, user was NOT online on the last iter, user is not currently incoming 
					#

					# If NOT already logged in NOT first run WAS online on last loop NOT in outgoing list 

					if( not rnick in users_logged_in and not first_run and rnick in online_dict and rnick not in outgoing_list ):
						# weechat.prnt("", "OUTgoing user - %s" % rnick)
						outgoing_list.insert(0, rnick)
						weechat.hook_timer(10 * 1000, 0, 1, "pop_outgoing", "")				# TODO - This hook executes pop_outgoing immediately instead of waiting 10 seconds
						color = "yellow"
						if rnick in online_dict:
							del online_dict[rnick]

					# If IS logged in NOT first run IN nicklist WAS offline on last loop NOT in incoming list

					elif( rnick in users_logged_in and not first_run and rnick in offline_dict and rnick not in incoming_list ):
						# weechat.prnt("", "INcoming user - %s" % rnick)
						incoming_list.insert(0, rnick)
						weechat.hook_timer(10 * 1000, 0, 1, "pop_incoming", "")				# TODO - This hook executes pop_incoming immediately instead of waiting 10 seconds
						color = "red"														# Color incoming users red
						if( rnick in offline_dict ):
							del offline_dict[rnick]

					elif( rnick in incoming_list ): color = "red"

					elif( rnick in outgoing_list ): color = "yellow"

					# Check to see if that user is logged
					elif( rnick in users_logged_in):
						if (rnick in offline_dict):
							del offline_dict[rnick]
						online_dict[rnick] = ""
						color = "lightgreen"												# Color online users green

					else:
						offline_dict[rnick] = ""
						if (rnick in online_dict):
							del online_dict[rnick]
						color = "darkgray"

					# Adding nicks with relevant colours back into the nicklist

					if(buff_ptr and nick_ptr):
						# TODO - Decide whether or not this REMOVE should be moved...
						weechat.nicklist_remove_nick(buff_ptr, nick_ptr)
					if(buff_ptr):															# The nick may already have been removed from the buffer....
						if ( flag == 0 ):													# Check if normal user
							weechat.nicklist_add_nick(buff_ptr, group_normal_ptr, name, weechat.color(color), " ", color, 1)
						elif ( flag == 8 ):													# Check if ops (include @ prefix) 
							weechat.nicklist_add_nick(buff_ptr, group_op_ptr, name, weechat.color(color), "@", color, 1)
	first_run = 0
	users_rb_dict.clear()
	weechat.infolist_free(nicks)
	return weechat.WEECHAT_RC_OK
	
def users_online():
	# Return dictionary of names of users logged into the same server as the current user via SSH
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
	return users_rb_dict			# users_online is a dictionary

def update_nicklist(data, remaining_calls):
	# TODO - main function.... shouldn't this actually be part of the "main" function? oh well. Fix later.
	users_logged_in = users_online()		# Get a dictionary of all users logged into the same redbrick server as the current user
	set_colors(users_logged_in)	
	return weechat.WEECHAT_RC_OK

if __name__ == "__main__" and import_ok:
	if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", ""):
		# set default settings
		for option, default_value in rb_online_settings.iteritems():
			if not weechat.config_is_set_plugin(option):
				weechat.config_set_plugin(option, default_value)
		weechat.hook_timer(1000, 0, 0, "update_nicklist", "")
