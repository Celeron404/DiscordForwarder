# bot.py
import discord
import traceback
from discord.ext import commands

from admins_ids import ADMIN_IDS
from config import PREFIX, DISCORD_TOKEN, INTENTS
from help_texts import GENERAL_HELP, COMMAND_HELP
from data_utils import DATA, ensure_guild, ensure_section, save_data

bot = commands.Bot(command_prefix=PREFIX, intents=INTENTS, help_command=None)



def is_admin():
    async def predicate(ctx):
        if ctx.author.id in ADMIN_IDS.values():
            return True
        else:
            await ctx.send(f"User with ID `{ctx.author.id}` is not in Forwarder Bot admin list. Ask admin to add you to the list to use the command.")
            return False
    return commands.check(predicate)

# -----------------------
# Сommands
# -----------------------
@is_admin()
@bot.command(name="addkeyword", aliases=["akw", "addkw"])
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

@is_admin()
@bot.command(name="remkeyword", aliases=["rkw", "remkw"])
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

@bot.command(name="listkeywords", aliases=["lkw", "lskw"])
async def listkeywords(ctx, section_name: str):
    guild_conf = ensure_guild(ctx.guild.id)
    section = ensure_section(guild_conf, section_name)
    kws = section["keywords"]
    if not kws:
        await ctx.send(f"The keyword list in section `{section_name}` is empty.")
        return
    await ctx.send("Keywords: " + ", ".join(f"`{k}`" for k in kws))

@is_admin()
@bot.command(name="addsource", aliases=["as", "addsrc"])
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

@is_admin()
@bot.command(name="remsource", aliases=["rs", "rmsrc"])
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

@is_admin()
@bot.command(name="setforward", aliases=["sf", "setfw"])
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
    return

@is_admin()
@bot.command(name="listsections", aliases=["lsec"])
async def listsections(ctx):
    guild_conf = ensure_guild(ctx.guild.id)
    sections = guild_conf["sections"]
    if not sections:
        await ctx.send("Section list is empty.")
        return
    await ctx.send("Sections list: `" + "`, `".join(sections.keys()) + "`")

@is_admin()
@bot.command(name="remsection", aliases=["rsec", "remsec"])
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

        # Forward message
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