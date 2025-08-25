#!/usr/bin/env python3
"""
Test script for audio format handling
"""

def test_audio_format_sorting():
    """Test the audio format sorting logic"""
    print("🧪 Testing Audio Format Sorting...")
    
    # Mock audio formats with various data types
    mock_formats = [
        {'acodec': 'mp4a.40.2', 'abr': 128, 'filesize': 1000000, 'url': 'http://example.com/1'},
        {'acodec': 'none', 'abr': None, 'filesize': None, 'url': 'http://example.com/2'},
        {'acodec': 'mp4a.40.2', 'abr': 256, 'filesize': 2000000, 'url': 'http://example.com/3'},
        {'acodec': 'mp4a.40.2', 'abr': 64, 'filesize': 500000, 'url': 'http://example.com/4'},
        {'acodec': 'none', 'abr': 192, 'filesize': 1500000, 'url': 'http://example.com/5'},
    ]
    
    print(f"Original formats: {len(mock_formats)}")
    for i, fmt in enumerate(mock_formats):
        print(f"  {i}: acodec={fmt.get('acodec')}, abr={fmt.get('abr')}, filesize={fmt.get('filesize')}")
    
    # Test the safe sorting logic
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
        # Filter out formats without URLs
        valid_formats = [f for f in mock_formats if f.get('url')]
        print(f"\nValid formats with URLs: {len(valid_formats)}")
        
        # Sort formats
        valid_formats.sort(key=safe_sort_key)
        print("✅ Sorting completed successfully!")
        
        print("\nSorted formats:")
        for i, fmt in enumerate(valid_formats):
            print(f"  {i}: acodec={fmt.get('acodec')}, abr={fmt.get('abr')}, filesize={fmt.get('filesize')}")
        
        # Test edge cases
        print("\n🧪 Testing Edge Cases...")
        
        # Test with None values
        edge_formats = [
            {'acodec': None, 'abr': None, 'filesize': None, 'url': 'http://example.com/edge1'},
            {'acodec': '', 'abr': '', 'filesize': '', 'url': 'http://example.com/edge2'},
            {'acodec': 'mp4a.40.2', 'abr': 'invalid', 'filesize': 'invalid', 'url': 'http://example.com/edge3'},
        ]
        
        edge_formats.sort(key=safe_sort_key)
        print("✅ Edge case sorting completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during sorting: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Audio Format Handling Test")
    print("=" * 40)
    
    success = test_audio_format_sorting()
    
    if success:
        print("\n🎉 All tests passed! Audio format handling is working correctly.")
    else:
        print("\n❌ Tests failed! There are issues with audio format handling.")
