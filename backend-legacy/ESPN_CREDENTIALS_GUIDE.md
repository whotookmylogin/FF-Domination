# ESPN Fantasy Football Credentials Guide

This guide explains how to obtain and use ESPN credentials for accessing your private fantasy football league data.

## Why ESPN Credentials Are Needed

ESPN requires authentication to access private fantasy league data. Without proper credentials, you can only access publicly available information. This app provides mock data when credentials are not available, but for real league data, you'll need to provide your ESPN session cookies.

## What You Need

To access your ESPN fantasy football data, you need two cookie values:

1. **espn_s2** - ESPN session cookie
2. **SWID** - ESPN signed user ID cookie

## How to Get ESPN Credentials

### Method 1: Using Browser Developer Tools (Recommended)

1. **Log into ESPN Fantasy Football**
   - Open your web browser
   - Go to [fantasy.espn.com](https://fantasy.espn.com)
   - Log into your account
   - Navigate to your fantasy football league

2. **Open Developer Tools**
   - **Chrome/Edge**: Press `F12` or right-click and select "Inspect"
   - **Firefox**: Press `F12` or right-click and select "Inspect Element"
   - **Safari**: Enable Developer menu in Safari > Preferences > Advanced, then press `F12`

3. **Find Your Cookies**
   - Click on the **Application** tab (Chrome) or **Storage** tab (Firefox)
   - In the left sidebar, expand **Cookies**
   - Click on `https://fantasy.espn.com`
   - Look for these two cookies:
     - `espn_s2` - Copy the entire value
     - `SWID` - Copy the entire value (including the curly braces {})

4. **Format Your Cookie String**
   - Combine both values like this:
   ```
   espn_s2=YOUR_ESPN_S2_VALUE_HERE; SWID=YOUR_SWID_VALUE_HERE
   ```

### Method 2: Using Browser Network Tab

1. **Log into ESPN** and navigate to your league
2. **Open Developer Tools** and go to the **Network** tab
3. **Reload the page** or navigate to a different section of your league
4. **Find ESPN API requests** - look for requests to `fantasy.espn.com`
5. **Check request headers** - look for the `Cookie` header
6. **Extract the values** for `espn_s2` and `SWID`

## Setting Up Credentials

### Option 1: Environment Variables (Recommended)

Set these environment variables:

```bash
# Full cookie string (preferred method)
export ESPN_COOKIE="espn_s2=YOUR_ESPN_S2_VALUE; SWID=YOUR_SWID_VALUE"

# Individual values (alternative method)
export ESPN_S2="YOUR_ESPN_S2_VALUE"
export SWID="YOUR_SWID_VALUE"

# Your league ID (optional, defaults to 83806)
export ESPN_LEAGUE_ID="YOUR_LEAGUE_ID"
```

### Option 2: Direct Initialization

```python
from src.platforms.service import PlatformIntegrationService

# Initialize with cookie string
espn_cookie = "espn_s2=YOUR_ESPN_S2_VALUE; SWID=YOUR_SWID_VALUE"
platform_service = PlatformIntegrationService(espn_cookie=espn_cookie)
```

## Finding Your League ID

Your ESPN league ID can be found in the URL when viewing your league:
```
https://fantasy.espn.com/football/league?leagueId=123456789
```
The number after `leagueId=` is your league ID (123456789 in this example).

## Testing Your Credentials

Run the comprehensive test script to verify your credentials work:

```bash
python test_espn_complete.py
```

This will test all ESPN integration methods and provide detailed feedback.

## Important Security Notes

⚠️ **Keep Your Credentials Secure**

- **Never commit credentials to version control** - use environment variables or a `.env` file that's gitignored
- **Credentials expire** - ESPN session cookies typically expire after some time, requiring you to get new ones
- **Private league access only** - these credentials only work for leagues you're a member of
- **Don't share credentials** - each user needs their own ESPN session cookies

## Common Issues and Solutions

### Problem: "ESPN API access denied with status 401/403"
**Solution**: Your credentials have expired or are incorrect. Follow the steps above to get new credentials.

### Problem: "No data returned from ESPN"
**Solution**: 
1. Verify your league ID is correct
2. Make sure you're a member of the league you're trying to access
3. Check that your credentials are properly formatted

### Problem: "ESPN API may have changed access requirements"
**Solution**: ESPN occasionally implements anti-bot measures or changes their API. Try:
1. Getting fresh credentials
2. Waiting a few minutes before retrying
3. Using the app's mock data mode for development

## Mock Data Mode

If you can't or don't want to provide ESPN credentials, the app will automatically use realistic mock data:

```python
# Initialize without credentials - will use mock data
platform_service = PlatformIntegrationService()
```

Mock data includes:
- Realistic fantasy team rosters
- Sample transactions and trades
- Player statistics and information
- League standings and records

## Credential Formats

### Valid ESPN_COOKIE formats:
```bash
# Full format with both cookies
"espn_s2=VALUE1; SWID=VALUE2"

# With additional cookies (other cookies will be included)
"other_cookie=value; espn_s2=VALUE1; SWID=VALUE2; another_cookie=value"
```

### Valid individual formats:
```bash
ESPN_S2="AE..."  # Just the value, no 'espn_s2=' prefix
SWID="{12345...}"  # Include the curly braces if present
```

## Support

If you continue having issues with ESPN credentials:

1. **Check the test output** - run `python test_espn_complete.py` for detailed diagnostics
2. **Verify browser login** - ensure you can access your league data in a web browser
3. **Try fresh credentials** - logout and login again to get new session cookies
4. **Use mock data mode** - for development and testing, mock data provides all necessary functionality

## Legal and Ethical Considerations

- Only access leagues you're a legitimate member of
- Respect ESPN's terms of service
- Don't make excessive API requests (the integration includes rate limiting)
- Use this for personal fantasy football management only

---

*This integration is for personal use only and is not affiliated with ESPN. Always respect the terms of service of any platform you're accessing.*