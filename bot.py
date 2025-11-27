# bot.py
import discord
import traceback

from discord import abc, Thread, ForumChannel
from discord.ext import commands

from admins_ids import ADMIN_IDS
from config import PREFIX, DISCORD_TOKEN, INTENTS
from help_texts import GENERAL_HELP, COMMAND_HELP
from data_utils import DATA, ensure_guild, ensure_section, save_data

bot = commands.Bot(command_prefix=PREFIX, intents=INTENTS, help_command=None)


# -----------------------
# Utility
# -----------------------
def is_admin():
    async def predicate(ctx):
        if ctx.author.id in ADMIN_IDS.values():
            return True
        else:
            await ctx.send(f"User with ID `{ctx.author.id}` is not in my admin list. Ask admin to add you to the list to use the command.")
            return False
    return commands.check(predicate)


# -----------------------
# Сommands
# -----------------------
@is_admin()
@bot.command(name="addkeyword", aliases=["ak"])
async def addkeyword(ctx, section_name: str, *, keyword: str):
    guild_conf = ensure_guild(ctx.guild.id)
    section = ensure_section(guild_conf, section_name)
    keywords = keyword.strip().lower().split()

    added_keywords = []
    for k in keywords:
        if k in section["keywords"]:
            await ctx.send(f"The keyword `{k}` is already in the list of section `{section_name}`.")
            continue
        else:
            section["keywords"].append(k)
            added_keywords.append(k)
    if added_keywords:
        save_data(DATA)
        added_keywords_str = ", ".join(f"`{x}`" for x in added_keywords)
        await ctx.send(f"Added keyword(s) to section `{section_name}`: {added_keywords_str}")



    # if kw in section["keywords"]:
    #     await ctx.send(f"The keyword `{kw}` is already in the list of section `{section_name}`.")
    #     return
    # section["keywords"].append(kw)
    # save_data(DATA)
    # await ctx.send(f"Added keyword: `{kw}` to section `{section_name}`")

@is_admin()
@bot.command(name="remkeyword", aliases=["rk"])
async def remkeyword(ctx, section_name: str, *, keyword: str):
    guild_conf = ensure_guild(ctx.guild.id)
    section = ensure_section(guild_conf, section_name)
    kw = keyword.strip().lower()
    if kw not in section["keywords"]:
        await ctx.send(f"The keyword `{kw}` is not in the list of section `{section_name}`.")
        return
    section["keywords"].remove(kw)
    save_data(DATA)
    await ctx.send(f"Removed keyword: `{kw}` from section `{section_name}`")

@bot.command(name="listkeywords", aliases=["lk"])
async def listkeywords(ctx, section_name: str):
    guild_conf = ensure_guild(ctx.guild.id)
    section = ensure_section(guild_conf, section_name)
    kws = section["keywords"]
    if not kws:
        await ctx.send(f"The keyword list in section `{section_name}` is empty.")
        return
    await ctx.send(f"Keywords in section `{section_name}`: " + ", ".join(f"`{k}`" for k in kws))

