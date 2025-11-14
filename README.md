# Discord Forward Bot

A simple yet powerful **Discord bot** that monitors selected channels and automatically **forwards messages** containing specific keywords to target channels or users.
Supports **multiple independent configurations per server**, making it ideal for organizations that share channels but need different forwarding rules.

---

## 🚀 Features

* **Keyword-based message forwarding** — automatically detect messages containing target words.
* **Per-guild and per-section configuration** — each server can define multiple independent "sections" with their own filters and destinations.
* **Flexible forwarding modes**:

  * `forward` — (Default) only forward messages to target channels.
  * `dm` — only send messages to subscribers via direct messages.
  * `all` — both forward and DM.
* **Multi-channel support** — monitor multiple source channels simultaneously.
* **Custom subscriber notifications** — notify specific users privately.
* **Persistent configuration** — settings stored in `data.json`.
* **Admin commands** — only approved users can use protected commands.

---

## ⚙️ How It Works

1. The bot monitors messages in channels listed under `"sources"`.
2. When a new message is detected:

   * It checks if the content matches any keyword from the `"keywords"` list.
   * If matched, it forwards the message to the mapped destination channel or DMs subscribers.
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
        "_comment_keywords": "List of words that trigger forwarding",

        "sources": ["111111111111111111", "222222222222222222"],
        "_comment_sources": "IDs of channels to monitor",

        "forward_map": {
          "111111111111111111": "333333333333333333",
          "222222222222222222": "444444444444444444"
        },
        "_comment_forward_map": "Maps source channels to destination channels",

        "mode": "all",
        "_comment_mode": "Forwarding mode: 'forward', 'dm', or 'all'",

        "subscribers": ["555555555555555555", "666666666666666666"],
        "_comment_subscribers": "List of user IDs for direct notifications"
      },

      "org2": {
        "_comment": "Another section for organization #2",
        "keywords": ["urgent", "event"],
        "sources": ["111111111111111111"],
        "forward_map": {
          "111111111111111111": "777777777777777777"
        },
        "mode": "forward",
        "subscribers": []
      }
    }
  }
}
```

---

## 🧠 Terminology

| Term            | Meaning                                                                                                 |
|-----------------|---------------------------------------------------------------------------------------------------------|
| **Guild**       | A Discord server. Each guild has its own configuration.                                                 |
| **Section**     | A subgroup inside a guild’s config. Used to isolate multiple organizations or teams sharing one server. |
| **Source**      | Channel where messages are read.                                                                        |
| **Destination** | Channel where messages are forwarded.                                                                   |
| **Keyword**     | A trigger word that activates forwarding.                                                               |
| **Subscriber**  | User who receives forwarded messages via DM.                                                            |
| **Admin**       | User who was added to bot admin list and can use protected commands.                                    |

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

---

## ⚡ Example Usage

1. **Add your Discord ID to the bot admin list**: Type some protected command, you will see your Discord ID:
   ```text
   ?fw addsource organization_section_name1 #channel_name1
   
   Forwarder Bot: User with ID 123456789012345678 is not in Forwarder Bot admin list. Ask admin to add you to the list.
   ```
   Ask bot admin to add your ID to the list in `admins_ids.py` file. After that you will be able to use protected commands.


2. **Add a new section for your organization**
   (Handled automatically when first using commands within the guild.)

2. **Add source channels (Bot Admin only)** — channels the bot should monitor:

   ```text
   ?fw addsource organization_section_name1 #channel_name1
   ?fw addsource organization_section_name1 #channel_name2
   ?fw addsource organization_section_name2 #channel_name1
   ```

3. **Add keywords for this section (Bot Admin only)** — words that trigger forwarding:

   ```text
   ?fw addkeyword organization_section_name1 urgent
   ?fw addkeyword organization_section_name1 base
   ?fw addkeyword organization_section_name1 tow
   ?fw addkeyword organization_section_name2 urgent
   ?fw addkeyword organization_section_name2 police
   ```

4. **Set forwarding destinations (Bot Admin only)** — where messages matching keywords will be forwarded:

   ```text
   ?fw setforward organization_section_name1 #channel_name1 #forwarded_channel1
   ?fw setforward organization_section_name1 #channel_name2 #forwarded_channel1
   ?fw setforward organization_section_name2 #channel_name1 #forwarded_channel2
   ```

5. **Set mode (Bot Admin only)** — choose how messages are delivered:

   ```text
   ?fw setmode organization_section_name1 all       # forward to channel + DM subscribers
   ?fw setmode organization_section_name2 forward   # only forward to channels
   ```

6. **Subscribe to DM alerts** — users who want to get notified should write this command, it will work only with section with "all" or "dm" mode:

   ```text
   ?fw subscribe organization_section_name1
   ```

7. **Send a test message** in one of the monitored channels:

   ```
   "Urgent: server maintenance starts in 10 minutes!"
   ```

   The bot will automatically:

   * Forward the message to the destination channel(s) if `forward` or `all` is enabled
   * Send a DM to subscribers if `dm` or `all` is enabled
   * Skip messages without matching keywords
   

8. **See subscriptions (Bot Admin only)**:

   ```text
   ?fw organization_section_name1 listsubs            # view all current subscribers
   ```
   
9. **Manage subscriptions** - by user why was subscribed:

   ```text
   ?fw organization_section_name1 unsubscribe         # stop receiving DMs
   ```
   
10. **Get list of all sections (Bot Admin only)**:

   ```text
   ?fw listsections
   ```
   Shows all sections created in this guild.

11. **Remove section (Bot Admin only)**:

   ```text
   ?fw remsection organization_section_name1
   ```
   Removes section `organization_section_name1`.<br>
   *Reminder: If you want to add a section, no need to use specific commands. A new section will be created automatically when first using commands working with section, for example `?fw addkeyword`, `?fw addsource`.*

---

## 🔐 Permissions & Intents

To function properly, the bot requires:

* `View Channels`
* `Send Messages`
* `Read Message history`
* `Send Messages in Threads` *(optional)*
* `Embed Links` *(optional)*
* `Guild Members Intent` *(for DMs and user management)*
* `Message Content Intent`

Make sure to enable **Privileged Intents** in the Discord Developer Portal.

---

## 📜 License

MIT License © 2025 Zimatskii Sergei

---
