# bot.py
import discord
import traceback
import re

from discord import abc, Thread, ForumChannel
from discord.ext import commands

from admins_ids import ADMIN_IDS
from config import PREFIX, DISCORD_TOKEN, INTENTS, SEPARATOR_MODE
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

    # Check if flag "--exact" was received at the end of the command
    exact = False
    if keyword.endswith("--exact"):
        exact = True
        keyword = keyword.replace("--exact", "")
    elif "--" in keyword:
        raise commands.CommandError(
            "Error: Incorrect command usage. Please check optional arguments.\n"
            "`--exact` should be only at the end of the command.\n"
            "Correct example with argument: `?fw addkeyword <section_name> <keyword> <keyword2> <keywordN> --exact`\n"
            "Correct example without argument: `?fw addkeyword <section_name> <keyword> <keyword2> <keywordN>`"
        )

    # Check if keywords are already in the lists and add them if not
    keywords = keyword.strip().lower().split()
    added_keywords = []
    for k in keywords:
        if k in section["keywords"]:
            await ctx.send(f"The keyword `{k}` is already in the list of section `{section_name}`.")
            continue
        elif k in section["exact_keywords"]:
            await ctx.send(f"The keyword `{k}` is already in the exact keywords list of section `{section_name}`.")
            continue
        else:
            if exact:
                section["exact_keywords"].append(k)
            else:
                section["keywords"].append(k)
            added_keywords.append(k)

    if added_keywords:
        save_data(DATA)
        added_keywords_str = ", ".join(f"`{x}`" for x in added_keywords)
        if exact:
            await ctx.send(f"Added keyword(s) to exact keywords list of section `{section_name}`: {added_keywords_str}")
        else:
            await ctx.send(f"Added keyword(s) to section `{section_name}`: {added_keywords_str}")

@is_admin()
@bot.command(name="remkeyword", aliases=["rk"])
async def remkeyword(ctx, section_name: str, *, keyword: str):
    guild_conf = ensure_guild(ctx.guild.id)
    section = ensure_section(guild_conf, section_name)
    keywords = keyword.strip().lower().split()

    removed_keywords = []
    exact_removed_keywords = []
    for k in keywords:
        keyword_in_list = False
        if k in section["keywords"]:
            section["keywords"].remove(k)
            removed_keywords.append(k)
            keyword_in_list = True
        if k in section["exact_keywords"]:
            section["exact_keywords"].remove(k)
            exact_removed_keywords.append(k)
            keyword_in_list = True
        if not keyword_in_list:
            await ctx.send(f"The keyword `{k}` is not in the list and not in the exact keywords list of section `{section_name}`.")

    if removed_keywords or exact_removed_keywords:
        save_data(DATA)
        msg_to_send = ""
        if removed_keywords:
            msg_to_send = f"Removed keyword(s) from section `{section_name}`: " + ", ".join(f"`{k}`" for k in removed_keywords)
        if exact_removed_keywords:
            if msg_to_send:
                msg_to_send += "\n"
            msg_to_send += f"Removed keyword(s) from exact keywords list of section `{section_name}`: " + ", ".join(f"`{k}`" for k in exact_removed_keywords)
        await ctx.send(msg_to_send)

