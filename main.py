import discord
from discord.ext import commands
import asyncio
import logging
from config import Config
from music_player import MusicPlayer, Song

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix=Config.BOT_PREFIX, intents=intents, help_command=None)
music_player = MusicPlayer(bot)

@bot.event
async def on_ready():
    """Called when the bot is ready"""
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot is in {len(bot.guilds)} guilds')
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=f"{Config.BOT_PREFIX}help for music commands"
        )
    )

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        return
    
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")
        return
    
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ I don't have the required permissions to do that!")
        return
    
    logger.error(f"Command error: {error}")
    await ctx.send(f"❌ An error occurred: {str(error)}")

@bot.command(name='join', aliases=['j'])
async def join(ctx):
    """Join the user's voice channel"""
    if not ctx.author.voice:
        await ctx.send("❌ You need to be in a voice channel first!")
        return
    
    channel = ctx.author.voice.channel
    
    try:
        voice_client = await channel.connect()
        music_player.voice_clients[ctx.guild.id] = voice_client
        music_player.volume[ctx.guild.id] = Config.DEFAULT_VOLUME
        
        await ctx.send(f"🎵 Joined **{channel.name}** and ready to play music!")
        logger.info(f"Bot joined voice channel {channel.name} in guild {ctx.guild.id}")
        
    except Exception as e:
        logger.error(f"Error joining voice channel: {e}")
        await ctx.send("❌ Failed to join the voice channel!")

@bot.command(name='play', aliases=['p'])
async def play(ctx, *, query: str):
    """Play a song from YouTube"""
    if not ctx.author.voice:
        await ctx.send("❌ You need to be in a voice channel first!")
        return
    
    if not ctx.guild.voice_client:
        await ctx.invoke(bot.get_command('join'))
    
    # Show searching message
    searching_msg = await ctx.send(f"🔍 Searching for: **{query}**")
    
    try:
        # Search for the song
        song = await music_player.search_youtube(query)
        
        if not song:
            await searching_msg.edit(content="❌ No songs found for that query!")
            return
        
        # Set the requester
        song.requester = ctx.author
        
        # Check song length
        if song.duration > Config.MAX_SONG_LENGTH:
            await searching_msg.edit(content=f"❌ Song is too long! Maximum allowed: {Config.MAX_SONG_LENGTH // 60} minutes")
            return
        
        # Add to queue
        added = await music_player.add_to_queue(ctx.guild.id, song)
        
        if not added:
            await searching_msg.edit(content="❌ Queue is full!")
            return
        
        # Update message
        await searching_msg.edit(content=f"✅ Added to queue: **{song.title}** ({song.formatted_duration})")
        
        # Start playing if nothing is currently playing
        if not music_player.now_playing.get(ctx.guild.id):
            await music_player.play_next(ctx.guild.id)
        
    except Exception as e:
        logger.error(f"Error in play command: {e}")
        await searching_msg.edit(content="❌ An error occurred while searching for the song!")

@bot.command(name='skip', aliases=['s'])
async def skip(ctx):
    """Skip the current song"""
    if not ctx.guild.voice_client:
        await ctx.send("❌ I'm not playing anything!")
        return
    
    await music_player.skip(ctx.guild.id)
    await ctx.send("⏭️ Skipped the current song!")

@bot.command(name='stop', aliases=['st'])
async def stop(ctx):
    """Stop playback and clear the queue"""
    if not ctx.guild.voice_client:
        await ctx.send("❌ I'm not playing anything!")
        return
    
    await music_player.stop(ctx.guild.id)
    await ctx.send("⏹️ Stopped playback and cleared the queue!")

@bot.command(name='queue', aliases=['q'])
async def queue(ctx):
    """Show the current music queue"""
    queue_info = music_player.get_queue_info(ctx.guild.id)
    
    if not queue_info['current_song'] and not queue_info['queue']:
        await ctx.send("📭 The queue is empty!")
        return
    
    embed = discord.Embed(title="🎵 Music Queue", color=0x00ff00)
    
    # Current song
    if queue_info['current_song']:
        current = queue_info['current_song']
        embed.add_field(
            name="🎶 Now Playing",
            value=f"**{current.title}** ({current.formatted_duration})\nRequested by: {current.requester.display_name}",
            inline=False
        )
    
    # Queue
    if queue_info['queue']:
        queue_text = ""
        for i, song in enumerate(queue_info['queue'][:10], 1):  # Show first 10 songs
            queue_text += f"**{i}.** {song.title} ({song.formatted_duration}) - {song.requester.display_name}\n"
        
        if len(queue_info['queue']) > 10:
            queue_text += f"\n... and {len(queue_info['queue']) - 10} more songs"
        
        embed.add_field(name="📋 Up Next", value=queue_text, inline=False)
    
    # Volume
    embed.add_field(name="🔊 Volume", value=f"{int(queue_info['volume'] * 100)}%", inline=True)
    embed.add_field(name="📊 Queue Length", value=str(queue_info['queue_length']), inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='volume', aliases=['vol', 'v'])
