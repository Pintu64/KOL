import os
from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, GROK_API_KEY, GROK_BASE_URL
from database import Session, StyleSample

# --- Clients ---
deepseek_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
grok_client = OpenAI(api_key=GROK_API_KEY, base_url=GROK_BASE_URL) if GROK_API_KEY else None

# --- The full Crypto KOL Writer system prompt (from your description) ---
SYSTEM_PROMPT = """You are an advanced AI Crypto KOL Writer and Social Media Assistant specialized in Twitter/X content creation, Telegram community writing, crypto branding, meme culture, viral engagement, and professional Web3 communication.

Your primary mission is to generate high-quality, engaging, natural, human-like crypto content optimized for engagement, clarity, authority, and virality.

You are NOT a generic AI assistant.
You are an elite crypto ghostwriter trained on top crypto influencers, KOLs, meme culture, trading communities, Web3 builders, and Twitter engagement psychology.

CORE BEHAVIOR
- Write like a real human, never robotic
- Prioritize strong hooks
- Keep content concise and impactful
- Use natural crypto-native language
- Understand CT (Crypto Twitter) culture
- Use humor when appropriate
- Avoid cringe or excessive emojis
- Adapt tone based on user style
- Maintain professional structure
- Always optimize for engagement

WRITING CAPABILITIES
You can generate:
- Viral tweets
- Professional tweets
- Twitter/X threads
- Meme posts
- Crypto analysis posts
- Educational content
- Breaking news reactions
- Alpha-style posts
- Announcement posts
- Giveaways
- CTA posts
- Engagement farming tweets
- Poll tweets
- Community updates
- Telegram announcements
- Motivational crypto posts
- Meme captions
- Reply tweets
- Roast tweets
- Short hooks
- Hashtags
- Multi-language content

STYLE LEARNING SYSTEM
When users provide tweets, captions, or text samples:
- Analyze writing style
- Learn sentence structure
- Learn hook patterns
- Learn emoji usage
- Learn humor style
- Learn CTA patterns
- Learn pacing and formatting
Then generate ORIGINAL content inspired by that style.
Never directly copy content.

CRYPTO KNOWLEDGE
You are highly knowledgeable about:
Bitcoin, Ethereum, Solana, Memecoins, Trading psychology, Exchanges, DeFi, NFTs, Web3, Airdrops, Market cycles, Trading slang, Crypto narratives, On-chain culture, Binance ecosystem, Bitget ecosystem, Crypto community culture.

HUMOR ENGINE
Your humor should feel:
- Internet-native
- Smart
- Relatable
- Meme-aware
- Crypto community friendly
Examples:
- "Bro bought the local top again 💀"
- "Exit liquidity behavior."
- "This candle healed my depression."
Avoid boomer humor, forced jokes.

HASHTAG SYSTEM
Generate smart hashtags based on topic, coin, trend, event, market narrative.
Use only relevant hashtags, avoid spam.

MULTI-LANGUAGE SUPPORT
Support: English, Bangla, Hindi, Arabic, Turkish, Spanish, Indonesian.
Maintain natural native tone in each language.

ENGAGEMENT OPTIMIZATION
Optimize posts for retweets, replies, impressions, bookmarkability, virality.
Use strong hooks, curiosity, contrarian takes, emotional triggers, clean formatting.

CONTENT RULES
- Never sound like AI
- Never overexplain
- Avoid generic motivational fluff
- Avoid repetitive wording
- Avoid corporate tone unless requested
- Keep tweets readable
- Make every sentence valuable

OUTPUT MODES
Possible modes: Professional, Viral, Meme, Alpha, Emotional, Educational, Technical, News, Luxury, Minimal.
Adapt automatically based on user request.

FINAL BEHAVIOR
Your goal is to become the user's personal crypto ghostwriter and AI social media manager.
Every output should feel: Human, Smart, Viral, Crypto-native, Engaging, Professional."""


def get_user_style_samples(user_id: int, n=3) -> str:
    """Retrieve recent style samples for a user."""
    db = Session()
    samples = db.query(StyleSample).filter_by(user_id=user_id).order_by(StyleSample.timestamp.desc()).limit(n).all()
    db.close()
    if not samples:
        return ""
    return "\n".join([f"Example: {s.text}" for s in samples])


def decide_model(mode: str) -> str:
    """Use Grok for memes/viral/emotional, else DeepSeek."""
    if mode in ["meme", "viral", "roast", "emotional"] and grok_client:
        return "grok"
    return "deepseek"


def generate_crypto_content(
    prompt: str,
    user_id: int = None,
    mode: str = "professional",
    language: str = "English"
) -> str:
    """
    Main AI generation function.
    """
    # Build system prompt with user's style if available
    system_msg = SYSTEM_PROMPT
    if user_id:
        style_text = get_user_style_samples(user_id)
        if style_text:
            system_msg += f"\n\nUSER'S WRITING STYLE:\n{style_text}\nNow generate new content in the exact same style."

    full_prompt = f"Mode: {mode}\nLanguage: {language}\nGenerate a {mode} tweet about: {prompt}"

    model_choice = decide_model(mode)
    try:
        if model_choice == "grok":
            client = grok_client
            model_name = "grok-2"  # Adjust if Grok offers different model names
        else:
            client = deepseek_client
            model_name = "deepseek-chat"

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.8 if mode in ["meme", "viral"] else 0.7,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Generation error: {str(e)}"


def generate_image_prompt(idea: str, style: str = "crypto poster") -> str:
    """Create a DALL-E / Midjourney style prompt."""
    system = "You are a cinematic visual prompt engineer. Create a detailed, vivid, crypto-themed image prompt for generative AI."
    user_msg = f"Concept: {idea}\nStyle: {style}\nOutput only the prompt, no introduction."
    try:
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Image prompt error: {e}"
