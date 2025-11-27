# help_texts.py
"""
This module contains help texts for the Discord Forward Bot commands.
These texts are used for ?fw help and ?fw <command> help.
"""

GENERAL_HELP = """
**Discord Forward Bot Commands**
`?fw addkeyword <section_name> <keyword>`
Add a new keyword to trigger forwarding for specific section. **(Bot Admin Only)**
Multiple keywords are allowed to be added at once. Space character is used as a separator.
Optional argument `--exact` **at the end of the command** will make the keyword to be matched exactly.
Aliases: `ak`
    
`?fw remkeyword <section_name> <keyword>`
Remove a keyword from specific section. **(Bot Admin Only)**
Multiple keywords are allowed to be removed at once. Space character is used as a separator.
Aliases: `rk`
    
`?fw listkeywords <section_name>`
List all keywords for specific section.
Aliases: `lk`
    
`?fw addforward <section_name> #<channel_source> #<channel_destination>`
Set forwarding destination channel for a source channel for specific section. **(Bot Admin Only)**
Aliases: `af`

`?fw remforward <section_name> #<channel_source> #<channel_destination>`
Remove forwarding from source channel to destination channel. **(Bot Admin Only)**
If destination is not provided → disable forwarding for all destinations for specific source.
Aliases: `rf`

`?fw listforward <section_name>`
List all forwarding source:destination pairs for specific section.
Aliases: `lf`
    
`?fw listsections`
List all sections. **(Bot Admin Only)**
Aliases: `ls`
    
`?fw remsection <section_name>`
Will remove an entire section. **Be careful! (Bot Admin Only)**
    
`?fw help` — Shows this message.

`?fw help <command>` — Shows help for specific command.

"""

COMMAND_HELP = {
    "addkeyword": {
        "help":
            "`?fw addkeyword <section_name> <keyword>` — Add a new keyword for specific section. **(Bot Admin Only)**\n"
                      "Example: `?fw addkeyword org1 urgent`\n"
                      "Now all messages containing the keyword `urgent` will be forwarded for section `org1`\n"
                      "(in case if addforward already configured).\n"
                      "Multiple keywords are allowed to be added at once. Space character is used as a separator.\n"
                      "Example: `?fw addkeyword org1 urgent base tow`\n"
                      "Now all messages containing the keywords `urgent`, `base` and `tow` will be forwarded for section `org1`\n"
                      "Optional argument `--exact` **at the end of the command** will make the keyword to be matched exactly.\n"
                      "Example: `?fw addkeyword org1 tow --exact`\n"
                      "Now all messages containing the keyword `tow` will be forwarded for section `org1` exactly. Words contains `towel` will not be forwarded",
        "aliases": ["ak"]
    },

    "remkeyword": {
        "help":
            "`?fw remkeyword <section_name> <keyword>` — Remove an existing keyword from specific section. **(Bot Admin Only)**\n"
                  "Example: `?fw remkeyword org1 help`\n"
                  "Now all messages containing the keyword `help` will no longer be forwarded for section `org1`\n"
                  "Multiple keywords are allowed to be removed at once. Space character is used as a separator.\n"
                  "Example: `?fw remkeyword org1 help base tow`\n"
                  "Now all messages containing the keywords `help`, `base` and `tow` will no longer be forwarded for section `org1`",
        "aliases": ["rk"]
    },

    "listkeywords": {
        "help":
            "`?fw listkeywords <section_name>` — Show all keywords for specific section.\n"
                  "Example: `?fw listkeywords org1`",
        "aliases": ["lk"]
    },

    "addforward": {
        "help":
            "`?fw addforward <section_name> #<channel_source> #<channel_destination>` — Set a forwarding destination for specific section. **(Bot Admin Only)**\n"
                  "Example: `?fw addforward org1 #general #forwarded`\n"
                  "Now all messages from channel `#general` will be forwarded to channel `#forwarded` for section `org1`.\n"
                  "(in case if addkeyword already configured)\n"
                  "If destination is not provided → disable forwarding\n"
                  "Example: `?fw addforward org1 #general`",
        "aliases": ["af"]
    },

    "remforward": {
        "help":
            "`?fw remforward <section_name> #<channel_source> #<channel_destination>` — Remove forwarding from source channel to destination channel. **(Bot Admin Only)** \n"
            "If destination is not provided → disable forwarding for all destinations for specific source.\n"
                  "Example: `?fw remforward org1 #general #forwarded`\n"
                  "Now all messages from channel `#general` will not be forwarded to channel `#forwarded` anymore for section `org1`.\n"
                  "Example: `?fw remforward org1 #general`\n"
                  "Now all messages from channel `#general` will not be forwarded to any channels for section `org1`.",
        "aliases": ["rf"]
    },

    "listforward": {
        "help":
            "`?fw listforward` — List all forwarding source:destination pairs for specific section. **(Bot Admin Only)**\n" 
                  "Example: `?fw listforward <section_name>`",
        "aliases": ["lf"]
    },

    "listsections": {
        "help":
            "`?fw listsections` — List all sections. **(Bot Admin Only)**\n" 
                  "Example: `?fw listsections`",
        "aliases": ["ls"]
    },

    "remsection": {
        "help":
            "`?fw remsection` — Will remove an entire section. **Be careful! (Bot Admin Only)**\n" 
                  "Example: `?fw remsection org1`\n"
                  "Now section `org1` was removed."
    }
}