async def volume(ctx, volume: float):
    """Set the bot's volume (0-100)"""
    if not ctx.guild.voice_client:
        await ctx.send("❌ I'm not in a voice channel!")
        return
    
    # Convert percentage to decimal
    volume = volume / 100.0
    
    if volume < 0 or volume > 1:
        await ctx.send("❌ Volume must be between 0 and 100!")
        return
    
    music_player.set_volume(ctx.guild.id, volume)
    await ctx.send(f"🔊 Volume set to {int(volume * 100)}%!")

@bot.command(name='pause')
async def pause(ctx):
    """Pause the current song"""
    if not ctx.guild.voice_client:
        await ctx.send("❌ I'm not playing anything!")
        return
    
    if ctx.guild.voice_client.is_playing():
        ctx.guild.voice_client.pause()
        await ctx.send("⏸️ Paused the music!")
    else:
        await ctx.send("❌ Nothing is currently playing!")

@bot.command(name='resume')
async def resume(ctx):
    """Resume the paused song"""
    if not ctx.guild.voice_client:
        await ctx.send("❌ I'm not in a voice channel!")
        return
    
    if ctx.guild.voice_client.is_paused():
        ctx.guild.voice_client.resume()
        await ctx.send("▶️ Resumed the music!")
    else:
        await ctx.send("❌ Nothing is currently paused!")

@bot.command(name='leave', aliases=['disconnect', 'dc'])
async def leave(ctx):
    """Leave the voice channel"""
    if not ctx.guild.voice_client:
        await ctx.send("❌ I'm not in a voice channel!")
        return
    
    await music_player.stop(ctx.guild.id)
    await ctx.guild.voice_client.disconnect()
    await ctx.send("👋 Left the voice channel!")

@bot.command(name='nowplaying', aliases=['np'])
async def nowplaying(ctx):
    """Show information about the currently playing song"""
    if not ctx.guild.voice_client:
        await ctx.send("❌ I'm not playing anything!")
        return
    
    current_song = music_player.now_playing.get(ctx.guild.id)
    if not current_song:
        await ctx.send("❌ Nothing is currently playing!")
        return
    
    embed = discord.Embed(
        title="🎶 Now Playing",
        description=f"**{current_song.title}**",
        color=0x00ff00
    )
    
    embed.add_field(name="Duration", value=current_song.formatted_duration, inline=True)
    embed.add_field(name="Requested by", value=current_song.requester.display_name, inline=True)
    embed.add_field(name="Volume", value=f"{int(music_player.get_volume(ctx.guild.id) * 100)}%", inline=True)
    
    if current_song.thumbnail:
        embed.set_thumbnail(url=current_song.thumbnail)
    
    await ctx.send(embed=embed)

@bot.command(name='shuffle')
async def shuffle(ctx):
    """Shuffle the current music queue"""
    if not ctx.guild.voice_client:
        await ctx.send("❌ I'm not in a voice channel!")
        return
    
    queue = music_player.get_queue(ctx.guild.id)
    if len(queue) < 2:
        await ctx.send("❌ Need at least 2 songs in queue to shuffle!")
        return
    
    import random
    random.shuffle(queue)
    await ctx.send("🔀 Shuffled the music queue!")

@bot.command(name='clear')
async def clear(ctx):
    """Clear the music queue"""
    if not ctx.guild.voice_client:
        await ctx.send("❌ I'm not in a voice channel!")
        return
    
    queue = music_player.get_queue(ctx.guild.id)
    if not queue:
        await ctx.send("❌ The queue is already empty!")
        return
    
    queue.clear()
    await ctx.send("🗑️ Cleared the music queue!")

