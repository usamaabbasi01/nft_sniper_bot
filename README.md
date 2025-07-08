# 🚀 NFT Sniper Bot

A modern desktop GUI application for monitoring NFT listings and sending alerts for high-value NFTs based on rarity scoring.

## ✨ Features

- **Modern Dark UI**: Clean, professional interface with dark theme
- **Secure Configuration**: Password-masked API keys with show/hide toggles
- **Real-time Monitoring**: Live OpenSea API monitoring with instant alerts
- **Telegram Integration**: Automatic alerts for high-value NFTs
- **Rarity Scoring**: Advanced algorithm to identify valuable NFTs
- **Live Output**: Real-time bot logs displayed in the GUI
- **Process Management**: Start/stop bot with proper cleanup

## 🛠️ Installation

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Get Required API Keys**:
   - **OpenSea API Key**: Get from [OpenSea Developer Portal](https://docs.opensea.io/reference/api-overview)
   - **Telegram Bot Token**: Create a bot via [@BotFather](https://t.me/botfather)
   - **Telegram User ID**: Get your user ID from [@userinfobot](https://t.me/userinfobot)

## 🚀 Usage

1. **Launch the Application**:
   ```bash
   python sniper_gui.py
   ```

2. **Configure Settings**:
   - **Collection Slug**: The OpenSea collection identifier (e.g., "boredapeyachtclub")
   - **Contract Address**: The NFT contract address
   - **Telegram Bot Token**: Your bot's API token
   - **Telegram User ID**: Your Telegram user ID
   - **OpenSea API Key**: Your OpenSea API key

3. **Start Monitoring**:
   - Click "▶ Start Bot" to begin monitoring
   - Watch real-time output in the terminal area
   - Receive Telegram alerts for high-value NFTs

## 📋 Configuration Fields

| Field | Description | Required |
|-------|-------------|----------|
| `COLLECTION_SLUG` | OpenSea collection identifier | ✅ |
| `CONTRACT_ADDRESS` | NFT contract address | ✅ |
| `TELEGRAM_BOT_TOKEN` | Telegram bot API token | ✅ |
| `TELEGRAM_USER_ID` | Your Telegram user ID | ✅ |
| `OPENSEA_API_KEY` | OpenSea API key | ✅ |

## 🔧 How It Works

1. **Configuration**: Settings are saved to `.env` file
2. **Monitoring**: Bot polls OpenSea API every 5 seconds
3. **Analysis**: Each NFT is scored based on trait rarity
4. **Alerts**: High-score NFTs trigger Telegram notifications
5. **Logging**: All activity is logged in real-time

## 🎯 Rarity Scoring

The bot uses an advanced algorithm to calculate NFT rarity:

- Analyzes trait combinations and frequencies
- Calculates rarity percentage for each trait
- Scores NFTs based on overall rarity
- Alerts when score exceeds threshold (default: 100)

## 📱 Telegram Alerts

When a high-value NFT is detected, you'll receive a formatted message with:

- 🎯 NFT name and token ID
- 🏆 Rarity score
- 💰 Current price in ETH
- 🔗 Direct OpenSea link
- ⚡ Action recommendation

## 🛡️ Security Features

- **Password Masking**: Sensitive fields are hidden by default
- **Show/Hide Toggle**: Reveal characters when needed
- **Secure Storage**: Configuration saved locally in `.env`
- **Error Handling**: Graceful handling of API failures

## 🔍 Troubleshooting

### Common Issues:

1. **"Missing Bot File" Error**:
   - Ensure `bot.py` is in the same directory as `sniper_gui.py`

2. **API Rate Limiting**:
   - The bot automatically handles rate limits and retries

3. **Telegram Notifications Not Working**:
   - Verify bot token and user ID are correct
   - Ensure bot is added to your chat

4. **Encoding Issues**:
   - The application handles UTF-8 encoding automatically
   - Special characters and emojis are supported

### Debug Mode:

Check the output area for detailed logs including:
- API request status
- NFT processing details
- Error messages with timestamps
- Configuration validation

## 📁 File Structure

```
nft_sniper_bot/
├── sniper_gui.py     # Main GUI application
├── bot.py            # NFT monitoring logic
├── utils.py          # Utility functions
├── requirements.txt  # Python dependencies
├── .env             # Configuration (auto-generated)
└── traits_cache.json # Rarity data (auto-generated)
```

## 🔄 Updates

The application automatically:
- Loads existing configuration from `.env`
- Validates all required fields
- Handles process cleanup on exit
- Maintains state between sessions

## ⚠️ Important Notes

- **API Limits**: Respect OpenSea API rate limits
- **Network**: Requires stable internet connection
- **Storage**: Creates cache files for performance
- **Privacy**: All data is stored locally

## 🎨 UI Features

- **Dark Theme**: Modern, eye-friendly interface
- **Responsive Layout**: Adapts to window size
- **Real-time Updates**: Live output with auto-scroll
- **Clear Controls**: Intuitive start/stop/clear buttons
- **Status Indicators**: Visual feedback for all actions

---

**Happy NFT Sniping! 🚀** 