SCRIPT_NAME = "split_squash"
SCRIPT_AUTHOR = "Bernard McKeever <dregin@gmail.com>"
SCRIPT_VERSION = "0.1"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC = "Squash netsplit channel spam into one line detailing the number of splits and the server they were connected to."

import re
import os
import_ok = True
pattern = '([^.]+\.)+[^ ]+ ([^.]+\.)+[^.]+'		# Two addresses with a space between them (Freenode netsplit pattern)
splits = []

try:
    import weechat
except:
	print "This script must be run under Weechat"
	print "Get weechat @ http://www.weechat.org"
	import_ok = False

def strip_print(data, modifier, modifier_data, string):
	# Find what type of message was printed
	# Return empty sting if it was a message in a channel buffer i.e. a netsplit
	tags = modifier_data.split(";")
	if "notify_message" in tags[2]:
		return ""
	else:
		return string

def quit_event(data, signal, signal_data):
	if (check_split(signal_data)):
		weechat.prnt("", "Netsplit? YES - %s" % signal_data)
		strip_string = signal_data
			# Create functions to:
			# Add user/host details to a dictionary to wait for their return
			# Stop the line from appearing in the channel's buffer
			# Count total number of splits
			# Print number of splits and the affected host to the channel's buffer
	else:
		weechat.prnt("", "Netsplit? NO - %s" % signal_data)
		#strip_string = signal_data
		# Check for user/host returning from a split (details will be contained in the dictionary)
		# TODO - Move the following hook so that it only blocks QUITS when they are net splits
	print_hook = weechat.hook_modifier("weechat_print", "strip_print", "")        # Replace string printed to buffer with "" <--- HACKY	
	return weechat.WEECHAT_RC_OK

def join_event():
	# This will check if the joining user is returning from a netsplit
	# Check for nick in dict of recently split users
	return weechat.WEECHAT_RC_OK

def check_split( signal_data ):
	# Check whether the quit is a net split or not
	# TODO - create stricter regexp
	if re.search(pattern, signal_data):
		host = weechat.infolist_string(signal_data, 'host')
		splits.append(signal_data)
		return True
	else:
		return False

if __name__ == "__main__" and import_ok:
	# Hook quit messages
	if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", ""):
		weechat.prnt("", "YEOW!")
		hook = weechat.hook_signal("*,irc_in_quit", "quit_event", "")
