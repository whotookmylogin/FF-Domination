#!/usr/bin/env python3
"""
Script to update ESPN cookies from your browser
Run this after logging into ESPN in your browser
"""

import os
import json
import sqlite3
import platform
from pathlib import Path

def get_chrome_cookies():
    """Extract ESPN cookies from Chrome browser"""
    
    # Find Chrome cookies database based on OS
    system = platform.system()
    if system == "Darwin":  # macOS
        cookie_path = Path.home() / "Library/Application Support/Google/Chrome/Default/Cookies"
    elif system == "Linux":
        cookie_path = Path.home() / ".config/google-chrome/Default/Cookies"
    elif system == "Windows":
        cookie_path = Path.home() / "AppData/Local/Google/Chrome/User Data/Default/Cookies"
    else:
        print(f"Unsupported OS: {system}")
        return None
    
    if not cookie_path.exists():
        print(f"Chrome cookies not found at: {cookie_path}")
        return None
    
    # Connect to Chrome's cookie database
    conn = sqlite3.connect(str(cookie_path))
    cursor = conn.cursor()
    
    # Get ESPN cookies
    cursor.execute("""
        SELECT name, value 
        FROM cookies 
        WHERE host_key LIKE '%espn.com%'
        AND (name = 'espn_s2' OR name = 'SWID')
    """)
    
    cookies = {}
    for name, value in cursor.fetchall():
        cookies[name] = value
    
    conn.close()
    return cookies

def get_safari_cookies():
    """Extract ESPN cookies from Safari (macOS only)"""
    if platform.system() != "Darwin":
        return None
    
    cookie_path = Path.home() / "Library/Cookies/Cookies.binarycookies"
    
    # Note: Safari cookies are in a binary format that's harder to parse
    # This would require additional libraries or manual extraction
    print("Safari cookie extraction requires manual copy from browser Developer Tools")
    print("1. Open Safari")
    print("2. Go to ESPN Fantasy and log in")
    print("3. Open Developer Tools (Cmd+Option+I)")
    print("4. Go to Storage > Cookies")
    print("5. Copy the espn_s2 and SWID values")
    return None

def update_env_file(cookies):
    """Update .env file with new ESPN cookies"""
    env_path = Path(".env")
    
    if not cookies:
        print("No cookies found")
        return
    
    # Format cookie string
    cookie_parts = []
    if 'espn_s2' in cookies:
        cookie_parts.append(f"espn_s2={cookies['espn_s2']}")
    if 'SWID' in cookies:
        cookie_parts.append(f"SWID={cookies['SWID']}")
    
    if not cookie_parts:
        print("Required ESPN cookies not found")
        return
    
    cookie_string = "; ".join(cookie_parts)
    
    # Read existing .env
    if env_path.exists():
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Update ESPN_COOKIE line
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('ESPN_COOKIE='):
                lines[i] = f'ESPN_COOKIE={cookie_string}\n'
                updated = True
                break
        
        if not updated:
            lines.append(f'\nESPN_COOKIE={cookie_string}\n')
        
        # Write back
        with open(env_path, 'w') as f:
            f.writelines(lines)
    else:
        # Create new .env
        with open(env_path, 'w') as f:
            f.write(f'ESPN_COOKIE={cookie_string}\n')
    
    print(f"✅ Updated ESPN cookies in .env file")
    print(f"Cookie string: {cookie_string[:50]}...")

def main():
    print("ESPN Cookie Updater")
    print("=" * 50)
    print("\nAttempting to extract ESPN cookies from your browser...")
    
    # Try Chrome first
    cookies = get_chrome_cookies()
    
    if not cookies:
        print("\nCouldn't extract cookies automatically.")
        print("\nManual method:")
        print("1. Log into ESPN Fantasy in your browser")
        print("2. Open Developer Tools (F12)")
        print("3. Go to Application/Storage > Cookies")
        print("4. Find and copy these values:")
        print("   - espn_s2")
        print("   - SWID")
        print("\n5. Paste them here:")
        
        espn_s2 = input("espn_s2 value: ").strip()
        swid = input("SWID value (include brackets): ").strip()
        
        if espn_s2 and swid:
            cookies = {'espn_s2': espn_s2, 'SWID': swid}
    
    if cookies:
        update_env_file(cookies)
        print("\n✅ Cookies updated successfully!")
        print("Restart the backend server to use new cookies")
    else:
        print("\n❌ No cookies to update")

if __name__ == "__main__":
    main()