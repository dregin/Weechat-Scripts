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


def quit_event(data, signal, signal_data):
	if (check_split(signal_data)):
		weechat.prnt("", "Netsplit? YES - %s" % signal_data)
	else:
		weechat.prnt("", "Netsplit? NO - %s" % signal_data)
        return weechat.WEECHAT_RC_OK

def check_split( signal_data ):
	if re.search(pattern, signal_data):
		host = weechat.infolist_string(signal_data, 'host')
		splits.append(signal_data)
		return True
	else:
		return False

if __name__ == "__main__" and import_ok:
	if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", ""):
		weechat.prnt("", "YEOW!")
		hook = weechat.hook_signal("*,irc_in_quit", "quit_event", "")
