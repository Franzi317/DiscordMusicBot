import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Discord Bot Token (required)
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    
    # Bot Configuration
    BOT_PREFIX = os.getenv('BOT_PREFIX', '!')
    BOT_NAME = os.getenv('BOT_NAME', 'MusicBot')
    
    # Music Configuration
    MAX_QUEUE_SIZE = int(os.getenv('MAX_QUEUE_SIZE', '100'))
    MAX_PLAYLIST_SIZE = int(os.getenv('MAX_PLAYLIST_SIZE', '50'))
    MAX_SONG_LENGTH = int(os.getenv('MAX_SONG_LENGTH', '600'))  # 10 minutes in seconds
    
    # Audio Configuration
    DEFAULT_VOLUME = float(os.getenv('DEFAULT_VOLUME', '0.5'))
    MAX_VOLUME = float(os.getenv('MAX_VOLUME', '1.0'))
    
    # YouTube Configuration
    YOUTUBE_DL_OPTIONS = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0'
    }
    
    # FFmpeg Configuration
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }
    
    # Database Configuration (if using persistent storage)
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///musicbot.db')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'musicbot.log')
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present"""
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN environment variable is required!")
        return True
