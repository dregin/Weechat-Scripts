SCRIPT_NAME = "rb_online"
SCRIPT_AUTHOR = "Bernard McKeever <dregin@gmail.com>"
SCRIPT_VERSION = "1.0"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC = "Colour nicks in #lobby depending on whether the user is logged into redbrick or not"

rb_online_settings = {
	"color_nick_online"			: "green",
	"color_nick_offline"		: "darkgray"
}
import re
import os
import_ok = True
PRINT_CMD = "rbusers"
cmd_buffer = ""
intermin_period = 10
users_rb_dict = {}
nicks_status = {}
buff_ptr = "NULL"
nick_ptr = "NULL"
first_run = True

try:
	import weechat
except:
	print "This script must be run under Weechat"
	print "Get weechat @ http://www.weechat.org"
	import_ok = False

def what_color():
	return weechat.WEECHAT_RC_OK

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
	# Clear users_rb_dict
	# Loop again using timer

	# TO-DO keep track of current nick colors to save removing and re-adding nicks that don't need changing

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
					rnick = re.sub("@Redbrick.dcu.ie","",host)							# Strip real nick from host
					nick_ptr = weechat.nicklist_search_nick(buff_ptr, "", name)         # Find nick pointer

					if (rnick in users_logged_in):		# Check to see if that user is currently online
						online_list.append(rnick)
						color = "lightgreen"											# Color online users green

					#
					# - Lists won't be populated if at least one iteration of the list hasn't happened.
					#		first_run set false at the end of first iteration
					# - Set outgoing if - user is offline, user WAS online on the last iter, user is not currently outgoing
					# - Set incoming if - user is online, user was NOT online on the last iter, user is not currently incoming
					#

					elif ( !rnick in users_logged_in && !first_run && rnick in online_list && !rnick in outgoing_list ):
						outgoing_list.append(rnick)
						weechat.hook_timer(10000, 1, 0, pop_outgoing, "")		# Pop from end of outgoing_list statck --> Add to offline_list
						color = "orange"
					elif ( rnick in users_logged_in && !first_run && !rnick in online_list && !rnick in incoming_list)
						incoming_list.append(rnick)
						weechat.hook_timer(10000, 1, 0, pop_incoming, "")		# Pop from end of incoming_list stack --> Add to online_list
						color = "red"
					elif( rnick in offline_list):
						color = "darkgray"


					if(buff_ptr and nick_ptr):											# Add nick coloured either green or darkgray
						weechat.nicklist_remove_nick(buff_ptr, nick_ptr)
					if(buff_ptr):														# The nick may already have been removed from the buffer....
						if ( flag == 0 ):													# Check if normal user
							weechat.nicklist_add_nick(buff_ptr, group_normal_ptr, name, weechat.color(color), " ", color, 1)
						elif ( flag == 8 ):													# Check if ops (include @ prefix) 
							weechat.nicklist_add_nick(buff_ptr, group_op_ptr, name, weechat.color(color), "@", color, 1)
				nicks_status.append(rnick)
		first_run = False
		users_rb_dict.clear()
		# Add nick:status to a dictionary....
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
	# main function.... shouldn't this actually be part of the "main" function? oh well. Fix later.
	users_logged_in = users_online()# Get a dictionary of all users logged into the same redbrick server as the current user
	set_colors(users_logged_in)	
	return weechat.WEECHAT_RC_OK

if __name__ == "__main__" and import_ok:
	if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", ""):
		# set default settings
		for option, default_value in rb_online_settings.iteritems():
			if not weechat.config_is_set_plugin(option):
				weechat.config_set_plugin(option, default_value)
		weechat.hook_timer(1000, 0, 0, "update_nicklist", "")
