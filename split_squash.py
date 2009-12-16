SCRIPT_NAME = "Split_Squish"
SCRIPT_AUTHOR = "Bernard McKeever <dregin@gmail.com>"
SCRIPT_VERSION = "0.1"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC = "Squash netsplit channel spam into one line detailing the number of splits and the server they were connected to."

import os
import_ok = True

try:
        import weechat
except:
        print "This script must be run under Weechat"
        print "Get weechat @ http://www.weechat.org"
        import_ok = False

# weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", "")
weechat.hook_signal("*,irc_in_quit", "check_split", "")

def check_split(data, signal, signal_data):
	weechat.prnt("", signal_data)
	weechat.prnt("", "User just quit")
        return weechat.WEECHAT_RC_OK     

if __name__ == "__main__" and import_ok:
	if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", ""):
		weechat.prnt("", "YEOW!")
		hook = weechat.hook_signal("*,irc_in_quit", "check_split", "")
