# help_texts.py
"""
This module contains help texts for the Discord Forward Bot commands.
These texts are used for ?fw help and ?fw <command> help.
"""

GENERAL_HELP = """
**Discord Forward Bot Commands**
`?fw addkeyword <section_name> <keyword>`
Add a new keyword to trigger forwarding for specific section. **(Bot Admin Only)**
Aliases: `akw`, `addkw`
    
`?fw remkeyword <section_name> <keyword>`
Remove a keyword from specific section. **(Bot Admin Only)**
Aliases: `rkw`, `remkw`
    
`?fw listkeywords <section_name>`
List all keywords for specific section.
Aliases: `lkw`, `lskw`
    
`?fw addsource <section_name> #<channel>`
Add a source channel to monitor for specific section. **(Bot Admin Only)**
Aliases: `as`, `addsrc`
    
`?fw remsource <section_name> #<channel>`
Remove a monitored channel from specific section. **(Bot Admin Only)**
Aliases: `rs`, `rmsrc`
    
`?fw setforward <section_name> #<channel_source> #<channel_destination>`
Set forwarding destination channel for a source channel for specific section. **(Bot Admin Only)**
If destination not provided → disable forwarding
Aliases: `sf`, `setfw`
    
`?fw listsections`
List all sections. **(Bot Admin Only)**
Aliases: `lsec`
    
`?fw remsection <section_name>`
Remove a section. **(Bot Admin Only)**
Aliases: `rsec`, `remsec`
    
`?fw help` — Shows this message.

`?fw help <command>` — Shows help for specific command.

"""

COMMAND_HELP = {
    "addkeyword": {
        "help":
            "`?fw addkeyword <section_name> <keyword>` — Add a new keyword for specific section. **(Bot Admin Only)**\n"
                      "Example: `?fw addkeyword org1 urgent`\n"
                      "Now all messages containing the keyword `urgent` will be forwarded for section `org1`\n"
                      "(in case if addsource and setforward already configured).",
        "aliases": ["akw", "addkw"]
    },

    "remkeyword": {
        "help":
            "`?fw remkeyword <section_name> <keyword>` — Remove an existing keyword from specific section. **(Bot Admin Only)**\n"
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
            "`?fw addsource <section_name> #<channel>` — Add a source channel to monitor for specific section. **(Bot Admin Only)**\n"
                  "Example: `?fw addsource org1 #general`\n"
                  "Now all messages from channel `#general` will be monitored for section `org1`\n"
                  "And if `setforward` is configured, then all messages containing configured keyword will be forwarded to configured channel for section `org1`.",
        "aliases": ["as", "addsrc"]
    },

    "remsource": {
        "help":
            "`?fw remsource <section_name> #<channel>` — Remove a monitored channel from specific section. **(Bot Admin Only)**\n"
                  "Example: `?fw remsource org1 #general`\n"
                  "Now all messages from channel `#general` will no longer be monitored for section `org1`.",
        "aliases": ["rs", "rmsrc"]
    },

    "setforward": {
        "help":
            "`?fw setforward <section_name> #<channel_source> #<channel_destination>` — Set a forwarding destination for specific section. **(Bot Admin Only)**\n"
                  "Example: `?fw setforward org1 #general #forwarded`\n"
                  "Now all messages from channel `#general` will be forwarded to channel `#forwarded` for section `org1`.\n"
                  "(in case if addkeyword and addsource already configured)\n"
                  "If destination is not provided → disable forwarding\n"
                  "Example: `?fw setforward org1 #general`",
        "aliases": ["sf", "setfw"]
    },

    "listsections": {
        "help":
            "`?fw listsections` — List all sections. **(Bot Admin Only)**\n" 
                  "Example: `?fw listsections`",
        "aliases": ["lsec"]
    },

    "remsection": {
        "help":
            "`?fw remsection` — Remove a section. **(Bot Admin Only)**\n" 
                  "Example: `?fw remsection org1`\n"
                  "Now section `org1` was removed.",
        "aliases": ["rsec", "remsec"]
    }
}