@is_admin()
@bot.command(name="addforward", aliases=["af"])
async def addforward(ctx, section_name: str, source: abc.GuildChannel | discord.Thread, destination: abc.GuildChannel | discord.Thread):

    guild_conf = ensure_guild(ctx.guild.id)
    section = ensure_section(guild_conf, section_name)
    sid = str(source.id)
    did = str(destination.id)

    # Check if there is already source:destination pair with same value and index
    if sid in section["sources"] and did in section["destinations"]:
        for idx, x in enumerate(section["sources"]):
            if x == sid:
                if section["destinations"][idx] == did:
                    await ctx.send(
                        f"Error: Forwarding from {source.mention} to {destination.mention} already exists in section `{section_name}`.")
                    return

    #Check if source channel/thread exists, check for permissions
    channel = ctx.guild.get_channel_or_thread(source.id)
    if channel is None:
        await ctx.send(f"Error: Source channel/thread with id {source.id} is not found.")
        return
    bot_permissions = channel.permissions_for(ctx.guild.me)
    if isinstance(channel, Thread):
        if not (bot_permissions.read_message_history or bot_permissions.view_channel):
            await ctx.send(f"Error: I don't have permission to read messages in Source thread {channel.mention}.")
            return
    else:
        if not bot_permissions.read_messages:
            await ctx.send(f"Error: I don't have permission to read messages in Source channel {channel.mention}.")
            return
    if isinstance(channel, ForumChannel):
        await ctx.send(f"Error: Source should be a channel or thread, not a forum channel.")
        return

    #Check if destination channel/thread exists, check for permissions
    channel = ctx.guild.get_channel_or_thread(destination.id)
    if channel is None:
        await ctx.send(f"Error: Destination channel/thread with id {destination.id} is not found.")
        return
    bot_permissions = channel.permissions_for(ctx.guild.me)
    if isinstance(channel, Thread):
        if not bot_permissions.send_messages_in_threads:
            await ctx.send(f"Error: I can't send messages to Destination thread {channel.mention}.")
            return
    else:
        if not bot_permissions.send_messages:
            await ctx.send(f"Error: I don't have permission to send messages in Destination channel {channel.mention}.")
            return
    if isinstance(channel, ForumChannel):
        await ctx.send(f"Error: Destination should be a channel or thread, not a forum channel.")
        return

    # Everything is good, adding source:destination pair
    section["sources"].append(sid)
    section["destinations"].append(did)
    if len(section["sources"]) != len(section["destinations"]):
        await ctx.send("Error: Sources and destinations arrays have different lengths. Data was not saved.")
        return
    save_data(DATA)
    await ctx.send(f"Messages from {source.mention} will be forwarded to {destination.mention} in section `{section_name}`.")
    return


"""
Removes a forwarding rule from the given section.

If no destination is provided:
    – Finds the source in the parallel sources/destinations lists.
    – Removes the source and its corresponding destination.

If a destination is provided:
    – Removes the rule only if the source is forwarded to that specific destination.

Both lists must stay aligned (same length) after removal.
"""
@is_admin()
@bot.command(name="remforward", aliases=["rf"])
async def remforward(ctx, section_name: str, source: abc.GuildChannel | discord.Thread, destination: abc.GuildChannel=None | discord.Thread):
    guild_conf = ensure_guild(ctx.guild.id)
    section = ensure_section(guild_conf, section_name)
    sid = str(source.id)

    if sid not in section["sources"]:
        await ctx.send(f"Error: Source {source.mention} is not added in section `{section_name}`.")
        return

    is_data_changed = False
    if destination is None:
        i = 0
        while i < len(section["sources"]):
            if section["sources"][i] == sid:
                dest_removed = section["destinations"].pop(i)
                dest_removed_channel = ctx.guild.get_channel_or_thread(int(dest_removed))
                section["sources"].pop(i)
                is_data_changed = True
                await ctx.send(f"Forwarding from {source.mention} to {dest_removed_channel.mention} disabled in section `{section_name}`.")
            else:
                i += 1
        if is_data_changed:
            if len(section["sources"]) != len(section["destinations"]):
                await ctx.send("Error: Sources and destinations arrays have different lengths. Data was not saved.")
                return
            save_data(DATA)

    else:
        did = str(destination.id)
        i = 0
        while i < len(section["sources"]):
            if section["sources"][i] == sid:
                if section["destinations"][i] == did:
                    dest_removed = section["destinations"].pop(i)
                    dest_removed_channel = ctx.guild.get_channel_or_thread(int(dest_removed))
                    section["sources"].pop(i)
                    is_data_changed = True
                    await ctx.send(f"Forwarding from {source.mention} to {dest_removed_channel.mention} disabled in section `{section_name}`.")
                else:
                    i += 1
            else:
                i += 1
        if is_data_changed:
            if len(section["sources"]) != len(section["destinations"]):
                await ctx.send("Error: Sources and destinations arrays have different lengths. Data was not saved.")
                return
            save_data(DATA)
        else:
            await ctx.send(f"Forwarding from {source.mention} to {destination.mention} not found in section `{section_name}`.")

@bot.command(name="listforward", aliases=["lf"])
async def listforward(ctx, section_name: str):
    guild_conf = ensure_guild(ctx.guild.id)
    section = ensure_section(guild_conf, section_name)

    if not section["sources"] or not section["destinations"]:
        await ctx.send("Forward list is empty.")
        return

    forward_list_message = f"Forward list for section `{section_name}`:"
    for idx, x in enumerate(section["sources"]):
        source_channel = ctx.guild.get_channel_or_thread(int(x))
        dest_id = section["destinations"][idx]
        destination_channel = ctx.guild.get_channel_or_thread(int(dest_id))
        forward_list_message += f"\nMessages from {source_channel.mention} are forwarding to {destination_channel.mention}"
    await ctx.send(forward_list_message)

