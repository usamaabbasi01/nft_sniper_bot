# import requests
# import json
# import os

# def send_telegram_alert(message):
#     token = os.getenv("TELEGRAM_BOT_TOKEN")
#     user_id = os.getenv("TELEGRAM_USER_ID")

#     if not token or not user_id:
#         print("Telegram token or user ID is missing.")
#         return

#     url = f"https://api.telegram.org/bot{token}/sendMessage"
#     data = {
#         "chat_id": user_id,
#         "text": message,
#         "parse_mode": "Markdown",
#         "disable_web_page_preview": True
#     }

#     try:
#         response = requests.post(url, data=data, timeout=10)
#         if response.status_code != 200:
#             print(f"Telegram send failed: {response.status_code} - {response.text}")
#         return response
#     except requests.exceptions.RequestException as e:
#         try:
#             print(f"Telegram alert error: {e}")
#         except UnicodeEncodeError:
#             print("Telegram alert error (encoding issue).")


# def fetch_metadata(token_id, contract_address):
#     url = f"https://api.opensea.io/api/v2/asset/{contract_address}/{token_id}"
#     headers = {"accept": "application/json"}
#     res = requests.get(url, headers=headers)
#     print(res.status_code)
#     if res.status_code == 200:
#         return res.json()
#     else:
#         print(f"Metadata fetch failed: {res.status_code}")
#         return None

# def load_traits_cache():
#     try:
#         with open("traits_cache.json", "r") as f:
#             return json.load(f)
#     except:
#         return {}

# def save_traits_cache(data):
#     with open("traits_cache.json", "w") as f:
#         json.dump(data, f, indent=2)

# def calculate_rarity_score(traits, traits_cache, total_supply):
#     score = 0.0
#     for trait in traits:
#         trait_type = trait.get("trait_type")
#         value = trait.get("value")
#         occurrence = traits_cache.get(trait_type, {}).get(value, 0)
#         if occurrence > 0:
#             rarity_percent = occurrence / total_supply
#             score += 1 / rarity_percent
#     return round(score, 2)






import requests
import json
import os
import sys
import io
from datetime import datetime

# Set UTF-8 encoding for stdout/stderr
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

def log_message(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def send_telegram_alert(message):
    """Send alert message to Telegram"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    user_id = os.getenv("TELEGRAM_USER_ID")

    if not token or not user_id:
        log_message("❌ Telegram token or user ID is missing.")
        return None

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": user_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }

    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            log_message("✅ Telegram alert sent successfully")
            return response
        else:
            log_message(f"❌ Telegram send failed: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        try:
            log_message(f"❌ Telegram alert error: {e}")
        except UnicodeEncodeError:
            log_message("❌ Telegram alert error (encoding issue).")
        return None


def fetch_metadata(token_id, contract_address):
    """Fetch NFT metadata from OpenSea API"""
    url = f"https://api.opensea.io/api/v2/asset/{contract_address}/{token_id}"
    
    headers = {
        "accept": "application/json",
        "User-Agent": "NFT-Sniper-Bot/1.0"
    }
    
    # Add API key if available
    api_key = os.getenv("OPENSEA_API_KEY")
    if api_key:
        headers["X-API-KEY"] = api_key

    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            log_message(f"✅ Metadata fetched for token {token_id}")
            return data
        elif response.status_code == 404:
            log_message(f"⚠️ Token {token_id} not found on OpenSea")
            return None
        elif response.status_code == 429:
            log_message("⚠️ Rate limited by OpenSea API - waiting before retry")
            return None
        else:
            log_message(f"❌ Metadata fetch failed: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        log_message(f"❌ Timeout fetching metadata for token {token_id}")
        return None
    except requests.exceptions.RequestException as e:
        log_message(f"❌ Network error fetching metadata: {e}")
        return None
    except json.JSONDecodeError as e:
        log_message(f"❌ Invalid JSON response for token {token_id}: {e}")
        return None


def load_traits_cache():
    """Load traits cache from file"""
    try:
        with open("traits_cache.json", "r", encoding='utf-8') as f:
            cache = json.load(f)
            log_message(f"✅ Loaded traits cache with {len(cache)} trait types")
            return cache
    except FileNotFoundError:
        log_message("ℹ️ No traits cache found - starting fresh")
        return {}
    except json.JSONDecodeError as e:
        log_message(f"❌ Error loading traits cache: {e}")
        return {}
    except Exception as e:
        log_message(f"❌ Unexpected error loading traits cache: {e}")
        return {}


def save_traits_cache(data):
    """Save traits cache to file"""
    try:
        with open("traits_cache.json", "w", encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        log_message(f"✅ Saved traits cache with {len(data)} trait types")
    except Exception as e:
        log_message(f"❌ Error saving traits cache: {e}")


def calculate_rarity_score(traits, traits_cache, total_supply):
    """Calculate rarity score for NFT based on traits"""
    if not traits:
        return 0.0
    
    score = 0.0
    trait_count = 0
    
    for trait in traits:
        trait_type = trait.get("trait_type")
        value = trait.get("value")
        
        if trait_type and value:
            occurrence = traits_cache.get(trait_type, {}).get(str(value), 0)
            if occurrence > 0:
                rarity_percent = occurrence / total_supply
                score += 1 / rarity_percent
                trait_count += 1
    
    # Normalize score by number of traits
    if trait_count > 0:
        score = score / trait_count
    
    return round(score, 2)


def build_traits_cache(collection_slug, contract_address):
    """Build traits cache for a collection"""
    log_message(f"🔧 Building traits cache for collection: {collection_slug}")
    
    url = f"https://api.opensea.io/api/v2/collection/{collection_slug}/stats"
    headers = {
        "accept": "application/json",
        "User-Agent": "NFT-Sniper-Bot/1.0"
    }
    
    api_key = os.getenv("OPENSEA_API_KEY")
    if api_key:
        headers["X-API-KEY"] = api_key
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            stats = response.json()
            total_supply = stats.get("stats", {}).get("total_supply", 0)
            log_message(f"📊 Collection total supply: {total_supply}")
            
            # This is a simplified cache building - in a real implementation,
            # you'd need to fetch all NFTs and analyze their traits
            log_message("ℹ️ Traits cache building would require fetching all NFTs")
            return {}
        else:
            log_message(f"❌ Failed to get collection stats: {response.status_code}")
            return {}
    except Exception as e:
        log_message(f"❌ Error building traits cache: {e}")
        return {}
