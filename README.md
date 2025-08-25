# Discord Music Bot

A feature-rich Discord music bot that can search YouTube and play music in voice channels.

## Features

- 🎵 **YouTube Music Search**: Search and play songs from YouTube
- 📱 **Queue Management**: Add, view, and manage music queues
- 🔊 **Volume Control**: Adjust bot volume from 0-100%
- ⏯️ **Playback Controls**: Play, pause, resume, skip, and stop
- 🤖 **Auto-disconnect**: Automatically leaves when alone in voice channel
- 📊 **Queue Display**: Beautiful embeds showing current song and queue
- 🎨 **Rich Commands**: Intuitive command system with aliases

## Commands

| Command | Aliases | Description |
|---------|---------|-------------|
| `!join` | `!j` | Join your voice channel |
| `!play <query>` | `!p` | Play a song from YouTube |
| `!skip` | `!s` | Skip the current song |
| `!stop` | `!st` | Stop playback and clear queue |
| `!pause` | - | Pause the current song |
| `!resume` | - | Resume the paused song |
| `!queue` | `!q` | Show the current queue |
| `!volume <0-100>` | `!vol`, `!v` | Set the bot's volume |
| `!leave` | `!dc` | Leave the voice channel |
| `!help` | - | Show help information |

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
