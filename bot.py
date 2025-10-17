﻿# bot.py
import discord
from discord.ext import commands

from config import PREFIX, DISCORD_TOKEN, INTENTS
from help_texts import GENERAL_HELP, COMMAND_HELP
from data_utils import DATA, ensure_guild, ensure_section, save_data

bot = commands.Bot(command_prefix=PREFIX, intents=INTENTS, help_command=None)


# -----------------------
# Сommands
# -----------------------
@bot.command(name="addkeyword")
async def addkeyword(ctx, section_name: str, *, keyword: str):
    guild_conf = ensure_guild(ctx.guild.id)
    section = ensure_section(guild_conf, section_name)
    kw = keyword.strip().lower()
    if kw in section["keywords"]:
        await ctx.send(f"The keyword `{kw}` is already in the list of section `{section_name}`.")
        return
    section["keywords"].append(kw)
    save_data(DATA)
    await ctx.send(f"Added keyword: `{kw}` to section `{section_name}`")

@bot.command(name="remkeyword")
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

@bot.command(name="listkeywords")
async def listkeywords(ctx, section_name: str):
    guild_conf = ensure_guild(ctx.guild.id)
    section = ensure_section(guild_conf, section_name)
    kws = section["keywords"]
    if not kws:
        await ctx.send(f"The keyword list in section `{section_name}` is empty.")
        return
    await ctx.send("Keywords: " + ", ".join(f"`{k}`" for k in kws))

@bot.command(name="addsource")
async def addsource(ctx, section_name: str, channel: discord.TextChannel):
    guild_conf = ensure_guild(ctx.guild.id)
    section = ensure_section(guild_conf, section_name)
    cid = str(channel.id)
    if cid in section["sources"]:
        await ctx.send(f"The channel {channel.mention} is already being monitored in section `{section_name}`.")
        return
    section["sources"].append(cid)
    save_data(DATA)
    await ctx.send(f"Added {channel.mention} to monitored channels in section `{section_name}`.")

@bot.command(name="remsource")
async def remsource(ctx, section_name: str, channel: discord.TextChannel):
    guild_conf = ensure_guild(ctx.guild.id)
    section = ensure_section(guild_conf, section_name)
    cid = str(channel.id)
    if cid not in section["sources"]:
        await ctx.send(f"The channel {channel.mention} is not monitored in section `{section_name}`.")
        return
    section["sources"].remove(cid)
    if cid in section["forward_map"]:
        section["forward_map"].pop(cid)
    save_data(DATA)
    await ctx.send(f"Removed {channel.mention} from monitored channels in section `{section_name}`.")

@bot.command(name="setforward")
async def setforward(ctx, section_name: str, source: discord.TextChannel, destination: discord.TextChannel=None):
    guild_conf = ensure_guild(ctx.guild.id)
    section = ensure_section(guild_conf, section_name)
    sid = str(source.id)
    if sid not in section["sources"]:
        await ctx.send(f"Source {source.mention} is not added in section `{section_name}`. Use !addsource first.")
        return
    if destination is None:
        section["forward_map"].pop(sid, None)
        save_data(DATA)
        await ctx.send(f"Forwarding from {source.mention} disabled in section `{section_name}`.")
        return
    section["forward_map"][sid] = str(destination.id)
    save_data(DATA)
    await ctx.send(f"Messages from {source.mention} will be forwarded to {destination.mention} in section `{section_name}`.")

@bot.command(name="setmode")
async def setmode(ctx, section_name: str, mode: str):
    mode = mode.lower()
    if mode not in ("forward", "dm", "all"):
        await ctx.send("Invalid mode. Use: forward, dm, or all.")
        return
    guild_conf = ensure_guild(ctx.guild.id)
    section = ensure_section(guild_conf, section_name)
    section["mode"] = mode
    save_data(DATA)
    await ctx.send(f"Mode for section `{section_name}` set to: `{mode}`")

# -----------------------
# User DM subscriptions
# -----------------------
@bot.command(name="subscribe")
async def subscribe(ctx, section_name: str):
    guild_conf = ensure_guild(ctx.guild.id)
    section = ensure_section(guild_conf, section_name)
    uid = str(ctx.author.id)
    if uid in section["subscribers"]:
        await ctx.send(f"You are already subscribed to DM alerts in section `{section_name}`.")
        return
    section["subscribers"].append(uid)
    save_data(DATA)
    await ctx.send(f"You are now subscribed to DM alerts for keyword matches in section `{section_name}`.")

@bot.command(name="unsubscribe")
async def unsubscribe(ctx, section_name: str):
    guild_conf = ensure_guild(ctx.guild.id)
    section = ensure_section(guild_conf, section_name)
    uid = str(ctx.author.id)
    if uid not in section["subscribers"]:
        await ctx.send(f"You are not subscribed in section `{section_name}`.")
        return
    section["subscribers"].remove(uid)
    save_data(DATA)
    await ctx.send(f"You have been unsubscribed from DM alerts in section `{section_name}`.")

@bot.command(name="listsubs")
@commands.has_guild_permissions(manage_guild=True)
async def listsubs(ctx, section_name: str):
    guild_conf = ensure_guild(ctx.guild.id)
    section = ensure_section(guild_conf, section_name)
    subs = section["subscribers"]
    if not subs:
        await ctx.send(f"Subscriber list in section `{section_name}` is empty.")
        return
    users = []
    for uid in subs:
        member = ctx.guild.get_member(int(uid))
        users.append(member.display_name if member else uid)
    await ctx.send("Subscribers: " + ", ".join(users))

# -----------------------
# Message monitoring logic
# -----------------------
@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if message.author.bot or not message.guild:
        return

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

        mode = section.get("mode", "forward")

        # Forward message
        if mode in ("forward", "all"):
            dest_id = section.get("forward_map", {}).get(sid)
            if dest_id:
                dest = message.guild.get_channel(int(dest_id))
                if dest:
                    jump_url = message.jump_url
                    forwarded = (
                        f"**Forwarded message from {message.channel.mention}**, Original: {jump_url}\n"
                        f"Message: {message.content}"
                    )
                    try:
                        await dest.send(forwarded)
                        for att in message.attachments:
                            await dest.send(att.url)
                    except Exception as e:
                        print("Error forwarding:", e)

        # DM subscribers
        if mode in ("dm", "all"):
            subs = list(section.get("subscribers", []))
            if subs:
                for uid in subs:
                    try:
                        user = await bot.fetch_user(int(uid))
                        await user.send(
                            f"Keyword matched in **{message.guild.name}** / {message.channel.mention}\n"
                            f"Message: {message.content}\n"
                            f"Link: {message.jump_url}"
                        )
                    except Exception as e:
                        print(f"Failed to send DM to {uid}: {e}")

# -----------------------
# Command error handling
# -----------------------
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Incorrect command usage. Please check the arguments.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to run this command.")
    else:
        print("Command error:", error)

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
            await ctx.send(COMMAND_HELP[cmd_lower])
        else:
            await ctx.send(f"No help found for command `{cmd}`. Showing general help:\n{GENERAL_HELP}")
    else:
        await ctx.send(GENERAL_HELP)



# -----------------------
# Bot startup
# -----------------------
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)