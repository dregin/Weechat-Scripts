import_ok = True
try:
        import weechat
except ImportError:
        print('This script must be run under WeeChat.')
        print('Get WeeChat now at: http://www.weechat.org/')
        import_ok = False

SCRIPT_NAME = 'replace_ignore'
SCRIPT_AUTHOR = 'Bernard McKeever <dregin@gmail.com>'
SCRIPT_VERSION = '1.0'
SCRIPT_LICENSE = 'GPL3'
SCRIPT_DESC = "Instead of completely ignoring a user's comments, replace them with ..." 

# Default settings for the plugin.
settings = {
    'check_every': '5'
}

def handle_message_cb( data, buffer, date, tags, disp, hl, nick, message ):
    print "data: %s buffer: %s date: %s tags: %s disp: %s hl: %s nick: %s message: %s" %(data, buffer, date, tags, disp, hl, nick, message)
    return weechat.WEECHAT_RC_OK


if __name__ == '__main__' and import_ok:
    if( weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", "") ):
        for option, default_value in settings.iteritems():
            if not weechat.config_is_set_plugin( option ):
                weechat.config_set_plugin( option, default_value )

        # Hook to process incoming messages
        weechat.hook_print('', '', '', 1, 'handle_message_cb', '')
