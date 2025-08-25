import asyncio
import discord
from discord.ext import commands
import yt_dlp
import re
from typing import Optional, List, Dict
import logging
from config import Config

logger = logging.getLogger(__name__)

class Song:
    """Represents a song in the queue"""
    
    def __init__(self, title: str, url: str, duration: int, requester: discord.Member, thumbnail: str = None):
        self.title = title
        self.url = url
        self.duration = duration
        self.requester = requester
        self.thumbnail = thumbnail
        
    def __str__(self):
        return f"**{self.title}** - Requested by {self.requester.display_name}"
    
    @property
    def formatted_duration(self):
        """Return formatted duration string"""
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes}:{seconds:02d}"

class MusicPlayer:
    """Handles music playback and queue management"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queues: Dict[int, List[Song]] = {}  # guild_id -> queue
        self.now_playing: Dict[int, Song] = {}   # guild_id -> current song
        self.voice_clients: Dict[int, discord.VoiceClient] = {}  # guild_id -> voice client
        self.volume: Dict[int, float] = {}       # guild_id -> volume
        
    def get_queue(self, guild_id: int) -> List[Song]:
        """Get the music queue for a guild"""
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        return self.queues[guild_id]
    
    def get_volume(self, guild_id: int) -> float:
        """Get the volume for a guild"""
        if guild_id not in self.volume:
            self.volume[guild_id] = Config.DEFAULT_VOLUME
            logger.info(f"Initialized default volume for guild {guild_id}: {Config.DEFAULT_VOLUME}")
        return self.volume[guild_id]
    
    def ensure_volume_initialized(self, guild_id: int) -> float:
        """Ensure volume is initialized and return it"""
        if guild_id not in self.volume:
            self.volume[guild_id] = Config.DEFAULT_VOLUME
            logger.info(f"Ensured volume initialized for guild {guild_id}: {Config.DEFAULT_VOLUME}")
        return self.volume[guild_id]
    
    def set_volume(self, guild_id: int, volume: float):
        """Set the volume for a guild"""
        # Ensure volume is a valid float
        try:
            volume = float(volume)
            self.volume[guild_id] = max(0.0, min(volume, Config.MAX_VOLUME))
        except (ValueError, TypeError):
            # Fallback to default volume if invalid
            self.volume[guild_id] = Config.DEFAULT_VOLUME
        
        # Update current audio source volume if playing
        if guild_id in self.voice_clients and self.voice_clients[guild_id].source:
            try:
                self.voice_clients[guild_id].source.volume = self.volume[guild_id]
            except Exception as e:
                logger.warning(f"Could not update volume for guild {guild_id}: {e}")
    
    async def search_youtube(self, query: str) -> Optional[Song]:
        """Search YouTube for a song"""
        try:
            ydl_opts = Config.YOUTUBE_DL_OPTIONS.copy()
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Try to extract info directly if it's a URL
                if query.startswith(('http://', 'https://')):
                    info = ydl.extract_info(query, download=False)
                else:
                    # Search for the query
                    search_query = f"ytsearch1:{query}"
                    info = ydl.extract_info(search_query, download=False)
                    if 'entries' in info and info['entries']:
                        info = info['entries'][0]
                    else:
                        return None
                
                # Validate required fields
                if not info.get('title') or not info.get('webpage_url'):
                    logger.warning(f"Incomplete video info: {info}")
                    return None
                
                # Create Song object
                song = Song(
                    title=info.get('title', 'Unknown Title'),
                    url=info.get('webpage_url', query),
                    duration=info.get('duration', 0),
                    requester=None,  # Will be set by caller
                    thumbnail=info.get('thumbnail')
                )
                
                logger.info(f"Found song: {song.title} ({song.formatted_duration})")
                return song
                
        except Exception as e:
            logger.error(f"Error searching YouTube: {e}")
            return None

    async def search_youtube_multiple(self, query: str, max_results: int = 5) -> List[Song]:
        """Search YouTube for multiple songs"""
        try:
            ydl_opts = Config.YOUTUBE_DL_OPTIONS.copy()
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Try to extract info directly if it's a URL
                if query.startswith(('http://', 'https://')):
                    info = ydl.extract_info(query, download=False)
                    # For direct URLs, return as single result
                    if info.get('title') and info.get('webpage_url'):
                        song = Song(
                            title=info.get('title', 'Unknown Title'),
                            url=info.get('webpage_url', query),
                            duration=info.get('duration', 0),
                            requester=None,
                            thumbnail=info.get('thumbnail')
                        )
                        return [song]
                    return []
                else:
                    # Search for multiple results
                    search_query = f"ytsearch{max_results}:{query}"
                    info = ydl.extract_info(search_query, download=False)
                    
                    if 'entries' not in info or not info['entries']:
                        return []
                    
                    songs = []
                    for entry in info['entries']:
                        if entry and entry.get('title') and entry.get('webpage_url'):
                            song = Song(
                                title=entry.get('title', 'Unknown Title'),
                                url=entry.get('webpage_url', ''),
                                duration=entry.get('duration', 0),
                                requester=None,  # Will be set by caller
                                thumbnail=entry.get('thumbnail')
                            )
                            songs.append(song)
                            
                            if len(songs) >= max_results:
                                break
                    
                    logger.info(f"Found {len(songs)} songs for query: {query}")
                    return songs
                
        except Exception as e:
            logger.error(f"Error searching YouTube for multiple results: {e}")
            return []
    
    async def add_to_queue(self, guild_id: int, song: Song) -> bool:
        """Add a song to the queue"""
        queue = self.get_queue(guild_id)
        
        if len(queue) >= Config.MAX_QUEUE_SIZE:
            return False
        
        queue.append(song)
        return True
    
    async def play_next(self, guild_id: int):
        """Play the next song in the queue"""
        queue = self.get_queue(guild_id)
        
        if not queue:
            # No more songs, disconnect after a delay
            await asyncio.sleep(10)
            if guild_id in self.voice_clients:
                await self.voice_clients[guild_id].disconnect()
                del self.voice_clients[guild_id]
            return
        
        # Get next song
        song = queue.pop(0)
        self.now_playing[guild_id] = song
        
        # Play the song
        try:
            voice_client = self.voice_clients.get(guild_id)
            if not voice_client:
                logger.error(f"No voice client found for guild {guild_id}")
                return
            
            if not voice_client.is_connected():
                logger.error(f"Voice client not connected for guild {guild_id}")
                return
            
            logger.info(f"Starting playback for: {song.title} in guild {guild_id}")
            
            # Create audio source
            ydl_opts = Config.YOUTUBE_DL_OPTIONS.copy()
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(song.url, download=False)
                
                # Validate info structure
                if not info or 'formats' not in info:
                    logger.error(f"Invalid video info structure for song: {song.title}")
                    raise ValueError("Invalid video info structure")
                
                logger.info(f"Found {len(info['formats'])} audio formats for song: {song.title}")
                
                # Find the best audio format
                audio_formats = [f for f in info['formats'] if f.get('acodec') != 'none']
                if not audio_formats:
                    # Fallback to any format
                    audio_formats = info['formats']
                    logger.info(f"Using fallback formats for song: {song.title}")
                
                if not audio_formats:
                    logger.error(f"No audio formats found for song: {song.title}")
                    raise ValueError("No audio formats available")
                
                # Filter out formats without URLs
                audio_formats = [f for f in audio_formats if f.get('url')]
                if not audio_formats:
                    logger.error(f"No formats with URLs found for song: {song.title}")
                    raise ValueError("No audio formats with URLs available")
                
                # Sort by quality (prefer audio-only formats)
                # Handle None values safely in sorting
                def safe_sort_key(x):
                    acodec = x.get('acodec', '')
                    abr = x.get('abr', 0) or 0  # Convert None to 0
                    filesize = x.get('filesize', 0) or 0  # Convert None to 0
                    
                    # Ensure numeric values are valid
                    try:
                        abr = float(abr) if abr is not None else 0.0
                        filesize = float(filesize) if filesize is not None else 0.0
                    except (ValueError, TypeError):
                        abr = 0.0
                        filesize = 0.0
                    
                    return (
                        acodec == 'none',  # Prefer audio-only
                        abr,               # Higher bitrate
                        filesize           # Larger file size
                    )
                
                try:
                    audio_formats.sort(key=safe_sort_key)
                    logger.info(f"Successfully sorted {len(audio_formats)} audio formats")
                except Exception as e:
                    logger.warning(f"Error sorting audio formats, using first available: {e}")
                    # If sorting fails, just use the first format
                
                # Get the best format
                best_format = audio_formats[0]
                url = best_format.get('url')
                
                if not url:
                    logger.error(f"No URL found in audio format for song: {song.title}")
                    raise ValueError("No audio URL available")
                
                logger.info(f"Selected format: acodec={best_format.get('acodec', 'unknown')}, "
                          f"abr={best_format.get('abr', 'unknown')}, "
                          f"filesize={best_format.get('filesize', 'unknown')}")
                logger.info(f"Using audio URL: {url[:100]}...")
                
                # Create FFmpeg audio source
                source = discord.FFmpegPCMAudio(
                    url,
                    **Config.FFMPEG_OPTIONS
                )
                
                # Apply volume with safety check
                volume = self.ensure_volume_initialized(guild_id)
                if volume is None or not isinstance(volume, (int, float)):
                    volume = Config.DEFAULT_VOLUME
                    self.volume[guild_id] = volume
                    logger.info(f"Reset volume to default for guild {guild_id}: {volume}")
                
                logger.info(f"Setting volume to {volume} for guild {guild_id}")
                source = discord.PCMVolumeTransformer(source, volume=float(volume))
                
                # Play the audio
                voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.play_next(guild_id), self.bot.loop
                ))
                
                logger.info(f"Now playing: {song.title} in guild {guild_id}")
                
                # Reset retry counter on successful playback
                if hasattr(self, '_play_retry_count'):
                    self._play_retry_count = 0
                
        except Exception as e:
            logger.error(f"Error playing song '{song.title}' in guild {guild_id}: {e}")
            logger.error(f"Full error details: {type(e).__name__}: {str(e)}")
            
            # Log additional context for debugging
            logger.error(f"Voice client state: connected={voice_client.is_connected() if voice_client else 'No voice client'}")
            logger.error(f"Queue state: {len(queue)} songs remaining")
            
            # Try to play next song, but limit retries to prevent infinite loops
            if hasattr(self, '_play_retry_count'):
                self._play_retry_count += 1
            else:
                self._play_retry_count = 1
            
            if self._play_retry_count <= 3:
                logger.info(f"Retrying playback (attempt {self._play_retry_count}/3)")
                await self.play_next(guild_id)
            else:
                logger.error(f"Max retry attempts reached for guild {guild_id}, stopping playback")
                self._play_retry_count = 0
                # Clear the queue to prevent further issues
                queue.clear()
                if guild_id in self.now_playing:
                    del self.now_playing[guild_id]
    
    async def skip(self, guild_id: int):
        """Skip the current song"""
        if guild_id in self.voice_clients:
            self.voice_clients[guild_id].stop()
    
    async def stop(self, guild_id: int):
        """Stop playback and clear queue"""
        if guild_id in self.voice_clients:
            self.voice_clients[guild_id].stop()
        
        # Clear queue
        if guild_id in self.queues:
            self.queues[guild_id].clear()
        
        # Clear now playing
        if guild_id in self.now_playing:
            del self.now_playing[guild_id]
    
    def get_queue_info(self, guild_id: int) -> Dict:
        """Get information about the current queue and playback"""
        queue = self.get_queue(guild_id)
        current_song = self.now_playing.get(guild_id)
        
        return {
            'current_song': current_song,
            'queue': queue,
            'queue_length': len(queue),
            'volume': self.get_volume(guild_id)
        }
    
    async def remove_from_queue(self, guild_id: int, index: int) -> Optional[Song]:
        """Remove a song from the queue by index (1-based)"""
        queue = self.get_queue(guild_id)
        
        if index < 1 or index > len(queue):
            return None
        
        # Convert to 0-based index
        removed_song = queue.pop(index - 1)
        return removed_song
    
    def get_queue_position(self, guild_id: int, song_title: str) -> Optional[int]:
        """Get the position of a song in the queue by title"""
        queue = self.get_queue(guild_id)
        
        for i, song in enumerate(queue, 1):
            if song.title.lower() == song_title.lower():
                return i
        
        return None
    
    async def add_playlist(self, guild_id: int, playlist_url: str, requester: discord.Member) -> int:
        """Add a YouTube playlist to the queue"""
        try:
            ydl_opts = Config.YOUTUBE_DL_OPTIONS.copy()
            ydl_opts['extract_flat'] = True
            ydl_opts['playlist_items'] = f'1-{Config.MAX_PLAYLIST_SIZE}'
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(playlist_url, download=False)
                
                if 'entries' not in info:
                    return 0
                
                added_count = 0
                for entry in info['entries']:
                    if added_count >= Config.MAX_PLAYLIST_SIZE:
                        break
                    
                    if entry:
                        song = Song(
                            title=entry.get('title', 'Unknown Title'),
                            url=entry.get('url', ''),
                            duration=entry.get('duration', 0),
                            requester=requester,
                            thumbnail=entry.get('thumbnail')
                        )
                        
                        if await self.add_to_queue(guild_id, song):
                            added_count += 1
                
                return added_count
                
        except Exception as e:
            logger.error(f"Error adding playlist: {e}")
            return 0
