import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from contextlib import suppress
from database import Session, User, SystemSettings, StyleSample
from config import BOT_TOKEN, ADMIN_IDS
from ai_engine import generate_crypto_content, generate_image_prompt

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ---------- Helpers ----------
def get_db():
    return Session()

def get_user(telegram_id: int):
    db = get_db()
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    db.close()
    return user

def get_settings():
    db = get_db()
    settings = db.query(SystemSettings).first()
    if not settings:
        settings = SystemSettings()
        db.add(settings)
        db.commit()
    db.close()
    return settings

def is_admin(telegram_id: int) -> bool:
    return telegram_id in ADMIN_IDS

def require_admin(func):
    async def wrapper(message: types.Message, *args, **kwargs):
        if not is_admin(message.from_user.id):
            await message.answer("⛔ Admin only.")
            return
        return await func(message, *args, **kwargs)
    return wrapper

# ---------- FSM for style training ----------
class Training(StatesGroup):
    collecting = State()

# ---------- Middleware: auto-register users ----------
@dp.message()
async def auto_register(message: types.Message):
    db = get_db()
    existing = db.query(User).filter_by(telegram_id=message.from_user.id).first()
    if not existing:
        new_user = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username
        )
        db.add(new_user)
        db.commit()
    db.close()

# ---------- Premium check middleware ----------
from aiogram import BaseMiddleware
class PremiumGateMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: types.Message, data: dict):
        # Gate only commands that require premium
        premium_commands = ['/generate', '/image', '/train']
        text = event.text or ''
        if any(text.startswith(cmd) for cmd in premium_commands):
            user = get_user(event.from_user.id)
            if not user or not user.is_premium:
                await event.answer("❌ This is a premium feature.\nUse /upgrade to unlock.")
                return
        return await handler(event, data)

dp.message.middleware(PremiumGateMiddleware())

# ---------- /start ----------
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "🤖 <b>Crypto KOL AI Assistant</b>\n\n"
        "I'm your AI ghostwriter trained on CT culture, trading slang, and viral psychology.\n\n"
        "Commands:\n"
        "/generate - Create content (premium)\n"
        "/train - Teach me your style (premium)\n"
        "/image - Generate AI image prompt (premium)\n"
        "/upgrade - Unlock premium\n"
        "/status - Your premium status\n"
        "/help - All commands"
    )

# ---------- /help ----------
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "<b>Commands</b>\n"
        "/generate &lt;mode&gt; &lt;topic&gt;  e.g. /generate viral Bitcoin pumping\n"
        "/train - Start style training\n"
        "/image &lt;idea&gt;  e.g. /image Bull riding rocket\n"
        "/upgrade - Premium upgrade info\n"
        "/status - Check premium\n"
        "/done_training - Finish style training\n\n"
        "<b>Admin</b>\n"
        "/setprice &lt;amount&gt;\n"
        "/setaddress &lt;wallet&gt;\n"
        "/verify &lt;user_id&gt;"
    )

# ---------- /upgrade ----------
@dp.message(Command("upgrade"))
async def cmd_upgrade(message: types.Message):
    settings = get_settings()
    price = settings.premium_price
    address = settings.payment_address
    await message.answer(
        f"💎 <b>Premium Upgrade</b>\n\n"
        f"Price: <b>{price} USDT</b> (BSC/ERC20/TRC20)\n"
        f"Wallet: <code>{address}</code>\n\n"
        f"1️⃣ Send <b>{price} USDT</b> to the wallet above.\n"
        f"2️⃣ Contact admin with transaction hash.\n"
        f"3️⃣ Admin will verify and activate your premium.\n\n"
        f"Admin: @your_admin (change in code)"
    )

# ---------- /status ----------
@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    user = get_user(message.from_user.id)
    if user and user.is_premium:
        await message.answer("✅ <b>Premium active</b>")
    else:
        await message.answer("❌ Free user. /upgrade")