@bot.command(name='remove', aliases=['rm'])
async def remove(ctx, index: int):
    """Remove a song from the queue by its position"""
    if not ctx.guild.voice_client:
        await ctx.send("❌ I'm not in a voice channel!")
        return
    
    removed_song = await music_player.remove_from_queue(ctx.guild.id, index)
    
    if removed_song:
        await ctx.send(f"🗑️ Removed **{removed_song.title}** from the queue!")
    else:
        await ctx.send("❌ Invalid song position! Use `!queue` to see song positions.")

@bot.command(name='playlist', aliases=['pl'])
async def playlist(ctx, playlist_url: str):
    """Add a YouTube playlist to the queue"""
    if not ctx.author.voice:
        await ctx.send("❌ You need to be in a voice channel first!")
        return
    
    if not ctx.guild.voice_client:
        await ctx.invoke(bot.get_command('join'))
    
    # Check if it's a playlist URL
    if 'playlist' not in playlist_url and 'list=' not in playlist_url:
        await ctx.send("❌ Please provide a valid YouTube playlist URL!")
        return
    
    # Show processing message
    processing_msg = await ctx.send(f"🔍 Processing playlist: **{playlist_url}**")
    
    try:
        # Add playlist to queue
        added_count = await music_player.add_playlist(ctx.guild.id, playlist_url, ctx.author)
        
        if added_count == 0:
            await processing_msg.edit(content="❌ Failed to add playlist or playlist is empty!")
            return
        
        # Update message
        await processing_msg.edit(content=f"✅ Added **{added_count}** songs from playlist to queue!")
        
        # Start playing if nothing is currently playing
        if not music_player.now_playing.get(ctx.guild.id):
            await music_player.play_next(ctx.guild.id)
        
    except Exception as e:
        logger.error(f"Error in playlist command: {e}")
        await processing_msg.edit(content="❌ An error occurred while processing the playlist!")

@bot.command(name='help')
async def help_command(ctx):
    """Show help information"""
    embed = discord.Embed(
        title="🎵 Music Bot Help",
        description=f"Use `{Config.BOT_PREFIX}` before each command",
        color=0x00ff00
    )
    
    commands_info = [
        ("join/j", "Join your voice channel"),
        ("play/p <query>", "Play a song from YouTube"),
        ("playlist/pl <url>", "Add a YouTube playlist to queue"),
        ("skip/s", "Skip the current song"),
        ("stop/st", "Stop playback and clear queue"),
        ("pause", "Pause the current song"),
        ("resume", "Resume the paused song"),
        ("queue/q", "Show the current queue"),
        ("volume/vol/v <0-100>", "Set the bot's volume"),
        ("leave/dc", "Leave the voice channel"),
        ("nowplaying/np", "Show current song info"),
        ("shuffle", "Shuffle the current queue"),
        ("clear", "Clear the music queue"),
        ("remove/rm <position>", "Remove a song from queue"),
        ("help", "Show this help message")
    ]
    
    for cmd, desc in commands_info:
        embed.add_field(name=f"`{cmd}`", value=desc, inline=False)
    
    embed.set_footer(text=f"Bot prefix: {Config.BOT_PREFIX}")
    await ctx.send(embed=embed)

@bot.event
async def on_voice_state_update(member, before, after):
    """Handle voice state updates (auto-disconnect when alone)"""
    # Only care about the bot's guild
    if member.guild.id not in music_player.voice_clients:
        return
    
    voice_client = music_player.voice_clients[member.guild.id]
    
    # If bot is alone in the channel, disconnect after a delay
    if voice_client.is_connected():
        channel = voice_client.channel
        members = [m for m in channel.members if not m.bot]
        
        if len(members) == 0:
            logger.info(f"Bot is alone in {channel.name}, disconnecting in 10 seconds...")
            await asyncio.sleep(10)
            
            # Check again after delay
            if voice_client.is_connected():
                members = [m for m in voice_client.channel.members if not m.bot]
                if len(members) == 0:
                    await music_player.stop(member.guild.id)
                    await voice_client.disconnect()
                    await voice_client.guild.system_channel.send("👋 Left the voice channel because I was alone!")

def main():
    """Main function to run the bot"""
    try:
        # Validate configuration
        Config.validate()
        
        # Run the bot
        logger.info("Starting Discord Music Bot...")
        bot.run(Config.DISCORD_TOKEN)
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"Error: {e}")
        print("Please check your .env file and ensure DISCORD_TOKEN is set.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
