# help_texts.py
"""
This module contains help texts for the Discord Forward Bot commands.
These texts are used for ?fw help and ?fw <command> help.
"""

GENERAL_HELP = """
**Discord Forward Bot Commands**
`?fw addkeyword <section_name> <keyword>` — Add a new keyword to trigger forwarding for specific section.
`?fw remkeyword <section_name> <keyword>` — Remove a keyword from specific section.
`?fw listkeywords <section_name>` — List all keywords for specific section.
`?fw addsource <section_name> #<channel>` — Add a source channel to monitor for specific section.
`?fw remsource <section_name> #<channel>` — Remove a monitored channel from specific section.
`?fw setforward <section_name> #<channel_source> #<channel_destination>` — Set forwarding destination channel for a source channel for specific section.
`?fw setmode <section_name> <forward|dm|all>` — Set the forwarding mode for specific section.
`?fw subscribe <section_name>` — Subscribe to DM alerts for keywords for specific section.
`?fw unsubscribe <section_name>` — Unsubscribe from DM alerts from specific section.
`?fw listsubs <section_name>` — List all DM subscribers for specific section (admin only).
`?fw help` — Shows this message.
`?fw help <command>` — Shows help for specific command.
"""

COMMAND_HELP = {
    "addkeyword": "`?fw addkeyword <section_name> <keyword>` — Add a new keyword for specific section.\n"
                  "Example: `?fw addkeyword org1 urgent`\n"
                  "Now all messages containing the keyword `urgent` will be forwarded for section `org1`\n"
                  "(in case if addsource and setforward already configured).",

    "remkeyword": "`?fw remkeyword <section_name> <keyword>` — Remove an existing keyword from specific section.\n"
                  "Example: `?fw remkeyword org1 help`\n"
                  "Now all messages containing the keyword `help` will no longer be forwarded for section `org1`",

    "listkeywords": "`?fw listkeywords <section_name>` — Show all keywords for specific section.\n"
                  "Example: `?fw listkeywords org1`",

    "addsource": "`?fw addsource <section_name> #<channel>` — Add a source channel to monitor for specific section.\n"
                  "Example: `?fw addsource org1 #general`\n"
                  "Now all messages from channel `#general` will be monitored for section `org1`\n"
                  "And if `setforward` is configured, then all messages containing configured keyword will be forwarded to configured channel for section `org1`.",

    "remsource": "`?fw remsource <section_name> #<channel>` — Remove a monitored channel from specific section.\n"
                  "Example: `?fw remsource org1 #general`\n"
                  "Now all messages from channel `#general` will no longer be monitored for section `org1`.",

    "setforward": "`?fw setforward <section_name> #<channel_source> #<channel_destination>` — Set a forwarding destination for specific section.\n"
                  "Example: `?fw setforward org1 #general #forwarded`\n"
                  "Now all messages from channel `#general` will be forwarded to channel `#forwarded` for section `org1`.\n"
                  "(in case if addkeyword and addsource already configured)",

    "setmode": "`?fw setmode <section_name> <forward|dm|all>` — Set the forwarding mode for specific section.\n"
                  "`forward` - (Default) forward messages to configured channel for section.\n"
                  "`dm` - send DM alerts to subscribers for section.\n"
                  "`all` - forward messages to configured channel and send DM alerts to subscribers for section.\n"
                  "Example: `?fw setmode org1 all`",

    "subscribe": "`?fw subscribe <section_name>` — Subscribe user called the command to DM alerts for specific section.\n"
                  "Example: `?fw subscribe org1`",

    "unsubscribe": "`?fw unsubscribe <section_name>` — Unsubscribe user called the command from DM alerts from specific section.\n"
                  "Example: `?fw unsubscribe org1`",

    "listsubs": "`?fw listsubs <section_name>` — List all DM subscribers for specific section (admin only).\n" 
                  "Example: `?fw listsubs org1 help`",
}
