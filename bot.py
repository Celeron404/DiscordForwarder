# bot.py
import discord
import traceback
import re

from discord import abc, Thread, ForumChannel
from discord.ext import commands

from admins_ids import ADMIN_IDS
from config import PREFIX, DISCORD_TOKEN, INTENTS, SEPARATOR_MODE, INGAME_CHAT_NICK_REMOVER
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

def remove_chat_nickname(message: str):
    separator = ": "
    output_message = message.split(separator, 1)
    if len(output_message) < 2:
        return message
    return output_message[1]


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
    # Check if flag "--exclude" was received at the end of the command
    exclude = False
    if keyword.endswith("--exclude"):
        exclude = True
        keyword = keyword.replace("--exclude", "")
    elif "--" in keyword or exact and exclude:
        raise commands.CommandError(
            "Error: Incorrect command usage. Please check optional arguments.\n"
            "`--exact` or `--exclude` should be only at the end of the command.\n"
            "`--exact` and `--exclude` cannot be used at the same time.\n"
            "Correct example with argument: `?fw addkeyword <section_name> <keyword_sentence> --exact`\n"
            "or: `?fw addkeyword <section_name> <keyword_sentence> --exclude`\n"
            "Correct example without argument: `?fw addkeyword <section_name> <keyword_sentence>`"
        )

    # Check if a keyword is already in the lists and add them if not
    keyword = keyword.strip().lower()
    if "\"" in keyword or "\\" in keyword:
        await ctx.send("Error: Keyword cannot contain symbols `\"` or `\\`.")
        return
    if keyword in section["keywords"]:
        await ctx.send(f"The keyword ``{keyword}`` is already in the list of section `{section_name}`.")
        return
    if keyword in section["exact_keywords"]:
        await ctx.send(f"The keyword ``{keyword}`` is already in the exact keywords list of section `{section_name}`.")
        return
    if keyword in section["exclude_keywords"]:
        await ctx.send(f"The keyword ``{keyword}`` is already in the exclude keywords list of section `{section_name}`.")
        return

    if exact:
        section["exact_keywords"].append(keyword)
    elif exclude:
        section["exclude_keywords"].append(keyword)
    else:
        section["keywords"].append(keyword)

    save_data(DATA)
    if exact:
        await ctx.send(f"Added keyword to exact keywords list of section `{section_name}`: ``{keyword}``")
    elif exclude:
        await ctx.send(f"Added keyword to exclude keywords list of section `{section_name}`: ``{keyword}``")
    else:
        await ctx.send(f"Added keyword to section `{section_name}`: ``{keyword}``")

@is_admin()
@bot.command(name="remkeyword", aliases=["rk"])
async def remkeyword(ctx, section_name: str, *, keyword: str):
    guild_conf = ensure_guild(ctx.guild.id)
    section = ensure_section(guild_conf, section_name)
    keyword = keyword.strip().lower()

    keyword_in_keywords_list = False
    keyword_in_exact_keywords_list = False
    keyword_in_exclude_keywords_list = False
    if keyword in section["keywords"]:
        section["keywords"].remove(keyword)
        keyword_in_keywords_list = True
    if keyword in section["exact_keywords"]:
        section["exact_keywords"].remove(keyword)
        keyword_in_exact_keywords_list = True
    if keyword in section["exclude_keywords"]:
        section["exclude_keywords"].remove(keyword)
        keyword_in_exclude_keywords_list = True
    if not keyword_in_keywords_list and not keyword_in_exact_keywords_list and not keyword_in_exclude_keywords_list:
        await ctx.send(f"The keyword ``{keyword}`` is not in the keywords, exact keywords, and exclude keywords list of section `{section_name}`.")
    else:
        save_data(DATA)
        msg_to_send = ""
        if keyword_in_keywords_list:
            msg_to_send += f"Removed keyword from keywords list of section `{section_name}`: ``{keyword}``"
        if keyword_in_exact_keywords_list:
            if msg_to_send:
                msg_to_send += "\n"
            msg_to_send += f"Removed keyword from exact keywords list of section `{section_name}`: ``{keyword}``"
        if keyword_in_exclude_keywords_list:
            if msg_to_send:
                msg_to_send += "\n"
            msg_to_send += f"Removed keyword from exclude keywords list of section `{section_name}`: ``{keyword}``"
        await ctx.send(msg_to_send)

