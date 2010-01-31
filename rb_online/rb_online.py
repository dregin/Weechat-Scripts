SCRIPT_NAME = "rb_online"
SCRIPT_AUTHOR = "Bernard McKeever <dregin@gmail.com>"
SCRIPT_VERSION = "3.0-DEV"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC = """Colour nicks in #lobby depending on whether or not nick is logged into the same server as the user via SSH."""

#
#	online_color	-->		Colour for online user nicks		--> Default:	lightgreen
#	offline_color	-->		Colour for offline user nicks		--> Default:	darkgray
#	incoming_color	-->		Colour for incoming user nicks		-->	Default:	red
#	outgoing_color	-->		Colour for outgoing user nicks		-->	Default:	yellow
#	interim_period	-->		Timeout for interim statuses (incoming / outgoing)	-->Default: 10
# After loading this script, you can add item "hlpv" to your status
# bar with command:
#   /set weechat.bar.status.items [+tab]
#   then complete string by adding for example (without quotes): ",[rbon]"

import re
import os
import time
import_ok = True

users_logged_in = {}
users_rb_dict = {}

buff_ptr = "NULL"
nick_ptr = "NULL"

first_run = 1

online_dict = {}
offline_dict = {}

outgoing_list = []
incoming_list = []

rbon_messages = []

try:
	import weechat
except:
	print "This script must be run under Weechat"
	print "Get weechat @ http://www.weechat.org"
	import_ok = False

# Script Options
rbon_settings = {
		"online_color"		:	"lightgreen",
		"offline_color"		:	"darkgray",
		"incoming_color"	:	"red",
		"outgoing_color"	:	"yellow",
		"interim_period"	:	"10",
		"display_status"	:	"on"
		}
def pop_outgoing( data, remaining_calls ):
	# weechat.prnt('', 'OUTgoing callback called at %s' % time.time())
	global outgoing_list
	global offline_dict
	global online_dict
	global rbon_messages

	rbon_messages.pop(0)
	weechat.bar_item_update("rbon")

	if ( outgoing_list ):
		rnick  = outgoing_list.pop()					# User's colour can now be changed from yellow to dark gray
		offline_dict[rnick] = ""						# Add user to offline dictionary
		if (rnick in online_dict):						# Remove user from online dictionary if they are in it
			del online_dict[rnick]
	return weechat.WEECHAT_RC_OK

def pop_incoming( data, remaining_calls ):
	global incoming_list
	global offline_dict
	global online_dict
	global rbon_messages

	rbon_messages.pop(0)
	weechat.bar_item_update("rbon")

	if( incoming_list ):
		rnick = incoming_list.pop()						# User's colour can now be changed from red to green
		online_dict[rnick] = ""							# Add user to online dictionary
		if( rnick in offline_dict ):					# Remove user from offline dictionary if they are in it
			del offline_dict[rnick]
	return weechat.WEECHAT_RC_OK

