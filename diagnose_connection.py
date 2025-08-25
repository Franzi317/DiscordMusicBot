#!/usr/bin/env python3
"""
Discord Connection Diagnostic Tool
Helps troubleshoot connectivity issues with Discord servers
"""

import asyncio
import aiohttp
import requests
import socket
import ssl
import json
from datetime import datetime

def test_basic_connectivity():
    """Test basic internet connectivity"""
    print("🌐 Testing Basic Internet Connectivity...")
    
    # Test DNS resolution
    try:
        ip = socket.gethostbyname("discord.com")
        print(f"✅ DNS Resolution: discord.com -> {ip}")
    except socket.gaierror as e:
        print(f"❌ DNS Resolution failed: {e}")
        return False
    
    # Test basic ping (simulated)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(("discord.com", 443))
        sock.close()
        
        if result == 0:
            print("✅ Port 443 (HTTPS) - Accessible")
        else:
            print(f"❌ Port 443 (HTTPS) - Blocked (error code: {result})")
            return False
    except Exception as e:
        print(f"❌ Port test failed: {e}")
        return False
    
    return True

def test_discord_endpoints_sync():
    """Test Discord endpoints using synchronous requests"""
    print("\n🔍 Testing Discord Endpoints (Synchronous)...")
    
    endpoints = [
        ("Gateway", "https://discord.com/api/v10/gateway"),
        ("Status API", "https://status.discord.com/api/v2/status.json"),
        ("CDN", "https://cdn.discordapp.com/"),
    ]
    
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: OK (Status: {response.status_code})")
            else:
                print(f"⚠️  {name}: Status {response.status_code}")
        except requests.exceptions.Timeout:
            print(f"⏰ {name}: Timeout")
        except requests.exceptions.ConnectionError as e:
            print(f"❌ {name}: Connection Error - {e}")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")

async def test_discord_endpoints_async():
    """Test Discord endpoints using asynchronous requests"""
    print("\n🔍 Testing Discord Endpoints (Asynchronous)...")
    
    endpoints = [
        ("Gateway", "https://discord.com/api/v10/gateway"),
        ("Status API", "https://status.discord.com/api/v2/status.json"),
        ("CDN", "https://cdn.discordapp.com/"),
    ]
    
    async with aiohttp.ClientSession() as session:
        for name, url in endpoints:
            try:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        print(f"✅ {name}: OK (Status: {response.status})")
                    else:
                        print(f"⚠️  {name}: Status {response.status}")
            except asyncio.TimeoutError:
                print(f"⏰ {name}: Timeout")
            except aiohttp.ClientError as e:
                print(f"❌ {name}: Client Error - {e}")
            except Exception as e:
                print(f"❌ {name}: Error - {e}")

def test_ssl_connection():
    """Test SSL connection to Discord"""
    print("\n🔒 Testing SSL Connection...")
    
    try:
        context = ssl.create_default_context()
        with socket.create_connection(("discord.com", 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname="discord.com") as ssock:
                cert = ssock.getpeercert()
                print(f"✅ SSL Connection: OK")
                print(f"   Certificate Subject: {cert.get('subject', 'Unknown')}")
                print(f"   Valid Until: {cert.get('notAfter', 'Unknown')}")
    except Exception as e:
        print(f"❌ SSL Connection failed: {e}")

def check_discord_status():
    """Check Discord's official status"""
    print("\n📊 Checking Discord Status...")
    
    try:
        response = requests.get("https://status.discord.com/api/v2/status.json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', {})
            print(f"✅ Discord Status: {status.get('indicator', 'Unknown')}")
            print(f"   Description: {status.get('description', 'No description')}")
        else:
            print(f"⚠️  Could not fetch Discord status (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Failed to check Discord status: {e}")

def main():
    """Main diagnostic function"""
    print("Discord Connection Diagnostic Tool")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test basic connectivity first
    if not test_basic_connectivity():
        print("\n❌ Basic connectivity test failed. Check your internet connection.")
        return
    
    # Test SSL
    test_ssl_connection()
    
    # Test Discord endpoints synchronously
    test_discord_endpoints_sync()
    
    # Test Discord endpoints asynchronously
    try:
        asyncio.run(test_discord_endpoints_async())
    except Exception as e:
        print(f"❌ Async test failed: {e}")
    
    # Check Discord status
    check_discord_status()
    
    print("\n" + "=" * 50)
    print("Diagnostic completed!")
    print("\nIf you're still having issues:")
    print("1. Check https://status.discord.com/ for Discord outages")
    print("2. Try using a different network (mobile hotspot, etc.)")
    print("3. Check if your firewall/antivirus is blocking Discord")
    print("4. Try running the bot again in a few minutes")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Diagnostic interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()