@is_admin()
@bot.command(name="listsections", aliases=["ls"])
async def listsections(ctx):
    guild_conf = ensure_guild(ctx.guild.id)
    sections = guild_conf["sections"]
    if not sections:
        await ctx.send("Section list is empty.")
        return
    await ctx.send("Sections list: `" + "`, `".join(sections.keys()) + "`")

@is_admin()
@bot.command(name="remsection")
async def remsection(ctx, section_name: str):
    guild_conf = ensure_guild(ctx.guild.id)
    sections = guild_conf["sections"]
    if not sections:
        await ctx.send("Section list is empty.")
        return
    if section_name not in sections:
        await ctx.send(f"Section `{section_name}` does not exist.")
        return
    sections.pop(section_name)
    save_data(DATA)
    await ctx.send(f"Section `{section_name}` removed.")


# -----------------------
# Message monitoring logic
# -----------------------
@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if not message.guild:
        return

    if message.author is message.guild.me:
        return

    # Debug
    # print(f"Got message: {message.content}")

    guild_conf = ensure_guild(message.guild.id)
    for section_name, section in guild_conf.get("sections", {}).items():
        sid = str(message.channel.id)
        if sid not in section["sources"]:
            continue

        content = (message.content or "").lower()
        if not content:
            continue

        # Check for keyword match
        matched = False
        for kw in section["keywords"]:
            if kw and kw in content:
                matched = True
                break

        if not matched:
            continue

        # Forwarding message for all source:destination pairs
        for idx, x in enumerate(section["sources"]):
            if x == sid:
                dest_id = section["destinations"][idx]
                if dest_id:
                    dest = message.guild.get_channel_or_thread(int(dest_id))
                    if dest:
                        bot_permissions = dest.permissions_for(message.guild.me)

                        if isinstance(dest, Thread):
                            if not bot_permissions.send_messages_in_threads:
                                print(f"Error: I cannot send messages in Destination thread {dest.mention}.")
                                continue
                        else:
                            if not bot_permissions.send_messages:
                                print(f"Error: I don't have permission to send messages in Destination channel {dest.mention}.")
                                continue

                        jump_url = message.jump_url
                        forwarded = (
                            f"**Forwarded message**, link: {jump_url}\n"
                            f"Message: {message.content}"
                        )
                        try:
                            await dest.send(forwarded)
                            # Send attachments if any
                            for att in message.attachments:
                                await dest.send(att.url)
                        except Exception as e:
                            print("Error forwarding:", e)
                    else:
                        print(f"Error: Destination with id {dest_id} is not found.")
                        continue

# -----------------------
# Command error handling
# -----------------------
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Error: Incorrect command usage. Please check the arguments.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("Error: You do not have permission to run this command.")
    elif isinstance(error, commands.CheckFailure):
        return
    else:
        print(f"Command error: {error} \n{traceback.format_exception(error)}")
        await ctx.send(f"Command error: {error}")

# -----------------------
# Help command
# -----------------------
@bot.command(name="help")
async def help_command(ctx, *, cmd: str = None):
    """
    Show general help or specific command help.
    Usage:
      ?fw help               -> show general help
      ?fw help <command>     -> show help for a specific command
    """
    if cmd:
        cmd_lower = cmd.lower().strip()
        # Check if the command exists in COMMAND_HELP
        if cmd_lower in COMMAND_HELP:
            cmd_info = COMMAND_HELP.get(cmd_lower)
            help_text = cmd_info["help"]
            aliases = cmd_info.get("aliases")
            if aliases:
                alias_list = ", ".join(f"`{a}`" for a in aliases)
                help_text += f"\n**Aliases:** {alias_list}"
            await ctx.send(help_text)
        else:
            await ctx.send(f"No help found for command `{cmd}`. Showing general help:\n{GENERAL_HELP}")
    else:
        await ctx.send(GENERAL_HELP)


# -----------------------
# Bot startup
# -----------------------
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)