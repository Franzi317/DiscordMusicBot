# Discord Music Bot

A feature-rich Discord music bot that plays music directly from YouTube URLs or searches. Perfect for quick music playback and advanced queue management.

## Quick Start

1. **Join a voice channel** in your Discord server
2. **Use `!play <song name or YouTube URL>`** to add music to the queue
3. **That's it!** The bot will automatically join and start playing

**Examples:**
- `!play despacito` - Search and play "Despacito"
- `!play https://youtube.com/watch?v=...` - Play from YouTube URL
- `!p billie jean` - Quick play with alias

## Features

- 🎵 **Direct YouTube Playback**: Play songs instantly with `!play <url or search>`
- 📱 **Queue Management**: Add, view, and manage music queues
- 🔊 **Volume Control**: Adjust bot volume from 0-100%
- ⏯️ **Playback Controls**: Play, pause, resume, skip, and stop
- 🤖 **Auto-disconnect**: Automatically leaves when alone in voice channel
- 📊 **Queue Display**: Beautiful embeds showing current song and queue
- 🎨 **Rich Commands**: Intuitive command system with aliases

## Commands

| Command | Aliases | Description |
|---------|---------|-------------|
| `!play <query>` | `!p` | **Primary command** - Play a song from YouTube URL or search |
| `!join` | `!j` | Join your voice channel |
| `!playlist <url>` | `!pl` | Add a YouTube playlist to queue |
| `!skip` | `!s` | Skip the current song |
| `!stop` | `!st` | Stop playback and clear queue |
| `!pause` | - | Pause the current song |
| `!resume` | - | Resume the paused song |
| `!queue` | `!q` | Show the current queue |
| `!volume <0-100>` | `!vol`, `!v` | Set the bot's volume |
| `!leave` | `!dc` | Leave the voice channel |
| `!nowplaying` | `!np` | Show current song info |
| `!shuffle` | - | Shuffle the current queue |
| `!clear` | - | Clear the music queue |
| `!remove <position>` | `!rm` | Remove a song from queue |
| `!search <query>` | `!sr` | Advanced search with interactive results |
| `!quicksearch <query>` | `!qs` | Quick search showing results without reactions |
| `!playresult <number>` | - | Play a specific search result |
| `!clearsearch` | - | Clear stored search results |
| `!autodisconnect <on/off>` | `!ad` | Enable/disable auto-disconnect when alone |
| `!help` | - | Show help information |

## Primary Usage: `!play` Command

The `!play` command is the main way to add music to your queue. It's fast, simple, and works with both YouTube URLs and search queries.

### `!play <query>` or `!p <query>`
- **Primary command** for adding music to your queue
- Works with YouTube URLs: `!play https://youtube.com/watch?v=...`
- Works with search queries: `!play rick astley never gonna give you up`
- Automatically finds the best match and adds it to your queue
- Perfect for quick music requests

**Examples:**
- `!play https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- `!play despacito`
- `!play queen bohemian rhapsody`
- `!p billie jean michael jackson`

## Advanced Search Commands

For more control over song selection, the bot includes advanced search functionality:

### `!search <query>` or `!sr <query>`
- **Advanced search** with interactive results (use `!play` for quick requests)
- Shows up to 5 results with interactive reactions
- Click the number emoji (1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣) to play that song
- Results are stored for use with `!playresult`
- Best for when you want to choose from multiple options

### `!quicksearch <query>` or `!qs <query>`
- **Quick preview** of search results without reactions
- Useful for seeing what's available before deciding
- Results are also stored for `!playresult`
- Alternative to `!search` when you don't need reactions

### `!playresult <number>`
- Play a specific search result by number (1-5)
- Use after running `!search` or `!quicksearch`
- Example: `!playresult 3` plays the 3rd result

### `!clearsearch`
- Clear your stored search results
- Use if you want to start fresh with new searches

### `!autodisconnect <on/off>` or `!ad <on/off>`
- Control whether the bot automatically leaves when no one is listening
- **On (default)**: Bot leaves after 10 seconds of being alone
- **Off**: Bot stays in voice channel even when alone
- Examples: `!autodisconnect on`, `!ad off`

## Auto-Disconnect Feature

The bot automatically detects when it's alone in a voice channel and will leave after a configurable delay (default: 10 seconds). This helps save resources and ensures the bot isn't playing music for no one.

**How it works:**
1. **Detection**: Bot monitors voice channel for human users
2. **Warning**: Sends a message when alone: "⚠️ No one is listening! I'll leave in 10 seconds if no one joins..."
3. **Countdown**: Waits 10 seconds, checking every second for new users
4. **Cancellation**: If someone joins during the countdown, the bot stays
5. **Disconnect**: If still alone after 10 seconds, bot stops music and leaves

**Configuration:**
- Set `AUTO_DISCONNECT_DELAY=15` in your `.env` file to change the delay to 15 seconds
- Use `!autodisconnect off` to disable the feature for your server
- Use `!autodisconnect on` to re-enable it

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system
- A Discord bot token

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg

**Windows:**
1. Download FFmpeg from [FFmpeg website](https://ffmpeg.org/download.html)
   - Go to "Windows Builds" section
   - Download the latest release (e.g., "ffmpeg-master-latest-win64-gpl.zip")
2. Extract the ZIP file to a permanent location (e.g., `C:\ffmpeg`)
3. Add FFmpeg to PATH:
   - Press `Win + R`, type `sysdm.cpl`, press Enter
   - Go to "Advanced" tab → "Environment Variables"
   - Under "System Variables", find "Path" and click "Edit"
   - Click "New" and add the path to FFmpeg's bin folder:
     - If you extracted to `C:\ffmpeg`, add: `C:\ffmpeg\bin`
     - If you extracted elsewhere, add: `[your-path]\bin`
   - Click "OK" on all dialogs
4. Restart your command prompt/PowerShell
5. Verify installation by typing: `ffmpeg -version`

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 4. Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section
4. Create a bot and copy the token
5. Enable required intents:
   - Message Content Intent
   - Voice States Intent
   - Server Members Intent

### 5. Invite Bot to Server

Use this URL (replace `YOUR_BOT_ID` with your actual bot ID):
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=3148800&scope=bot
```

