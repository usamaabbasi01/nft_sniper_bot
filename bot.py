import asyncio
import aiohttp
import os
import sys
import io
from datetime import datetime
from dotenv import load_dotenv
from utils import (
    send_telegram_alert,
    fetch_metadata,
    load_traits_cache,
    save_traits_cache,
    calculate_rarity_score
)

# Set UTF-8 encoding for stdout/stderr
# sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
# sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

load_dotenv()

COLLECTION_SLUG = os.getenv("COLLECTION_SLUG")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")
OPENSEA_API_KEY = os.getenv("OPENSEA_API_KEY")

# Collection-specific score thresholds
COLLECTION_THRESHOLDS = {
    # PFP Collections (High rarity focus)
    "milady": 150,      # Milady is very rarity-focused
    "azuki": 120,       # Azuki has high floor, need higher rarity
    "doodles": 80,      # Doodles are more floor-focused
    "bayc": 200,        # BAYC has very high rarity premiums
    "cryptopunks": 300, # CryptoPunks have extreme rarity values
    "cool-cats": 100,   # Cool Cats - moderate rarity
    "moonbirds": 180,   # Moonbirds - high rarity focus
    "veefriends": 90,   # VeeFriends - moderate rarity
    
    # Generative Art (Medium-high rarity)
    "art-blocks": 200,  # Art Blocks - artistic rarity
    "chromie-squig": 150, # Chromie Squig
    "fidenza": 250,     # Fidenza - very rare
    
    # Gaming/Metaverse (Lower rarity, utility-focused)
    "axie": 50,         # Axie Infinity - utility > rarity
    "sandbox": 60,      # The Sandbox
    "decentraland": 70, # Decentraland
    
    # Photography/Art (Very high rarity)
    "beeple": 500,      # Beeple works - extremely rare
    "pak": 400,         # Pak works
    "xcopy": 450,       # XCOPY works
    
    # Music/Audio (Medium rarity)
    "audius": 100,      # Audius
    "catalog": 120,     # Catalog
    
    # Domain/Name (Low rarity, utility-focused)
    "ens": 30,          # ENS domains
    "unstoppable": 40,  # Unstoppable Domains
    
    # Meme/Community (Variable)
    "pepe": 80,         # Pepe - community-driven
    "wojak": 70,        # Wojak
    
    # Default for unknown collections
    "default": 100
}

# Get threshold for current collection
def get_score_threshold(collection_slug):
    """Get the appropriate score threshold for a collection"""
    # Try exact match first
    if collection_slug in COLLECTION_THRESHOLDS:
        return COLLECTION_THRESHOLDS[collection_slug]
    
    # Try partial matches (e.g., "milady-maker" matches "milady")
    for key in COLLECTION_THRESHOLDS:
        if key in collection_slug.lower():
            return COLLECTION_THRESHOLDS[key]
    
    # Return default if no match found
    return COLLECTION_THRESHOLDS["default"]

# Get threshold from environment or use collection-specific default
env_threshold = os.getenv("MIN_SCORE_THRESHOLD")
if env_threshold:
    try:
        MIN_SCORE_THRESHOLD = int(env_threshold)
    except ValueError:
        MIN_SCORE_THRESHOLD = get_score_threshold(COLLECTION_SLUG)
else:
    MIN_SCORE_THRESHOLD = get_score_threshold(COLLECTION_SLUG)

TOTAL_SUPPLY = 4269

