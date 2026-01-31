import os
import random
import requests
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ========================================
# CONFIGURATION
# ========================================

XAI_API_KEY = os.getenv("XAI_API_KEY", "")
TYPEFULLY_API_KEY = os.getenv("TYPEFULLY_API_KEY", "")

# ========================================
# LOAD MY POSTS (for style reference)
# ========================================

def load_my_posts():
    """Load posts from my_posts.txt for style reference."""
    posts_file = os.path.join(os.path.dirname(__file__), "my_posts.txt")
    
    if os.path.exists(posts_file):
        with open(posts_file, "r", encoding="utf-8") as f:
            content = f.read()
            posts = content.split("---")
            posts = [p.strip() for p in posts if p.strip()]
            print(f"📝 Loaded {len(posts)} example posts from my_posts.txt")
            return posts
    else:
        print("⚠️ my_posts.txt not found, using default examples")
        return []

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
# GENERATE GM WITH GROK
# ========================================

def generate_gm_post():
    """Generate GM post using Grok (xAI) API."""
    
    if not XAI_API_KEY:
        raise ValueError("XAI_API_KEY not found!")
    
    client = OpenAI(
        api_key=XAI_API_KEY,
        base_url="https://api.x.ai/v1"
    )
    
    now = datetime.now()
    day_name = now.strftime("%A")
    
    # Load my posts for style reference
    my_posts = load_my_posts()
    if my_posts:
        sample_posts = random.sample(my_posts, min(10, len(my_posts)))
        style_examples = "\n\n---\n\n".join(sample_posts)
    else:
        style_examples = ""
    
    # Random Tria mention (20% chance)
    tria_instruction = ""
    if random.random() < 0.2:
        tria_instruction = "Somewhere in the post, mention @useTria casually - like you used it for something (coffee, lunch, shopping, whatever fits naturally). Don't force it."
    
    prompt = f"""Look at Crypto Twitter from the last 24 hours. What are the 2-3 hottest topics people are actually talking about? Could be drama, launches, market moves, memes, debates - whatever CT is buzzing about RIGHT NOW.

Write a GM post about it in MY style. Study these examples of how I write:

{style_examples}

MY STYLE:
- Casual, talking to friends not an audience
- Short lines with blank lines between them
- Lowercase mostly (except proper nouns)
- Light humor, self-aware, not tryhard
- I have opinions but I'm chill about them
- Simple words, no crypto jargon flex
- Sometimes I ask what others think, sometimes I don't
- NO hashtags, minimal emojis (0-1)

TODAY: {day_name}, {now.strftime("%B %d")}

{tria_instruction}

IMPORTANT:
- Talk about what's ACTUALLY happening on CT right now
- Have a take on it, don't just summarize
- Vary the structure - don't always start with "gm", don't always end with a question
- 4-7 lines max, each separated by blank line

Output ONLY the post. No quotes, no explanation."""

    try:
        response = client.chat.completions.create(
            model="grok-3-latest",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.9
        )
        
        tweet = response.choices[0].message.content.strip()
        tweet = tweet.strip('"').strip("'")
        lines = [line.strip() for line in tweet.split('\n') if line.strip()]
        tweet = '\n\n'.join(lines)
        print(f"✅ Generated GM: {tweet}")
        return tweet
            
    except Exception as e:
        print(f"❌ Grok API error: {e}")
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
        #"publish_at": "now"
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
    print("\n📝 Generating GM post with Grok...")
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
    if not XAI_API_KEY:
        print("❌ XAI_API_KEY not found!")
        exit(1)
    if not TYPEFULLY_API_KEY:
        print("❌ TYPEFULLY_API_KEY not found!")
        exit(1)
    
    run_gm_bot()