def set_colors( users_logged_in ):
	global rbon_messages								# Variable to hold contents of rbon bar item
	global first_run									# Script needs one run to populate online and offline dictionaries

	global online_dict
	global offline_dict
	global outgoing_list
	global incoming_list

	nicks = weechat.infolist_get( 'irc_nick', '', 'redbrick,#lobby' )
	buff_ptr = weechat.buffer_search( "irc","redbrick.#lobby" )
	if( nicks == "" and buff_ptr == "" ):
		nicks = weechat.infolist_get( 'irc_nick', '', 'irc.redbrick.dcu.ie,#lobby' )
		buff_ptr = weechat.buffer_search( "irc","irc.redbrick.dcu.ie.#lobby" )

	group_normal_ptr = weechat.nicklist_search_group( buff_ptr, "", "08|normal" )
	group_op_ptr = weechat.nicklist_search_group( buff_ptr, "", "04|op" )
	color_nick_online = weechat.config_get_plugin( "color_nick_online" )
	if( nicks != None ):
		if( nicks == {} ):
			weechat.prnt( "No nicks" )
		else:
			while weechat.infolist_next( nicks ):										# Stepping through each nick in #lobby
				name = weechat.infolist_string(nicks, 'name')
				host = weechat.infolist_string(nicks, 'host')
				flag = weechat.infolist_integer(nicks, 'flags')
				timeout = weechat.config_get_plugin("interim_period")
				if( "@Redbrick.dcu.ie" in host ):
					rnick = re.sub('@Redbrick.dcu.ie', '', host)						# Strip real nick from host
					nick_ptr = weechat.nicklist_search_nick(buff_ptr, "", name)         # Find nick pointer

					#
					# - Incoming/Outgoing lists won't be populated if at least one iteration of the list hasn't happened.
					#		first_run set false at the end of first iteration
					# - Set outgoing if - user is offline, user WAS online on the last iteration, user is not currently outgoing
					# - Set incoming if - user is online, user was NOT online on the last iteration, user is not currently incoming 
					#

					#
					# - Script uses stacks
					#		When user moves into a state they are pushed onto the stack
					#		After a set time hook_timer's callback pops the user off the stack and they are moved into either offline or online dictionary
					#

					# If NOT already logged in NOT first run WAS online on last loop NOT in outgoing list 

					if( not rnick in users_logged_in and not first_run and rnick in online_dict and rnick not in outgoing_list ):
						# weechat.prnt("", "OUTgoing user - %s" % rnick)
						outgoing_list.insert(0, rnick)
						weechat.hook_timer(timeout * 1000, 0, 1, "pop_outgoing", "")				# TODO - This hook executes pop_outgoing immediately instead of waiting 10 seconds
						color = weechat.config_get_plugin( "outgoing_color" )
						# TODO - Add OUTGOING nick to rbon_messages here to be displayed in the rbon bar item
						rbon_nick_color = weechat.color( color )
						string = "%s%s" % ( rbon_nick_color,name )

						rbon_messages.append( string )
						weechat.bar_item_update( "rbon" )

						if( rnick in online_dict ):
							del online_dict[ rnick ]

					# If IS logged in NOT first run IN nicklist WAS offline on last loop NOT in incoming list

					elif( rnick in users_logged_in and not first_run and rnick in offline_dict and rnick not in incoming_list ):
						# weechat.prnt("", "INcoming user - %s" % rnick)
						incoming_list.insert(0, rnick)
						weechat.hook_timer(timeout * 1000, 0, 1, "pop_incoming", "")				# TODO - This hook executes pop_incoming immediately instead of waiting 10 seconds
						color = weechat.config_get_plugin("incoming_color")												# Color incoming users red
						# TODO - Add INCOMING nick to rbon_messages here to be displayed in the rbon bar item
						rb_nick_color = weechat.color( color )	
						string = "%s%s" % ( rb_nick_color, name )
						
						rbon_messages.append( string )
						weechat.bar_item_update( "rbon" )

						if( rnick in offline_dict ):
							del offline_dict[rnick]

					elif( rnick in incoming_list ): color = weechat.config_get_plugin( "incoming_color" )

					elif( rnick in outgoing_list ): color = weechat.config_get_plugin( "outgoing_color" )

					# Check to see if that user is logged
					elif( rnick in users_logged_in ):
						if( rnick in offline_dict ):
							del offline_dict[rnick]
						online_dict[rnick] = ""
						color = weechat.config_get_plugin( "online_color" )												# Color online user user nicks

					else:
						offline_dict[rnick] = ""
						if( rnick in online_dict ):
							del online_dict[rnick]
						color = weechat.config_get_plugin( "offline_color" )											# Colour offline user nicks

					# Adding nicks with relevant colours back into the nicklist

					if( buff_ptr and nick_ptr ):
						# TODO - Decide whether or not this REMOVE should be moved...
						weechat.nicklist_remove_nick(buff_ptr, nick_ptr)
					if( buff_ptr ):															# The nick may already have been removed from the buffer....
						if( flag == 0 ):													# Check if normal user
							weechat.nicklist_add_nick(buff_ptr, group_normal_ptr, name, weechat.color(color), " ", color, 1)
						elif( flag == 8 ):													# Check if ops (include @ prefix) 
							weechat.nicklist_add_nick(buff_ptr, group_op_ptr, name, weechat.color(color), "@", color, 1)
	first_run = 0
	users_rb_dict.clear()
	weechat.infolist_free( nicks )
	return weechat.WEECHAT_RC_OK
	
def users_online():
	# Return dictionary of names of users logged into the same server as the current user via SSH
	value = 0
	pipe = os.popen( 'users' )
	pipeout = pipe.read()	
	for item in pipeout.split():
		key = item
		if users_rb_dict.get( key ):
			users_rb_dict[ key ] += int( value )
		else:
			users_rb_dict[ key ] = int( value )
	pipe.close()
	return users_rb_dict			# users_online is a dictionary

def update_nicklist( data, remaining_calls ):
	# TODO - main function.... shouldn't this actually be part of the "main" function? oh well. Fix later.
	users_logged_in = users_online()		# Get a dictionary of all users logged into the same redbrick server as the current user
	set_colors(users_logged_in)	
	return weechat.WEECHAT_RC_OK

def rbon_item_cb( data, buffer, args ):
	"""Callback for building rbon item."""
	global rbon_messages
	# string = ''.join(rbon_messages, ', ')
	if len( rbon_messages ) > 0:
		# return rbon_messages[0]
		# return string
		return ', '.join(rbon_messages)
	return ""

if( __name__ == "__main__" and import_ok ):
	if( weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", "") ):
		# set default settings
		for option, default_value in rbon_settings.iteritems():
			if not weechat.config_is_set_plugin( option ):
				weechat.config_set_plugin( option, default_value )

		# Create the bar item to alert the user when others log on / off
		weechat.bar_item_new( 'rbon', 'rbon_item_cb', '')

		# check for users logging on / off
		weechat.hook_timer(1000, 0, 0, "update_nicklist", "")
