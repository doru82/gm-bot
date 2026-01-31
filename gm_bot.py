import os
import random
import requests
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import x_search

load_dotenv()

# ========================================
# CONFIGURATION
# ========================================

XAI_API_KEY = os.getenv("XAI_API_KEY", "")
TYPEFULLY_API_KEY = os.getenv("TYPEFULLY_API_KEY", "")

# ========================================
# GENERATE GM WITH GROK + X SEARCH
# ========================================

def generate_gm_post():
    """Generate GM post using Grok with live X search."""
    
    if not XAI_API_KEY:
        raise ValueError("XAI_API_KEY not found!")
    
    client = Client(api_key=XAI_API_KEY)
    
    now = datetime.now()
    day_name = now.strftime("%A")
    yesterday = now - timedelta(days=1)
    
    # Random Tria mention (20% chance)
    tria_instruction = ""
    if random.random() < 0.2:
        tria_instruction = "\n- Mention @useTria once, casually, like you used it for something today"
    
    prompt = f"""Search X/Twitter for the 2-3 hottest crypto topics from the last 24 hours. Look for:
- Trending narratives (AI agents, memecoins, L2s, whatever is HOT right now)
- Drama or debates
- Big launches or announcements
- What crypto twitter is actually talking about

Then write a GM post as @doruOlt about these SPECIFIC topics you found.

MY STYLE (copy this exactly):
- Use :))) not lol
- Use "lezgo" not "let's go"  
- Use "frens" not "friends"
- Use "..." for pauses, NEVER use em-dash (—)
- Lowercase mostly, except proper nouns and day names
- Self-deprecating humor
- Concrete numbers when relevant
- Projects I care about: @puffpaw, @avax, @letsCatapult, @wallchain_xyz
- Sometimes Romanian: "doamne ajuta", "hai sa mergem"
- Endings: "see ya!", "have a good one!", or just leave it

STRUCTURE (5-7 short lines, blank line between each):
- Greeting with emoji (vary it: "happy {day_name}!", "GM frens!", "hey {day_name} crew!")
- 2-3 lines about the SPECIFIC hot topics you found on X (have an opinion, reference what you actually found)
- Maybe what I'm doing today
- Short closing{tria_instruction}

HARD RULES:
- NEVER use em-dash (—), use ... instead
- NEVER sound like a news reporter
- Reference the ACTUAL trending topics you found
- NO hashtags, max 1-2 emojis

Output ONLY the post text."""

    try:
        chat = client.chat.create(
            model="grok-4-1-fast",
            tools=[
                x_search(
                    from_date=yesterday,
                    to_date=now,
                ),
            ],
        )
        
        chat.append(user(prompt))
        response = chat.sample()
        
        tweet = response.content.strip()
        tweet = tweet.strip('"').strip("'")
        tweet = tweet.replace("—", "...")
        tweet = tweet.replace("–", "...")
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
    
    with open(image_path, "rb") as f:
        file_data = f.read()
        upload_response = requests.put(upload_url, data=file_data, timeout=30)
        
        if upload_response.status_code not in [200, 201]:
            print(f"❌ Failed to upload image: {upload_response.status_code}")
            return None
    
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
    
    try:
        social_set_id = get_social_set_id()
    except Exception as e:
        print(f"❌ Failed to get social set ID: {e}")
        return
    
    print("\n📝 Generating GM post with Grok + X Search...")
    tweet = generate_gm_post()
    
    if not tweet:
        print("❌ Failed to generate tweet")
        return
    
    print("\n🖼️ Selecting random image...")
    image_path = get_random_image()
    
    media_id = None
    if image_path:
        media_id = upload_image_to_typefully(social_set_id, image_path)
    
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