### 6. Configure Environment Variables

1. **Copy the template file:**
   ```bash
   # Windows
   copy env.template .env
   
   # macOS/Linux
   cp env.template .env
   ```

2. **Edit the `.env` file** and replace `your_discord_bot_token_here` with your actual Discord bot token

3. **Optional:** Customize other settings as needed

**Example .env file:**
```env
# Required: Your Discord Bot Token
DISCORD_TOKEN=MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5

# Optional: Bot Configuration
BOT_PREFIX=!
BOT_NAME=MusicBot

# Optional: Music Configuration
MAX_QUEUE_SIZE=100
MAX_SONG_LENGTH=600

# Optional: Audio Configuration
DEFAULT_VOLUME=0.5
MAX_VOLUME=1.0

# Optional: Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=musicbot.log
```

### 7. Run the Bot

```bash
# Windows
python main.py

# Or use the batch file
start_bot.bat

# macOS/Linux
python3 main.py

# Or use the shell script
./start_bot.sh
```

### 8. Start Playing Music!

1. **Invite the bot** to your Discord server
2. **Join a voice channel**
3. **Use `!play <song name>`** to start playing music instantly!

**Note:** The `env.template` file is provided as a starting point. Copy it to `.env` and customize it with your Discord bot token before running the bot.

## Configuration Options

### Bot Settings
- `DISCORD_TOKEN`: Your Discord bot token (required)
- `BOT_PREFIX`: Command prefix (default: `!`)
- `BOT_NAME`: Bot name (default: `MusicBot`)

### Music Settings
- `MAX_QUEUE_SIZE`: Maximum songs in queue (default: 100)
- `MAX_SONG_LENGTH`: Maximum song length in seconds (default: 600 = 10 minutes)
- `DEFAULT_VOLUME`: Default volume 0.0-1.0 (default: 0.5)
- `MAX_VOLUME`: Maximum volume allowed (default: 1.0)

### Auto-Disconnect Settings
- `AUTO_DISCONNECT_DELAY`: Seconds to wait before leaving when alone (default: 10)

### Audio Settings
- `FFMPEG_OPTIONS`: FFmpeg configuration for audio processing
- `YOUTUBE_DL_OPTIONS`: YouTube-DL configuration for video extraction

## File Structure

```
discord-music-bot/
├── main.py              # Main bot file with commands
├── music_player.py      # Music player logic and queue management
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── env.template         # Environment variables template
├── start_bot.bat        # Windows startup script
├── start_bot.sh         # Unix startup script
└── README.md            # This file
```

## Troubleshooting

### Common Issues

1. **Bot doesn't join voice channel**
   - Ensure the bot has "Connect" and "Speak" permissions
   - Check that voice states intent is enabled

2. **Audio doesn't play**
   - Verify FFmpeg is installed and in PATH
   - Check bot has "Use Voice Activity" permission

3. **YouTube search fails**
   - Update yt-dlp: `pip install --upgrade yt-dlp`
   - Check internet connection

4. **Bot crashes on startup**
   - Verify `.env` file exists and `DISCORD_TOKEN` is set
   - Check Python version (3.8+ required)

5. **FFmpeg not found error**
   - **Windows**: Make sure you added the `\bin` folder to PATH, not the main FFmpeg folder
   - **Example**: Add `C:\ffmpeg\bin` to PATH, not `C:\ffmpeg`
   - Restart your terminal after changing PATH
   - Test with: `ffmpeg -version` in a new command prompt

### Logs

The bot creates detailed logs in `musicbot.log`. Check this file for error details.

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.
