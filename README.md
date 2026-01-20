# 🌅 GM Bot

Automated daily GM (Good Morning) posts for X/Twitter using AI.

## Features

* 🤖 AI-generated GM posts using **Grok** (xAI's LLM)
* 📰 Incorporates current crypto news & market sentiment
* 🖼️ Random Cozy Wassie images
* 📅 Day-aware (Monday vibes, Friday energy, etc.)
* 🐦 Auto-posts via Typefully API
* 💬 Mentions @useTria naturally in posts

## Setup

### 1. Get API Keys

* **xAI API Key**: Get from [console.x.ai](https://console.x.ai)
* **Typefully API Key**: Get from Typefully settings

### 2. Add Secrets to GitHub

Go to your repository → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:
* `XAI_API_KEY` - your xAI API key
* `TYPEFULLY_API_KEY` - your Typefully API key

### 3. Add Images

Add your images to `images/gm/` folder (PNG, JPG, GIF supported)

### 4. Customize Style (Optional)

Edit `my_posts.txt` to add examples of your own posts for better style matching.

## Usage

### Automatic Posts

The bot runs automatically every day at **7:05 AM** (Romania time / EET) via GitHub Actions.

### Manual Run

1. Go to **Actions** tab in your repository
2. Select **Daily GM Post** workflow
3. Click **Run workflow**

## How It Works

1. **Fetches crypto market data** from CoinGecko
2. **Gets latest news** from CryptoPanic
3. **Generates GM tweet** using Grok AI based on:
   - Current day of the week
   - Market sentiment
   - Recent news
   - Your writing style (from `my_posts.txt`)
4. **Selects random image** from `images/gm/`
5. **Posts to X** via Typefully

## Style Guide

The bot writes in a casual, chill crypto Twitter style:
- Light sarcastic humor
- References to world events
- Lowercase writing (except day names)
- 3-4 short lines
- No hashtags
- Minimal emojis
- Natural @useTria mentions

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your keys
echo "XAI_API_KEY=your_key_here" > .env
echo "TYPEFULLY_API_KEY=your_key_here" >> .env

# Run the bot
python gm_bot.py
```

## Tech Stack

* **Python 3.11**
* **Grok API** (xAI) - AI text generation
* **Typefully API** - Social media posting
* **CoinGecko API** - Crypto market data
* **CryptoPanic API** - Crypto news
* **GitHub Actions** - Automation

## Files

* `gm_bot.py` - Main bot script
* `my_posts.txt` - Example posts for style reference
* `requirements.txt` - Python dependencies
* `.github/workflows/daily-gm.yml` - GitHub Actions workflow
* `images/gm/` - Image folder

## Why Grok?

Grok is xAI's flagship LLM that excels at:
- Witty, humorous writing
- Understanding crypto culture
- Current events knowledge
- Natural, conversational tone

Perfect for generating authentic-sounding crypto Twitter content!

## License

MIT

---

Made with ☕ and Grok