@bot.command(name="listkeywords", aliases=["lk"])
async def listkeywords(ctx, section_name: str):
    guild_conf = ensure_guild(ctx.guild.id)
    section = ensure_section(guild_conf, section_name)
    keywords = section["keywords"]
    exact_keywords = section["exact_keywords"]
    exclude_keywords = section["exclude_keywords"]

    if keywords or exact_keywords or exclude_keywords:
        msg_to_send = ""
        if keywords:
            msg_to_send = f"Keywords list in section `{section_name}`:\n\t" + "\n\t".join(f"``{k}``" for k in keywords)
        if exact_keywords:
            if msg_to_send:
                msg_to_send += "\n"
            msg_to_send += f"Exact keywords list in section `{section_name}`:\n\t" + "\n\t".join(f"``{k}``" for k in exact_keywords)
        if exclude_keywords:
            if msg_to_send:
                msg_to_send += "\n"
            msg_to_send += f"Exclude keywords list in section `{section_name}`:\n\t" + "\n\t".join(f"``{k}``" for k in exclude_keywords)
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

        if not source_channel and not destination_channel:
            forward_list_message += f"\nSource channel `{x}` and destination channel `{dest_id}` are not found. Forward list not working anymore for this pair.\n\tPlease remove the pair or fix the channel IDs, for example make a forum post active again."
            continue
        if not source_channel:
            forward_list_message += f"\nSource channel `{x}` is not found.\n\tForward list is not working anymore for pair: Source channel `{x}`, Destination channel `{dest_id}`.\n\tPlease remove the pair or fix the channel IDs, for example make a forum post active again."
            continue
        if not destination_channel:
            forward_list_message += f"\nDestination channel `{dest_id}` is not found.\n\tForward list is not working anymore for pair: Source channel `{x}`, Destination channel `{dest_id}`.\n\tPlease remove the pair or fix the channel IDs, for example make a forum post active again."
            continue
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

    if separator_mode_triggered:
        exclude_word_was_found = False
        for line in content:
            if INGAME_CHAT_NICK_REMOVER:
                if line.endswith(" disconnected**"):
                    continue
                line = remove_chat_nickname(line)

            for exclude_keyword in section["exclude_keywords"]:
                if exclude_keyword in line:
                    exclude_word_was_found = True
                    break
            if exclude_word_was_found:
                continue

            for kw in section["exact_keywords"]:
                if kw:
                    regex_pattern = r"(\s{kw}\s)|(\b{kw}\b)".format(kw=kw)
                    regex = re.compile(regex_pattern)
                    if regex.search(line):
                        matched += line + "\n"

            for kw in section["keywords"]:
                if kw and kw in line:
                    matched += line + "\n"

    else:
        if INGAME_CHAT_NICK_REMOVER:
            if content.endswith("disconnected**"):
                return ""
            content = remove_chat_nickname(content)

        for exclude_keyword in section["exclude_keywords"]:
            if exclude_keyword in content:
                return ""

        for kw in section["exact_keywords"]:
            if kw:
                regex_pattern = r"(\s{kw}\s)|(\b{kw}\b)".format(kw=kw)
                regex = re.compile(regex_pattern)
                if regex.search(content):
                    matched = content
                    break

        for kw in section["keywords"]:
            if kw and kw in content:
                matched = content
                break

    # for kw in section["exact_keywords"]:
    #     if kw:
    #         regex_pattern = r"(\s{kw}\s)|(\b{kw}\b)".format(kw=kw)
    #         regex = re.compile(regex_pattern)
    #
    #         if separator_mode_triggered:
    #             for line in content:
    #                 if INGAME_CHAT_NICK_REMOVER:
    #                     if line.endswith("disconnected**"):
    #                         continue
    #                     line = remove_chat_nickname(line)
    #
    #                 if regex.search(line):
    #                     matched += line + "\n"
    #         else:
    #             if INGAME_CHAT_NICK_REMOVER:
    #                 if content.endswith("disconnected**"):
    #                     continue
    #                 content = remove_chat_nickname(content)
    #
    #             if regex.search(content):
    #                 matched = content
    #                 break
    #
    # # Check for not exact (not strict) keyword match
    # for kw in section["keywords"]:
    #     if separator_mode_triggered:
    #         for line in content:
    #             if INGAME_CHAT_NICK_REMOVER:
    #                 if line.endswith("disconnected**"):
    #                     continue
    #                 line = remove_chat_nickname(line)
    #
    #             if kw and kw in line:
    #                 matched += line + "\n"
    #     else:
    #         if INGAME_CHAT_NICK_REMOVER:
    #             if content.endswith("disconnected**"):
    #                 continue
    #             content = remove_chat_nickname(content)
    #
    #         if kw and kw in content:
    #             matched = content
    #             break

    return matched

@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if not message.guild:
        return

    if message.author is message.guild.me:
        return

    ctx = await bot.get_context(message)
    if ctx.valid:
        print(f"Command triggered: {ctx.command.name} by {message.author}")
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