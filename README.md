# Discord Forward Bot

A simple yet powerful **Discord bot** that monitors selected channels and automatically **forwards messages** containing specific keywords to target channels.
Supports **multiple independent configurations per server**, making it ideal for organizations that share channels but need different forwarding rules.

---

## 🚀 Features

* **Keyword-based message forwarding** — automatically detect messages containing target words.
* **Different modes of keyword matching**
    * **Keyword matching** — automatically detect messages containing target words in any form.
    * **Exact keyword matching** — automatically detect messages containing target words written exactly as in the list.
* **Per-guild and per-section configuration** — each server can define multiple independent "sections" with their own filters and destinations.
* **Multi-channel support** — monitor multiple source channels simultaneously as well as multiple destination channels.
* **Persistent configuration** — settings stored in `data.json`.
* **Admin commands** — only approved users can use protected commands.
* **Separator mode** — if enabled, messages containing multiple lines will be split into separate lines by the bot and each line will be processed separately.

---

## ⚙️ How It Works

1. The bot monitors messages in channels listed under `"sources"`.
2. When a new message is detected:

   * It checks if the content matches any keyword from the `"keywords"` list.
   * If matched, it forwards the message to the mapped destination channel.
3. The configuration file (`data.json`) defines all behavior and is automatically updated when admins use bot commands.

---

## 🧩 JSON Configuration Structure (`data.json`)

Below is an example configuration with inline explanations.

```json
{
  "123456789012345678": {
    "_comment": "Guild (server) configuration",
    "sections": {
      "org1": {
        "_comment": "Section name for organization #1",

        "keywords": ["urgent", "alert", "meeting"],
        "_comment_keywords": "List of words that trigger forwarding if they are written in any form",
        
        "exact_keywords": ["tow", "help"],
        "_comment_exact_keywords": "List of words that trigger forwarding only if they are written exactly as in the list",

        "sources": ["111111111111111111", "222222222222222222"],
        "_comment_sources": "IDs of channels to monitor",

        "destinations": ["333333333333333333", "444444444444444444"],
        "_comment_destinations": "IDs of channels where to forward messages from source channel with same index"
      },

      "org2": {
        "_comment": "Another section for organization #2",
        "keywords": ["urgent", "event"],
        "exact_keywords": ["tow"],
        "sources": ["111111111111111111"],
        "destinations": ["777777777777777777"]        
      }
    }
  }
}
```

---

## 🧠 Terminology

| Term            | Meaning                                                                                                                       |
|-----------------|-------------------------------------------------------------------------------------------------------------------------------|
| **Guild**       | A Discord server. Each guild has its own configuration.                                                                       |
| **Section**     | A subgroup inside a guild’s config. Used to isolate multiple organizations or teams sharing one server.                       |
| **Source**      | Channel where messages are read.                                                                                              |
| **Destination** | Channel where messages are forwarded. <br/>Index based: message from source[n] message will be forwarded to destination[n] channel |
| **Keyword**     | A trigger word that activates forwarding.                                                                                     |
| **Admin**       | User who was added to bot admin list and can use protected commands.                                                          |

---

## 🛠️ Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/discord-forward-bot.git
   cd discord-forward-bot
   ```
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. Create .env file with discord token in bot directory:

   ```bash
   DISCORD_TOKEN=your_token_here
   ```
4. Run the bot:

   ```bash
   python bot.py
   ```
5. (Optional) If needed, separator mode can be turned on. In this mode, messages containing multiple lines will be split into separate lines by the bot and each line will be processed separately. Set separator mode in `config.py` file:
   ```python
   SEPARATOR_MODE = True
   ```

---

## ⚡ Example Usage

1. **Add your Discord ID to the bot admin list**: Type some protected command, you will see your Discord ID:
   ```text
   ?fw addkeyword organization_section_name1 keyword
   
   Forwarder Bot: User with ID 123456789012345678 is not in Forwarder Bot admin list. Ask admin to add you to the list.
   ```
   Ask bot admin to add your ID to the list in `admins_ids.py` file. After that you will be able to use protected commands.


2. **Add a new section for your organization**
   (Handled automatically when first using commands within the guild.)

3. **Add keywords for this section (Bot Admin only)** — words that trigger forwarding:

   ```text
   ?fw addkeyword organization_section_name1 urgent
   ?fw addkeyword organization_section_name1 base
   ?fw addkeyword organization_section_name1 tow
   ?fw addkeyword organization_section_name2 urgent
   ?fw addkeyword organization_section_name2 police
   ```
   
    Also it is possible to add multiple keywords **separated by space character**:
    ```text
   ?fw addkeyword organization_section_name1 urgent base tow
   ```
   Bot will forward messages containing any of these keywords in any form: `urgent`, `urgently`, `tow`, `towel`.
   <br><br>

   It is also possible to add exact keywords with optional argument `--exact` **at the end of the command:**
    ```text
   ?fw addkeyword organization_section_name1 help --exact
   ```
   Bot will forward messages containing exact word `help`. Message contains `helping` will not be forwarded.


4. **Add forwarding destinations (Bot Admin only)** — where messages matching keywords will be forwarded:

   ```text
   ?fw addforward organization_section_name1 #channel_name1 #forwarded_channel1
   ?fw addforward organization_section_name1 #channel_name2 #forwarded_channel1
   ?fw addforward organization_section_name2 #channel_name1 #forwarded_channel2
   ```
    It is possible to add multiple destination channels for each source channel:
    ```text
   ?fw addforward organization_section_name1 #channel_name1 #forwarded_channel1
   ?fw addforward organization_section_name1 #channel_name1 #forwarded_channel2
   ```
    As well as multiple source channels for each destination channel:
    ```text
   ?fw addforward organization_section_name1 #channel_name1 #forwarded_channel1
   ?fw addforward organization_section_name1 #channel_name2 #forwarded_channel1
   ```

5. **Send a test message** in one of the monitored channels:

   ```
   "Urgent: server maintenance starts in 10 minutes!"
   ```

   The bot will automatically:

   * Forward the message to the destination channel(s)
   * Skip messages without matching keywords
   
   
6. **Get list of all sections (Bot Admin only)**:

   ```text
   ?fw listsections
   ```
   Shows all sections created in this guild.


7. **Remove section (Bot Admin only)**:

   ```text
   ?fw remsection organization_section_name1
   ```
   Removes section `organization_section_name1`.<br>
   *Reminder: If you want to add a section, no need to use specific commands. A new section will be created automatically when first using commands working with section, for example `?fw addkeyword`*

---

## 🔐 Permissions & Intents

To function properly, the bot requires:

* `View Channels`
* `Send Messages`
* `Read Message history`
* `Send Messages in Threads` *(optional)*
* `Embed Links` *(optional)*
* `Message Content Intent`

Make sure to enable **Privileged Intents** in the Discord Developer Portal.

---

## 📜 License

MIT License © 2025 Zimatskii Sergei

---
