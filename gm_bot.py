import os
import random
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ========================================
# CONFIGURATION
# ========================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
TYPEFULLY_API_KEY = os.getenv("TYPEFULLY_API_KEY", "")

# ========================================
# STYLE EXAMPLES (your actual posts)
# ========================================

STYLE_EXAMPLES = """
Example 1:
"GM
we are here atm, that means we can happily touch grass today
I'll try to do that as well, but before that, I want to remind you about a great project coming soon on Avax"

Example 2:
"happy Monday!
let's spread some good vibes like usa spreading democracy
market looks ok ish, hope this trend will last more than Madurro"

Example 3:
"2026 started yesterday, and Friday already!
Happy Friday!!!"

Example 4:
"last day of the year!!!
was a hell of a ride, but grateful to be here
grateful for everything, good, bad, friends that stayed and friend who left
happy new year, bros and sis!"

Example 5:
"GM
rest day today?
yey or ney?"

Example 6:
"GM X
have a great Saturday!"
"""

# ========================================
# FETCH CRYPTO NEWS
# ========================================

def get_crypto_news():
    """Fetch latest crypto news from CryptoPanic (free, no API key needed for basic)."""
    try:
        url = "https://cryptopanic.com/api/free/v1/posts/?public=true"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            news = []
            for item in data.get("results", [])[:5]:
                news.append(item.get("title", ""))
            return news
        return []
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []


def get_market_sentiment():
    """Get basic market data from CoinGecko (free)."""
    try:
        url = "https://api.coingecko.com/api/v3/global"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json().get("data", {})
            market_cap_change = data.get("market_cap_change_percentage_24h_usd", 0)
            
            if market_cap_change > 3:
                return "bullish", market_cap_change
            elif market_cap_change > 0:
                return "slightly up", market_cap_change
            elif market_cap_change > -3:
                return "slightly down", market_cap_change
            else:
                return "bearish", market_cap_change
        return "neutral", 0
    except Exception as e:
        print(f"Error fetching market data: {e}")
        return "neutral", 0


# ========================================
# GENERATE GM WITH GROQ
# ========================================

