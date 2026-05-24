# Crypto KOL AI Assistant - Telegram Bot

A powerful Telegram bot powered by AI that generates high-quality crypto content, trains on your writing style, and creates viral tweets for the crypto community.

## Features

✨ **Core Features:**
- 🤖 AI-powered content generation using DeepSeek and Grok APIs
- 📝 Multiple content modes (Viral, Meme, Professional, Alpha, etc.)
- 🎓 Style learning system - Train the AI on your writing
- 🖼️ AI image prompt generation for visual content
- 💎 Premium user system with payment integration
- 👥 Admin controls for managing users and settings
- 🗄️ SQLite database for persistent storage
- 🌍 Multi-language support (English, Bangla, Hindi, Arabic, Turkish, Spanish, Indonesian)

## Security Features

⚠️ **Important Security Notice:**
This project contains sensitive API keys. **NEVER** commit `.env` files to version control.

**What's been fixed:**
- ✅ `.gitignore` file to prevent accidental secret commits
- ✅ `.env.example` template for safe setup
- ✅ Type hints and input validation
- ✅ Proper database session management
- ✅ Comprehensive error handling

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Pintu64/KOL.git
   cd KOL
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```

5. **Edit `.env` with your credentials:**
   ```dotenv
   BOT_TOKEN=your_telegram_bot_token_here
   ADMIN_IDS=your_admin_id_here
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
   GROK_API_KEY=your_grok_api_key_here
   GROK_BASE_URL=https://api.x.ai/v1
   ```

6. **Run the bot:**
   ```bash
   python bot.py
   ```

## Configuration

### Getting API Keys

**Telegram Bot Token:**
- Message [@BotFather](https://t.me/botfather) on Telegram
- Use `/newbot` command
- Copy the provided token

**DeepSeek API Key:**
- Visit [DeepSeek API](https://platform.deepseek.com/)
- Sign up or log in
- Create an API key
- Add credits to your account

**Grok (Xai) API Key:**
- Visit [X.ai Platform](https://console.x.ai/)
- Sign up or log in
- Create an API key
- Add credits to your account

### Admin Configuration

Update the admin ID in `.env`:
```dotenv
ADMIN_IDS=your_telegram_id
```

Multiple admins:
```dotenv
ADMIN_IDS=admin_id_1,admin_id_2,admin_id_3
```

## Bot Commands

### User Commands
- `/start` - Start the bot and see available commands
- `/help` - Get detailed command information
- `/generate <mode> <topic>` - Generate crypto content (premium)
- `/train` - Start style training mode (premium)
- `/image <idea>` - Generate AI image prompt (premium)
- `/upgrade` - View premium pricing and payment instructions
- `/status` - Check your premium status

### Admin Commands (Admin only)
- `/setprice <amount>` - Set premium price in USDT
- `/setaddress <wallet>` - Set payment wallet address
- `/verify <user_id>` - Upgrade user to premium status

### Style Training
- Send tweets/content samples after `/train`
- Send `/done_training` to finish learning your style

## Content Generation Modes

Generate content with different tones and styles:

```
/generate professional Bitcoin market trends
/generate viral Solana memecoins pump
/generate meme Ethereum gas fees
/generate alpha Trading secrets
/generate emotional Crypto journey story
/generate educational DeFi basics
/generate technical Smart contract audit
/generate news Market crash reactions
/generate luxury Luxury crypto lifestyle
/generate minimal Minimalist takes
```

## Database Schema

### Users Table
```
- id: Primary key
- telegram_id: Unique Telegram user ID
- username: Telegram username
- is_premium: Boolean flag for premium status
```

### Style Samples Table
```
- id: Primary key
- user_id: Foreign key to users
- text: User's writing sample
- category: Content category (e.g., "tweet")
- timestamp: When sample was created
```

### System Settings Table
```
- id: Primary key
- premium_price: Current premium price in USDT
- payment_address: Wallet address for payments
```

## Troubleshooting

### Bot Not Responding
- ✅ Verify `BOT_TOKEN` is correct in `.env`
- ✅ Check internet connection
- ✅ Ensure bot is running: `python bot.py`

### API Errors
- ✅ Verify API keys in `.env` are valid
- ✅ Check if API services are online
- ✅ Ensure your API accounts have sufficient credits
- ✅ Check for API rate limits

### Database Errors
- ✅ Ensure `bot.db` file has proper permissions
- ✅ Delete `bot.db` to reset database (users will need to `/start` again)
- ✅ Check database file location matches your working directory

### Permission Issues
- ✅ Make sure admin ID is correctly set in `.env`
- ✅ Admin must send the command directly to the bot

## Security Best Practices

🔒 **Important:**

1. **Never commit `.env` file** - Use `.env.example` as template
2. **Rotate API keys** - If compromised, regenerate immediately
3. **Use strong passwords** - For your API accounts
4. **Monitor API usage** - Check for unauthorized access
5. **Keep dependencies updated** - Run `pip install --upgrade -r requirements.txt`
6. **Use virtual environment** - Isolate project dependencies
7. **Protect bot.db** - Don't share database files
8. **Restrict admin access** - Only trusted users as admins

## Project Structure

```
KOL/
├── bot.py              # Main bot logic and command handlers
├── ai_engine.py        # AI content generation functions
├── config.py           # Configuration and environment variables
├── database.py         # Database models and setup
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (DON'T COMMIT)
├── .env.example        # Environment template (DO COMMIT)
├── .gitignore          # Git ignore rules
├── bot.db              # SQLite database (auto-created)
└── README.md           # This file
```

## Dependencies

- **aiogram** - Telegram bot framework
- **sqlalchemy** - Database ORM
- **python-dotenv** - Environment variable management
- **openai** - OpenAI SDK (compatible with DeepSeek and Grok)
- **chromadb** - Vector database for embeddings
- **sentence-transformers** - Text embeddings

See `requirements.txt` for specific versions.

## Performance Tips

⚡ **Optimization:**

1. Use `/done_training` after collecting 5-10 style samples
2. Generation works best with specific topics (not too vague)
3. Premium price recommendation: $49-99 USDT
4. Backup `bot.db` regularly for data safety
5. Clear old style samples periodically to improve performance

## API Limits

- **DeepSeek:** Check your plan limits at [platform.deepseek.com](https://platform.deepseek.com/)
- **Grok:** Check your plan limits at [console.x.ai](https://console.x.ai/)
- **Telegram:** Rate limited by default, respects bot token rules

## Contributing

Feel free to submit issues and enhancement requests!

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review error messages carefully
3. Ensure `.env` is properly configured
4. Verify all API keys are active

## License

This project is provided as-is. Use responsibly.

## Disclaimer

⚠️ **Important:**
- This bot generates AI content - Always review before publishing
- Respect copyright and intellectual property laws
- Don't use for spam or malicious purposes
- API usage is your responsibility and cost
- Keep your API keys secure at all times

---

**Created:** May 2026
**Last Updated:** May 24, 2026
