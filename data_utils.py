import os, json
from config import DATA_FILE

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8-sig") as file:
        return json.load(file)

def save_data(json_data):
    with open(DATA_FILE, "w", encoding="utf-8-sig") as file:
        json.dump(json_data, file, ensure_ascii=False, indent=2)

DATA = load_data()  # structure: data[guild_id]["sections"][section_name] = {keywords, sources, destinations}

def ensure_guild(gid):
    gid = str(gid)
    if gid not in DATA:
        DATA[gid] = {"sections": {}}
        save_data(DATA)
    return DATA[gid]

def ensure_section(guild_conf, section_name):
    if "sections" not in guild_conf:
        guild_conf["sections"] = {}
    if section_name not in guild_conf["sections"]:
        guild_conf["sections"][section_name] = {
            "keywords": [],
            "sources": [],
            "destinations": []
        }
        save_data(DATA)
    return guild_conf["sections"][section_name]