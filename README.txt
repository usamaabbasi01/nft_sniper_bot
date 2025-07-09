NFT Sniper Bot - Setup Instructions
====================================

Welcome to the NFT Sniper Bot! This tool monitors NFT listings on OpenSea and sends Telegram alerts for high-rarity NFTs.

📋 PREREQUISITES
----------------
1. Telegram Bot Token (get from @BotFather)
2. Your Telegram User ID
3. OpenSea API Key (optional but recommended)
4. Collection information (slug and contract address)

🚀 QUICK SETUP
--------------
1. Run the NFT_Sniper_Bot.exe file
2. The program will create a ".env" file automatically
3. Edit the .env file with your settings (see example below)
4. Restart the bot to apply your configuration
5. The bot will start monitoring and send Telegram alerts

📝 CONFIGURATION (.env file)
---------------------------
The program creates a ".env" file automatically. Edit it with the following content:

COLLECTION_SLUG=your-collection-name
CONTRACT_ADDRESS=your-contract-address
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_USER_ID=your-user-id
OPENSEA_API_KEY=your-opensea-key
MIN_SCORE_THRESHOLD=100

Example:
COLLECTION_SLUG=milady
CONTRACT_ADDRESS=0x5af0d9827e0c53e4799bb226655a1de152a425a5
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_USER_ID=123456789
OPENSEA_API_KEY=your-opensea-api-key-here
MIN_SCORE_THRESHOLD=150

🔧 GETTING YOUR CREDENTIALS
---------------------------

TELEGRAM BOT TOKEN:
1. Message @BotFather on Telegram
2. Send /newbot
3. Follow instructions to create a bot
4. Copy the token (looks like: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz)

TELEGRAM USER ID:
1. Message @userinfobot on Telegram
2. It will reply with your User ID (a number like 123456789)

OPENSEA API KEY (Optional):
1. Go to https://docs.opensea.io/reference/api-overview
2. Sign up for an API key
3. Add it to your .env file for better rate limits

COLLECTION INFORMATION:
- COLLECTION_SLUG: The OpenSea collection name (e.g., "milady", "azuki")
- CONTRACT_ADDRESS: The NFT contract address (0x...)
- MIN_SCORE_THRESHOLD: Minimum rarity score to trigger alerts (default: 100)

🎯 HOW IT WORKS
---------------
1. Bot monitors new NFT listings on OpenSea
2. Calculates rarity scores based on traits
3. Sends Telegram alerts for NFTs above your threshold
4. Alerts include: NFT name, rarity score, price, and OpenSea link

⚙️ ADVANCED SETTINGS
--------------------
MIN_SCORE_THRESHOLD: Adjust based on your collection:
- High-rarity collections (BAYC, CryptoPunks): 200-300
- Medium collections (Azuki, Doodles): 80-150
- Utility-focused collections: 50-100

📱 TELEGRAM ALERTS
------------------
The bot will send alerts like:
🚨 HIGH SCORE NFT DETECTED! 🚨

🎯 Name: Milady #1234
🏆 Rarity Score: 185
💰 Price: 2.5 ETH
🔗 Link: [OpenSea URL]

Action Required: This NFT meets your rarity criteria!

🔍 TROUBLESHOOTING
------------------
❌ "Missing required configuration"
- Check your .env file exists and has all required fields
- If the .env file is missing, restart the program and it will create one

❌ "Failed to send Telegram alert"
- Verify your bot token and user ID are correct
- Make sure you've started a chat with your bot

❌ "API request failed"
- Check your internet connection
- Verify your OpenSea API key (if using one)

❌ Bot not detecting listings
- Verify collection slug and contract address
- Check if the collection has recent listings

🛡️ SECURITY NOTES
-----------------
- Keep your .env file private
- Don't share your API keys
- The bot only reads data, never modifies anything

📞 SUPPORT
----------
If you need help, contact: [Your contact information]

Version: 1.0
Last Updated: [Date] 