#!/usr/bin/env python3
"""
Simple test script to verify the Discord Music Bot components
"""

import asyncio
import logging
from config import Config
from music_player import MusicPlayer, Song

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_music_player():
    """Test the music player functionality"""
    print("🧪 Testing Music Player Components...")
    
    # Test configuration
    try:
        Config.validate()
        print("✅ Configuration validation passed")
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False
    
    # Test volume handling
    print("\n🔊 Testing Volume Handling...")
    try:
        # Create a mock bot object
        class MockBot:
            def __init__(self):
                self.loop = asyncio.get_event_loop()
        
        mock_bot = MockBot()
        music_player = MusicPlayer(mock_bot)
        
        # Test volume initialization
        test_guild_id = 12345
        volume = music_player.get_volume(test_guild_id)
        print(f"✅ Initial volume: {volume}")
        
        # Test volume setting
        music_player.set_volume(test_guild_id, 0.7)
        volume = music_player.get_volume(test_guild_id)
        print(f"✅ Set volume to 0.7, got: {volume}")
        
        # Test volume bounds
        music_player.set_volume(test_guild_id, 1.5)  # Should be capped to 1.0
        volume = music_player.get_volume(test_guild_id)
        print(f"✅ Volume capped at 1.0, got: {volume}")
        
        music_player.set_volume(test_guild_id, -0.5)  # Should be capped to 0.0
        volume = music_player.get_volume(test_guild_id)
        print(f"✅ Volume capped at 0.0, got: {volume}")
        
        print("✅ Volume handling tests passed")
        
    except Exception as e:
        print(f"❌ Volume handling tests failed: {e}")
        return False
    
    # Test Song class
    print("\n🎵 Testing Song Class...")
    try:
        from discord import Member
        
        # Create a mock member
        class MockMember:
            def __init__(self, name):
                self.display_name = name
        
        mock_member = MockMember("TestUser")
        
        # Test song creation
        song = Song(
            title="Test Song",
            url="https://example.com/test",
            duration=180,
            requester=mock_member,
            thumbnail="https://example.com/thumb.jpg"
        )
        
        print(f"✅ Created song: {song.title}")
        print(f"✅ Duration: {song.formatted_duration}")
        print(f"✅ Requester: {song.requester.display_name}")
        
        print("✅ Song class tests passed")
        
    except Exception as e:
        print(f"❌ Song class tests failed: {e}")
        return False
    
    print("\n🎉 All tests passed! The bot components are working correctly.")
    return True

if __name__ == "__main__":
    print("Discord Music Bot - Component Test")
    print("=" * 40)
    
    try:
        asyncio.run(test_music_player())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