def log_message(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def validate_config():
    """Validate that all required configuration is present"""
    required_vars = {
        "COLLECTION_SLUG": COLLECTION_SLUG,
        "CONTRACT_ADDRESS": CONTRACT_ADDRESS,
        "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
        "TELEGRAM_USER_ID": TELEGRAM_USER_ID,
        "OPENSEA_API_KEY": OPENSEA_API_KEY
    }
    
    missing = [key for key, value in required_vars.items() if not value]
    
    if missing:
        log_message(f"❌ Missing required configuration: {', '.join(missing)}")
        log_message("Please check your .env file and restart the bot.")
        return False
    
    log_message("✅ All configuration validated successfully")
    log_message(f"🎯 Using score threshold: {MIN_SCORE_THRESHOLD}")
    return True

async def monitor_listings():
    seen = set()
    traits_cache = load_traits_cache()
    
    if not validate_config():
        return

    OPENSEA_EVENTS = "https://api.opensea.io/api/v2/events"
    params = {
        "event_type": "item_listed",
        "collection_slug": COLLECTION_SLUG,
        "limit": 25
    }

    headers = {
        "accept": "application/json"
    }
    
    if OPENSEA_API_KEY:
        headers["X-API-KEY"] = OPENSEA_API_KEY

    log_message("🚀 NFT Sniper Bot starting...")
    log_message(f"📊 Monitoring collection: {COLLECTION_SLUG}")
    log_message(f"🎯 Contract address: {CONTRACT_ADDRESS}")
    log_message(f"📈 Minimum score threshold: {MIN_SCORE_THRESHOLD}")
    log_message("=" * 60)

    try:
        send_telegram_alert("🤖 NFT Sniper Bot is now running and watching listings.")
        log_message("📱 Telegram alert sent: Bot is active")
    except Exception as e:
        log_message(f"⚠️ Failed to send Telegram startup alert: {e}")

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                log_message("🔍 Checking for new listings...")
                
                async with session.get(OPENSEA_EVENTS, params=params, headers=headers) as resp:
                    if resp.status != 200:
                        log_message(f"❌ API request failed: {resp.status} - {await resp.text()}")
                        await asyncio.sleep(10)
                        continue
                    
                    data = await resp.json()
                    log_message(f"📡 Received {len(data.get('asset_events', []))} events")

                    for event in data.get("asset_events", []):
                        if event.get("event_type") != "order":
                            continue
                        if event.get("order_type") != "listing":
                            continue
                        
                        asset = event.get("asset", {})
                        token_id = asset.get("identifier") or asset.get("token_id")
                        name = asset.get("name", f"Token #{token_id}")
                        
                        starting_price = event.get("payment", {}).get("quantity") or event.get("starting_price")
                        if starting_price is None:
                            continue

                        price_eth = float(starting_price) / (10 ** 18)
                        permalink = asset.get("opensea_url") or asset.get("permalink")
                        
                        # Check if we've already processed this listing
                        listing_id = f"{token_id}_{price_eth}"
                        if listing_id in seen:
                            continue
                        
                        seen.add(listing_id)
                        log_message(f"🆕 New listing: {name} - {price_eth:.4f} ETH")

                        # Fetch the metadata
                        try:
                            metadata = fetch_metadata(token_id, CONTRACT_ADDRESS)
                            if metadata:
                                traits = metadata.get("traits", [])
                                score = calculate_rarity_score(traits, traits_cache, TOTAL_SUPPLY)
                                
                                log_message(f"📊 {name} - Rarity Score: {score}")

                                # If the score is above the threshold, send an alert
                                if score >= MIN_SCORE_THRESHOLD:
                                    alert_message = f"""🚨 **HIGH SCORE NFT DETECTED!** 🚨

🎯 **Name:** {name}
🏆 **Rarity Score:** {score}
💰 **Price:** {price_eth:.4f} ETH
🔗 **Link:** {permalink}

⚡ **Action Required:** This NFT meets your rarity criteria!"""
                                    
                                    try:
                                        send_telegram_alert(alert_message)
                                        log_message(f"🚨 ALERT SENT: {name} (Score: {score})")
                                    except Exception as e:
                                        log_message(f"❌ Failed to send Telegram alert: {e}")
                            else:
                                log_message(f"⚠️ Could not fetch metadata for {name}")
                                
                        except Exception as e:
                            log_message(f"❌ Error processing {name}: {e}")

                await asyncio.sleep(5)

            except aiohttp.ClientError as e:
                log_message(f"❌ Network error: {e}")
                await asyncio.sleep(10)
            except Exception as e:
                log_message(f"❌ Unexpected error: {e}")
                await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        asyncio.run(monitor_listings())
    except KeyboardInterrupt:
        log_message("🛑 Bot stopped by user")
    except Exception as e:
        log_message(f"💥 Fatal error: {e}")
        sys.exit(1)
