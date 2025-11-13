# help_texts.py
"""
This module contains help texts for the Discord Forward Bot commands.
These texts are used for ?fw help and ?fw <command> help.
"""

GENERAL_HELP = """
\n**Discord Forward Bot Commands**
`?fw addkeyword <section_name> <keyword>` — Add a new keyword to trigger forwarding for specific section.
    \t\t**Aliases:** `akw`, `addkw`
`?fw remkeyword <section_name> <keyword>` — Remove a keyword from specific section.
    \t\t**Aliases:** `rkw`, `remkw`
`?fw listkeywords <section_name>` — List all keywords for specific section.
    \t\t**Aliases:** `lkw`, `lskw`
`?fw addsource <section_name> #<channel>` — Add a source channel to monitor for specific section.
    \t\t**Aliases:** `as`, `addsrc`
`?fw remsource <section_name> #<channel>` — Remove a monitored channel from specific section.
    \t\t**Aliases:** `rs`, `rmsrc`
`?fw setforward <section_name> #<channel_source> #<channel_destination>` — Set forwarding destination channel for a source channel for specific section.
    \t\t**Aliases:** `sf`, `setfw`
`?fw setmode <section_name> <forward|dm|all>` — Set the forwarding mode for specific section.
    \t\t**Aliases:** `sm`, `setmd`
`?fw subscribe <section_name>` — Subscribe to DM alerts for keywords for specific section.
    \t\t**Aliases:** `sub`
`?fw unsubscribe <section_name>` — Unsubscribe from DM alerts from specific section.
    \t\t**Aliases:** `unsub`
`?fw listsubs <section_name>` — List all DM subscribers for specific section (admin only).
    \t\t**Aliases:** `ls`, `lsub`
`?fw help` — Shows this message.
`?fw help <command>` — Shows help for specific command.
"""

COMMAND_HELP = {
    "addkeyword": {
        "help":
            "`?fw addkeyword <section_name> <keyword>` — Add a new keyword for specific section.\n"
                      "Example: `?fw addkeyword org1 urgent`\n"
                      "Now all messages containing the keyword `urgent` will be forwarded for section `org1`\n"
                      "(in case if addsource and setforward already configured).",
        "aliases": ["akw", "addkw"]
    },

    "remkeyword": {
        "help":
            "`?fw remkeyword <section_name> <keyword>` — Remove an existing keyword from specific section.\n"
                  "Example: `?fw remkeyword org1 help`\n"
                  "Now all messages containing the keyword `help` will no longer be forwarded for section `org1`",
        "aliases": ["rkw", "remkw"]
    },

    "listkeywords": {
        "help":
            "`?fw listkeywords <section_name>` — Show all keywords for specific section.\n"
                  "Example: `?fw listkeywords org1`",
        "aliases": ["lkw", "lskw"]
    },

    "addsource": {
        "help":
            "`?fw addsource <section_name> #<channel>` — Add a source channel to monitor for specific section.\n"
                  "Example: `?fw addsource org1 #general`\n"
                  "Now all messages from channel `#general` will be monitored for section `org1`\n"
                  "And if `setforward` is configured, then all messages containing configured keyword will be forwarded to configured channel for section `org1`.",
        "aliases": ["as", "addsrc"]
    },

    "remsource": {
        "help":
            "`?fw remsource <section_name> #<channel>` — Remove a monitored channel from specific section.\n"
                  "Example: `?fw remsource org1 #general`\n"
                  "Now all messages from channel `#general` will no longer be monitored for section `org1`.",
        "aliases": ["rs", "rmsrc"]
    },

    "setforward": {
        "help":
            "`?fw setforward <section_name> #<channel_source> #<channel_destination>` — Set a forwarding destination for specific section.\n"
                  "Example: `?fw setforward org1 #general #forwarded`\n"
                  "Now all messages from channel `#general` will be forwarded to channel `#forwarded` for section `org1`.\n"
                  "(in case if addkeyword and addsource already configured)",
        "aliases": ["sf", "setfw"]
    },

    "setmode": {
        "help":
            "`?fw setmode <section_name> <forward|dm|all>` — Set the forwarding mode for specific section.\n"
                  "`forward` - (Default) forward messages to configured channel for section.\n"
                  "`dm` - send DM alerts to subscribers for section.\n"
                  "`all` - forward messages to configured channel and send DM alerts to subscribers for section.\n"
                  "Example: `?fw setmode org1 all`",
        "aliases": ["sm", "setmd"]
    },

    "subscribe": {
        "help":
            "`?fw subscribe <section_name>` — Subscribe user called the command to DM alerts for specific section.\n"
                  "Example: `?fw subscribe org1`",
        "aliases": ["sub"]
    },

    "unsubscribe": {
        "help":
            "`?fw unsubscribe <section_name>` — Unsubscribe user called the command from DM alerts from specific section.\n"
                  "Example: `?fw unsubscribe org1`",
        "aliases": ["unsub"]
    },

    "listsubs": {
        "help":
            "`?fw listsubs <section_name>` — List all DM subscribers for specific section (admin only).\n" 
                  "Example: `?fw listsubs org1 help`",
        "aliases": ["ls", "lsub"]
    }
}