def generate_gm_post():
    """Generate GM post using Groq AI."""
    
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not found!")
    
    # Get current context
    now = datetime.now()
    day_name = now.strftime("%A")  # Monday, Tuesday, etc.
    
    # Get market info
    sentiment, change = get_market_sentiment()
    news = get_crypto_news()
    news_summary = "\n".join(news[:3]) if news else "No major news today"
    
    prompt = f"""You are writing a GM (good morning) tweet for a crypto Twitter account. 
The account owner is "doru" - a chill, funny crypto enthusiast who loves AVAX and uses sarcastic humor.

STYLE RULES (VERY IMPORTANT):
- Start with "GM" or "happy {day_name}!" or similar casual greeting
- Keep it SHORT: 2-4 sentences max
- Casual, friendly tone - like talking to friends
- Sometimes reference the day (Monday vibes, Friday energy, etc.)
- Light sarcastic humor is good (like comparing crypto to random world events)
- Can mention market briefly but don't be too serious about it
- Sometimes ask simple questions for engagement ("yey or ney?", "who's ready?")
- NO hashtags
- NO emojis (or max 1-2 if really fits)
- Write in lowercase mostly (casual vibe)
- End with something relatable or funny

EXAMPLES OF THE STYLE:
{STYLE_EXAMPLES}

CURRENT CONTEXT:
- Today is: {day_name}
- Date: {now.strftime("%B %d, %Y")}
- Market sentiment: {sentiment} ({change:+.1f}% 24h)
- Recent news headlines: {news_summary}

Now write ONE GM tweet in this exact style. Be creative, maybe reference something current happening in the world (politics, sports, memes) in a funny way. Keep it authentic and casual.

IMPORTANT: Output ONLY the tweet text, nothing else. No quotes, no explanation."""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 200,
        "temperature": 0.9
    }
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            tweet = data["choices"][0]["message"]["content"].strip()
            # Clean up any quotes if AI added them
            tweet = tweet.strip('"').strip("'")
            print(f"✅ Generated GM: {tweet}")
            return tweet
        else:
            print(f"❌ Groq error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None


# ========================================
# IMAGE HANDLING
# ========================================

def get_random_image():
    """Get a random image from the images/gm folder."""
    images_dir = os.path.join(os.path.dirname(__file__), "images", "gm")
    
    if not os.path.exists(images_dir):
        print(f"⚠️ Images directory not found: {images_dir}")
        return None
    
    images = [f for f in os.listdir(images_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    
    if not images:
        print("⚠️ No images found in images/gm/")
        return None
    
    selected = random.choice(images)
    image_path = os.path.join(images_dir, selected)
    print(f"📸 Selected image: {selected}")
    return image_path


def upload_image_to_typefully(social_set_id: str, image_path: str) -> str:
    """Upload image to Typefully and return media_id."""
    
    headers = {
        "Authorization": f"Bearer {TYPEFULLY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Step 1: Get upload URL
    file_name = os.path.basename(image_path)
    
    response = requests.post(
        f"https://api.typefully.com/v2/social-sets/{social_set_id}/media/upload",
        headers=headers,
        json={"file_name": file_name},
        timeout=10
    )
    
    if response.status_code not in [200, 201]:
        print(f"❌ Failed to get upload URL: {response.status_code}")
        return None
    
    data = response.json()
    media_id = data.get("media_id")
    upload_url = data.get("upload_url")
    
    # Step 2: Upload the file
    with open(image_path, "rb") as f:
        file_data = f.read()
        
        upload_response = requests.put(
            upload_url,
            data=file_data,
            timeout=30
        )
        
        if upload_response.status_code not in [200, 201]:
            print(f"❌ Failed to upload image: {upload_response.status_code}")
            return None
    
    # Step 3: Wait for processing
    import time
    for _ in range(10):
        status_response = requests.get(
            f"https://api.typefully.com/v2/social-sets/{social_set_id}/media/{media_id}",
            headers=headers,
            timeout=10
        )
        if status_response.status_code == 200:
            status_data = status_response.json()
            if status_data.get("status") == "ready":
                print(f"✅ Image uploaded: {media_id}")
                return media_id
            elif status_data.get("status") == "failed":
                print("❌ Image processing failed")
                return None
        time.sleep(1)
    
    print("⚠️ Image processing timeout, proceeding anyway")
    return media_id


# ========================================
# TYPEFULLY API
# ========================================

def get_social_set_id() -> str:
    """Get the first social set ID."""
    if not TYPEFULLY_API_KEY:
        raise ValueError("TYPEFULLY_API_KEY not found!")
    
    headers = {
        "Authorization": f"Bearer {TYPEFULLY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        "https://api.typefully.com/v2/social-sets",
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get("results") and len(data["results"]) > 0:
            social_set_id = data["results"][0]["id"]
            print(f"✅ Found social set ID: {social_set_id}")
            return str(social_set_id)
    
    raise ValueError("No social sets found!")


def post_to_typefully(social_set_id: str, tweet_text: str, media_id: str = None) -> bool:
    """Post tweet via Typefully API."""
    
    headers = {
        "Authorization": f"Bearer {TYPEFULLY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    post_content = {"text": tweet_text}
    if media_id:
        post_content["media_ids"] = [media_id]
    
    payload = {
        "platforms": {
            "x": {
                "enabled": True,
                "posts": [post_content]
            }
        },
        "publish_at": "now"
    }
    
    url = f"https://api.typefully.com/v2/social-sets/{social_set_id}/drafts"
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code in [200, 201]:
            print("✅ GM tweet posted successfully!")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


# ========================================
# MAIN
# ========================================

def run_gm_bot():
    """Main function."""
    
    print(f"🌅 GM Bot starting at {datetime.now()}\n")
    
    # 1. Get social set ID
    try:
        social_set_id = get_social_set_id()
    except Exception as e:
        print(f"❌ Failed to get social set ID: {e}")
        return
    
    # 2. Generate GM post
    print("\n📝 Generating GM post...")
    tweet = generate_gm_post()
    
    if not tweet:
        print("❌ Failed to generate tweet")
        return
    
    # 3. Get random image
    print("\n🖼️ Selecting random image...")
    image_path = get_random_image()
    
    media_id = None
    if image_path:
        media_id = upload_image_to_typefully(social_set_id, image_path)
    
    # 4. Post
    print("\n📤 Posting to X...")
    print(f"Tweet: {tweet}")
    print(f"Image: {'Yes' if media_id else 'No'}")
    
    success = post_to_typefully(social_set_id, tweet, media_id)
    
    if success:
        print(f"\n🎉 GM posted successfully at {datetime.now()}")
    else:
        print("\n❌ Failed to post GM")


if __name__ == "__main__":
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY not found!")
        exit(1)
    if not TYPEFULLY_API_KEY:
        print("❌ TYPEFULLY_API_KEY not found!")
        exit(1)
    
    run_gm_bot()