# ---------- /generate (premium) ----------
@dp.message(Command("generate"))
async def cmd_generate(message: types.Message, command: CommandObject):
    args = command.args
    if not args:
        await message.answer("Usage: /generate &lt;mode&gt; &lt;topic&gt;\nExample: /generate meme Solana memecoins")
        return

    parts = args.split(maxsplit=1)
    valid_modes = ["professional","viral","meme","alpha","emotional","educational","technical","news","luxury","minimal"]
    mode = "professional"
    topic = args

    if parts[0].lower() in valid_modes:
        mode = parts[0].lower()
        topic = parts[1] if len(parts) > 1 else "crypto market"
    else:
        topic = args

    await message.answer("✍️ Generating...")
    content = generate_crypto_content(
        prompt=topic,
        user_id=message.from_user.id,
        mode=mode,
        language="English"
    )
    await message.answer(content)

# ---------- /image (premium) ----------
@dp.message(Command("image"))
async def cmd_image(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("Usage: /image &lt;idea&gt;\nExample: /image Bull breaking through resistance")
        return
    prompt = generate_image_prompt(command.args)
    await message.answer(f"<b>Generated Image Prompt:</b>\n<code>{prompt}</code>")

# ---------- Style Training (premium, FSM) ----------
@dp.message(Command("train"))
async def train_start(message: types.Message, state: FSMContext):
    await state.set_state(Training.collecting)
    await message.answer(
        "📚 <b>Style Training Mode</b>\n\n"
        "Send me your tweets, captions, or threads one by one.\n"
        "I'll learn your writing style.\n"
        "When finished, send /done_training"
    )

@dp.message(Training.collecting, F.text & ~F.text.startswith('/'))
async def collect_style(message: types.Message, state: FSMContext):
    db = get_db()
    sample = StyleSample(user_id=message.from_user.id, text=message.text, category="tweet")
    db.add(sample)
    db.commit()
    db.close()
    await message.answer("✅ Sample stored. Send more or /done_training")

@dp.message(Training.collecting, Command("done_training"))
async def finish_training(message: types.Message, state: FSMContext):
    await state.clear()
    db = get_db()
    count = db.query(StyleSample).filter_by(user_id=message.from_user.id).count()
    db.close()
    await message.answer(f"✅ Training finished. I learned from {count} samples. Your style will now be used in /generate.")

# ---------- ADMIN COMMANDS ----------
@dp.message(Command("setprice"))
@require_admin
async def cmd_setprice(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("Usage: /setprice 49")
        return
    try:
        new_price = float(command.args)
    except ValueError:
        await message.answer("❌ Invalid number.")
        return
    db = get_db()
    settings = db.query(SystemSettings).first()
    settings.premium_price = new_price
    db.commit()
    db.close()
    await message.answer(f"✅ Premium price updated to <b>{new_price} USDT</b>")

@dp.message(Command("setaddress"))
@require_admin
async def cmd_setaddress(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("Usage: /setaddress 0xAbc...")
        return
    new_addr = command.args.strip()
    db = get_db()
    settings = db.query(SystemSettings).first()
    settings.payment_address = new_addr
    db.commit()
    db.close()
    await message.answer(f"✅ Payment address updated to:\n<code>{new_addr}</code>")

@dp.message(Command("verify"))
@require_admin
async def cmd_verify(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer("Usage: /verify &lt;user_id&gt;")
        return
    try:
        uid = int(command.args)
    except ValueError:
        await message.answer("❌ Invalid user ID.")
        return
    db = get_db()
    user = db.query(User).filter_by(telegram_id=uid).first()
    if not user:
        db.close()
        await message.answer("User not found. They must /start first.")
        return
    if user.is_premium:
        db.close()
        await message.answer("User already premium.")
        return
    user.is_premium = True
    db.commit()
    db.close()
    await message.answer(f"✅ User <b>{uid}</b> upgraded to premium.")
    with suppress(Exception):
        await bot.send_message(uid, "🎉 Your premium has been activated! Enjoy all features.")

# ---------- Error handler ----------
@dp.errors()
async def error_handler(update: types.Update, exception: Exception):
    print(f"Update {update} caused error {exception}")

# ---------- Main ----------
async def main():
    # Ensure settings row exists
    db = get_db()
    if not db.query(SystemSettings).first():
        db.add(SystemSettings())
        db.commit()
    db.close()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