@bot.command(name="listkeywords", aliases=["lk"])
async def listkeywords(ctx, section_name: str):
    guild_conf = ensure_guild(ctx.guild.id)
    section = ensure_section(guild_conf, section_name)
    keywords = section["keywords"]
    exact_keywords = section["exact_keywords"]

    if keywords or exact_keywords:
        msg_to_send = ""
        if keywords:
            msg_to_send = f"Keywords list in section `{section_name}`: " + ", ".join(f"`{k}`" for k in keywords)
        if exact_keywords:
            if msg_to_send:
                msg_to_send += "\n"
            msg_to_send += f"Exact keywords list in section `{section_name}`: " + ", ".join(f"`{k}`" for k in exact_keywords)
        await ctx.send(msg_to_send)
    else:
        await ctx.send(f"The keyword and exact keyword lists in section `{section_name}` are empty.")

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
                    raise commands.CommandError(
                        f"Error: Forwarding from {source.mention} to {destination.mention} already exists in section `{section_name}`."
                    )

    #Check if source channel/thread exists, check for permissions
    channel = ctx.guild.get_channel_or_thread(source.id)
    if channel is None:
        raise commands.CommandError(f"Error: Source channel/thread with id {source.id} is not found.")
    bot_permissions = channel.permissions_for(ctx.guild.me)
    if isinstance(channel, Thread):
        if not (bot_permissions.read_message_history or bot_permissions.view_channel):
            raise commands.CommandError(f"Error: I don't have permission to read messages in Source thread {channel.mention}.")
    else:
        if not bot_permissions.read_messages:
            raise commands.CommandError(f"Error: I don't have permission to read messages in Source channel {channel.mention}.")
    if isinstance(channel, ForumChannel):
        raise commands.CommandError(f"Error: Source should be a channel or thread, not a forum channel.")

    #Check if destination channel/thread exists, check for permissions
    channel = ctx.guild.get_channel_or_thread(destination.id)
    if channel is None:
        raise commands.CommandError(f"Error: Destination channel/thread with id {destination.id} is not found.")
    bot_permissions = channel.permissions_for(ctx.guild.me)
    if isinstance(channel, Thread):
        if not bot_permissions.send_messages_in_threads:
            raise commands.CommandError(f"Error: I can't send messages to Destination thread {channel.mention}.")
    else:
        if not bot_permissions.send_messages:
            raise commands.CommandError(f"Error: I don't have permission to send messages in Destination channel {channel.mention}.")
    if isinstance(channel, ForumChannel):
        raise commands.CommandError(f"Error: Destination should be a channel or thread, not a forum channel.")

    # Everything is good, adding source:destination pair
    section["sources"].append(sid)
    section["destinations"].append(did)
    if len(section["sources"]) != len(section["destinations"]):
        raise commands.CommandError("Error: Sources and destinations arrays have different lengths. Data was not saved.")
    save_data(DATA)
    await ctx.send(f"Messages from {source.mention} will be forwarded to {destination.mention} in section `{section_name}`.")


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
        raise commands.CommandError(f"Error: Source {source.mention} is not added in section `{section_name}`.")

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
                raise commands.CommandError("Error: Sources and destinations arrays have different lengths. Data was not saved.")
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
                raise commands.CommandError("Error: Sources and destinations arrays have different lengths. Data was not saved.")
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

async def if_matched(section, content):
    # Check for exact keyword match
    matched = ""
    separator_mode_triggered = False
    if SEPARATOR_MODE and content.count("\n") > 0:
        content = content.split("\n")
        separator_mode_triggered = True
    for kw in section["exact_keywords"]:
        if kw:
            regex_pattern = r"\b{kw}\b".format(kw=kw)
            regex = re.compile(regex_pattern)

            if separator_mode_triggered:
                for line in content:
                    if regex.search(line):
                        matched += line + "\n"
            else:
                if regex.search(content):
                    matched = content
                    break

    # Check for not exact (not strict) keyword match
    for kw in section["keywords"]:
        if separator_mode_triggered:
            for line in content:
                if kw and kw in line:
                    matched += line + "\n"
        else:
            if kw and kw in content:
                matched = content
                break

    return matched

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

        matched_str = await if_matched(section, content)
        if not matched_str:
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
                            f"Message: {matched_str}"
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
    print(f"Command error: {error} \n{traceback.format_exception(error)}")
    embed = discord.Embed(
        title="Command error",
        description=f"{error}",
        color=discord.Color.red()
    )

    if isinstance(error, commands.CommandInvokeError):
        error = error.original
    if isinstance(error, commands.MissingRequiredArgument):
        embed.description = f"```'{error.param.name}'``` is a required argument."
    elif isinstance(error, commands.CommandNotFound):
        embed.description = "```Command not found.```"
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("Error: You do not have permission to run this command.")
    elif isinstance(error, commands.CheckFailure):
        return

    await ctx.send(embed=embed)


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