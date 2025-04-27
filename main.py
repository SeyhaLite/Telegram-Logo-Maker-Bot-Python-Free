import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import random
import os
import logging
import json
from datetime import datetime
import uuid
import asyncio
import textwrap

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bot token and admin ID
TOKEN = "BOT_TOKEN_HERE"
# Your ID Telegram here
ADMIN_ID = 5271587219

# Bot username
BOT_USERNAME = "@SYLOGODesignBot"

# JSON file paths
IMAGE_URLS_FILE = "image_urls.json"
TEXT_STYLES_FILE = "text_styles.json"
DATA_FILE = "bot_data.json"
LANGUAGE_FILE = "languages.json"
BASE_FONT_DIR = "user_fonts"  # Base directory for user-specific font folders
FONT_CACHE = {}  # Cache for loaded font objects

# Supported languages and their font directories
LANGUAGES = ["en", "kh", "th", "vi", "pt", "zh", "ja", "hi", "ar", "ko", "es"]
DEFAULT_FONTS = {
    "en": "font/en/Roboto-Regular.ttf",
    "kh": "font/kh/NotoSansKhmer-Regular.ttf",
    "th": "font/th/THSarabunPSK-Regular.ttf",
    "vi": "font/vi/Quicksand-Regular.ttf",
    "pt": "font/pt/Lato-Regular.ttf",
    "zh": "font/zh/NotoSansSC-Regular.ttf",
    "ja": "font/ja/NotoSansJP-Regular.ttf",
    "hi": "font/hi/NotoSansDevanagari-Regular.ttf",
    "ar": "font/ar/NotoNaskhArabic-Regular.ttf",
    "ko": "font/ko/NotoSansKR-Regular.ttf",
    "es": "font/es/OpenSans-Regular.ttf"
}

# Default JSON content for missing files
DEFAULT_IMAGE_URLS = [
    "https://images.unsplash.com/photo-1507525428034-b723cf961d3e",
    "https://images.unsplash.com/photo-1519125323398-675f0ddb6308",
    "https://images.unsplash.com/photo-1497436072909-60f360e1d4b1"
]
DEFAULT_TEXT_STYLES = [
    {"name": "Plain Black", "color": [0, 0, 0], "shadow_color": None, "outline": 0, "effect": "none", "category": "Simple Style"}
]
DEFAULT_LANGUAGES = {lang: {} for lang in LANGUAGES}

# Load JSON files with default creation
def load_json_file(file_path, default):
    if not os.path.exists(file_path):
        logger.warning(f"{file_path} not found. Creating with default content.")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(default, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Failed to create {file_path}: {str(e)}")
            return default
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load {file_path}: {str(e)}. Using default.")
        return default

# Load image URLs
IMAGE_URLS = load_json_file(IMAGE_URLS_FILE, DEFAULT_IMAGE_URLS)

# Load text styles and convert color lists to tuples
def load_text_styles():
    styles = load_json_file(TEXT_STYLES_FILE, DEFAULT_TEXT_STYLES)
    for style in styles:
        try:
            style["color"] = tuple(style["color"]) if style["color"] is not None else None
            style["shadow_color"] = tuple(style["shadow_color"]) if style["shadow_color"] is not None else None
        except Exception as e:
            logger.error(f"Invalid color format in style {style.get('name', 'unknown')}: {str(e)}")
            style["color"] = (0, 0, 0)
            style["shadow_color"] = None
    return styles

TEXT_STYLES = load_text_styles()

# Load languages
LANGUAGES_DATA = load_json_file(LANGUAGE_FILE, DEFAULT_LANGUAGES)

# Ensure base font directory exists
if not os.path.exists(BASE_FONT_DIR):
    try:
        os.makedirs(BASE_FONT_DIR)
    except Exception as e:
        logger.error(f"Failed to create {BASE_FONT_DIR}: {str(e)}")

# Load or initialize data
def load_data():
    data = load_json_file(DATA_FILE, {"users": {}})
    if "users" not in data:
        data["users"] = {}
    return data

# Save data
def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Failed to save {DATA_FILE}: {str(e)}")

data = load_data()

# Bot State Manager Class
class BotStateManager:
    def __init__(self):
        self.current_language = "kh"  # Default to Khmer

    def set_language(self, language):
        if language in LANGUAGES:
            self.current_language = language
            return True
        return False

    def get_font_path(self, user_id):
        user_id_str = str(user_id)
        # Check for user-uploaded font
        if user_id_str in data["users"] and "font_path" in data["users"][user_id_str]:
            font_path = data["users"][user_id_str]["font_path"]
            if os.path.exists(font_path):
                return font_path
        # Use default font for current language
        default_font = DEFAULT_FONTS.get(self.current_language, DEFAULT_FONTS["en"])
        if os.path.exists(default_font):
            return default_font
        logger.warning(f"Default font {default_font} not found. Using PIL default.")
        return None

    async def set_font(self, user_id, font_file, file_name):
        user_id_str = str(user_id)
        user_font_dir = os.path.join(BASE_FONT_DIR, f"user_{user_id_str}", "font")
        try:
            if not os.path.exists(user_font_dir):
                os.makedirs(user_font_dir)
            # Remove old font if it exists and is not default
            if user_id_str in data["users"] and "font_path" in data["users"][user_id_str]:
                old_font_path = data["users"][user_id_str]["font_path"]
                if os.path.exists(old_font_path) and old_font_path not in DEFAULT_FONTS.values():
                    try:
                        os.remove(old_font_path)
                    except Exception as e:
                        logger.error(f"Failed to remove old font {old_font_path}: {str(e)}")
            # Set new font path
            new_font_path = os.path.join(user_font_dir, f"custom_{uuid.uuid4().hex}.ttf")
            await font_file.download_to_drive(new_font_path)
            if user_id_str not in data["users"]:
                data["users"][user_id_str] = {}
            data["users"][user_id_str]["font_path"] = new_font_path
            save_data(data)
            return new_font_path
        except Exception as e:
            logger.error(f"Failed to set font for user {user_id}: {str(e)}")
            raise

    def get_style_index(self, user_id):
        user_id_str = str(user_id)
        return data["users"].get(user_id_str, {}).get("style_index", -1)  # -1 indicates random style

    def set_style_index(self, user_id, index):
        user_id_str = str(user_id)
        if 0 <= index < len(TEXT_STYLES):
            if user_id_str not in data["users"]:
                data["users"][user_id_str] = {}
            data["users"][user_id_str]["style_index"] = index
            save_data(data)
            return True
        return False

    def reset_to_random_style(self, user_id):
        user_id_str = str(user_id)
        if user_id_str in data["users"]:
            if "style_index" in data["users"][user_id_str]:
                del data["users"][user_id_str]["style_index"]
            save_data(data)
            return True
        return False

    def get_message(self, key, **kwargs):
        messages = LANGUAGES_DATA.get(self.current_language, LANGUAGES_DATA.get("en", {}))
        message = messages.get(key, LANGUAGES_DATA["en"].get(key, key))
        return message.format(**kwargs)

# Initialize bot state
bot_state = BotStateManager()

async def start(update, context):
    """Handle the /start command with an inline keyboard."""
    user = update.message.from_user
    user_id = str(user.id)
    username = user.username if user.username else "No Username"
    name = user.full_name
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if user_id not in data["users"]:
        data["users"][user_id] = {"username": username, "name": name, "date": date, "language": bot_state.current_language}
        save_data(data)
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"New User Notification 📩\n"
                     f"Username: @{username}\n"
                     f"Name: {name}\n"
                     f"ID: {user_id}\n"
                     f"Date: {date}"
            )
            logger.info(f"New user registered: {username} (ID: {user_id})")
        except telegram.error.BadRequest as e:
            logger.error(f"Failed to notify admin (ID: {ADMIN_ID}): {str(e)}")

    if user_id in data["users"]:
        bot_state.current_language = data["users"][user_id].get("language", "kh")

    # Create inline keyboard
    keyboard = [
        [
            InlineKeyboardButton("🎨 Styles", callback_data="styles"),
            InlineKeyboardButton("📜 Set Font", callback_data="setfont"),
        ],
        [
            InlineKeyboardButton("🌐 Language", callback_data="language"),
            InlineKeyboardButton("📚 Tutorial", callback_data="tutorial"),
        ],
        [InlineKeyboardButton("🎲 Random Style", callback_data="randomstyle")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        bot_state.get_message("welcome"),
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_callback(update, context):
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()
    command_map = {
        "styles": list_styles,
        "setfont": set_font,
        "language": set_language,
        "tutorial": tutorial,
        "randomstyle": random_style,
    }
    if query.data in command_map:
        await command_map[query.data](query, context)

async def set_font(update, context):
    """Handle font upload and persist it based on user ID."""
    user_id = str(update.message.from_user.id)
    file = update.message.document
    if file and (file.mime_type == "application/x-font-ttf" or file.file_name.endswith(".ttf")):
        try:
            font_file = await context.bot.get_file(file.file_id)
            await bot_state.set_font(user_id, font_file, file.file_name)
            await update.message.reply_text(bot_state.get_message("font_success"))
        except Exception as e:
            logger.error(f"Font upload failed for user {user_id}: {str(e)}")
            await update.message.reply_text(bot_state.get_message("font_error"))
    else:
        await update.message.reply_text(bot_state.get_message("font_invalid"))

async def list_styles(update, context):
    """List all available styles."""
    if not TEXT_STYLES:
        await update.message.reply_text(bot_state.get_message("no_styles"))
        return
    style_list = bot_state.get_message("available_styles") + "\n"
    for i, style in enumerate(TEXT_STYLES, 1):
        style_list += f"{i}. {style['name']} ({style['category']})\n"
    await update.message.reply_text(style_list)

async def list_fonts(update, context):
    """List available default fonts for each language."""
    font_list = bot_state.get_message("available_fonts") + "\n"
    for lang in LANGUAGES:
        font_path = DEFAULT_FONTS.get(lang, DEFAULT_FONTS["en"])
        font_name = os.path.basename(font_path).replace(".ttf", "")
        lang_name = {
            "en": "English",
            "kh": "Khmer",
            "th": "Thai",
            "vi": "Vietnamese",
            "pt": "Portuguese",
            "zh": "Chinese",
            "ja": "Japanese",
            "hi": "Hindi",
            "ar": "Arabic",
            "ko": "Korean",
            "es": "Spanish"
        }.get(lang, lang)
        font_list += f"{lang_name}: {font_name}\n"
    await update.message.reply_text(font_list)

async def set_style(update, context):
    """Set the current style based on user input."""
    user_id = str(update.message.from_user.id)
    if not context.args:
        await update.message.reply_text(bot_state.get_message("style_input_invalid"))
        return
    style_input = " ".join(context.args).lower()
    try:
        if style_input.isdigit():
            index = int(style_input) - 1
            if bot_state.set_style_index(user_id, index):
                await update.message.reply_text(bot_state.get_message("style_set", style_name=TEXT_STYLES[index]['name']))
            else:
                await update.message.reply_text(bot_state.get_message("style_invalid"))
        else:
            for i, style in enumerate(TEXT_STYLES):
                if style["name"].lower() == style_input:
                    if bot_state.set_style_index(user_id, i):
                        await update.message.reply_text(bot_state.get_message("style_set", style_name=style['name']))
                    return
            await update.message.reply_text(bot_state.get_message("style_not_found"))
    except ValueError:
        await update.message.reply_text(bot_state.get_message("style_input_invalid"))

async def random_style(update, context):
    """Reset the user's style to random selection."""
    user_id = str(update.message.from_user.id)
    if bot_state.reset_to_random_style(user_id):
        await update.message.reply_text(bot_state.get_message("style_reset"))
    else:
        await update.message.reply_text(bot_state.get_message("style_reset_failed"))

async def set_language(update, context):
    """Set the current language and register user if new."""
    user_id = str(update.message.from_user.id)
    username = update.message.from_user.username if update.message.from_user.username else "No Username"
    name = update.message.from_user.full_name
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if user_id not in data["users"]:
        data["users"][user_id] = {"username": username, "name": name, "date": date, "language": bot_state.current_language}
        save_data(data)
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"New User Notification 📩\n"
                     f"Username: @{username}\n"
                     f"Name: {name}\n"
                     f"ID: {user_id}\n"
                     f"Date: {date}"
            )
            logger.info(f"New user registered via /language: {username} (ID: {user_id})")
        except telegram.error.BadRequest as e:
            logger.error(f"Failed to notify admin (ID: {ADMIN_ID}): {str(e)}")

    if not context.args or context.args[0].lower() not in LANGUAGES:
        await update.message.reply_text(bot_state.get_message("language_invalid"))
        return
    if bot_state.set_language(context.args[0].lower()):
        data["users"][user_id]["language"] = bot_state.current_language
        save_data(data)
        language_name = {
            "en": "English",
            "kh": "Khmer",
            "th": "Thai",
            "vi": "Vietnamese",
            "pt": "Portuguese",
            "zh": "Chinese",
            "ja": "Japanese",
            "hi": "Hindi",
            "ar": "Arabic",
            "ko": "Korean",
            "es": "Spanish"
        }.get(bot_state.current_language, bot_state.current_language)
        await update.message.reply_text(bot_state.get_message("language_set", language=language_name))

async def tutorial(update, context):
    """Display tutorial in selected language."""
    await update.message.reply_text(bot_state.get_message("tutorial"), parse_mode="Markdown")

def fetch_image(url):
    """Fetch an HD image from a URL with original dimensions."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "").lower()
        if "image" not in content_type:
            raise ValueError(f"URL does not point to an image (Content-Type: {content_type}).")
        return Image.open(BytesIO(response.content)).convert("RGBA")
    except Exception as e:
        logger.error(f"Failed to fetch image from {url}: {str(e)}")
        raise

def apply_text_to_image(img, text, font_path, user_id):
    """Apply styled text to an image with dynamic sizing."""
    draw = ImageDraw.Draw(img)
    img_width, img_height = img.size

    # Determine text direction (RTL for Arabic)
    is_rtl = bot_state.current_language == "ar"
    try:
        # Cache font loading
        font_key = f"{font_path}_{img_width}_{img_height}"
        if font_key not in FONT_CACHE:
            max_font_size = min(img_width // 6, img_height // 6, 150)
            font_size = max_font_size
            font = ImageFont.truetype(font_path, font_size) if font_path and os.path.exists(font_path) else ImageFont.load_default()
            credit_font_size = max(20, font_size // 4)
            credit_font = ImageFont.truetype(font_path, credit_font_size) if font_path and os.path.exists(font_path) else ImageFont.load_default()
            FONT_CACHE[font_key] = (font, credit_font, font_size, credit_font_size)
        else:
            font, credit_font, font_size, credit_font_size = FONT_CACHE[font_key]
    except Exception as e:
        logger.warning(f"Font loading failed: {str(e)}. Using default font.")
        font = ImageFont.load_default()
        credit_font = ImageFont.load_default()
        font_size = 50
        credit_font_size = 20

    # Wrap text to fit image width
    max_text_width = img_width * 0.8
    wrapped_text = []
    for line in text.split("\n"):
        if draw.textbbox((0, 0), line, font=font)[2] > max_text_width:
            wrapped_lines = textwrap.wrap(line, width=int(max_text_width / (font_size / 2)))
            wrapped_text.extend(wrapped_lines)
        else:
            wrapped_text.append(line)

    # Calculate total text height
    line_heights = [draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in wrapped_text]
    total_text_height = sum(line_heights) + (len(wrapped_text) - 1) * (font_size // 4)

    # Center text vertically
    y_position = (img_height - total_text_height) // 2
    style_index = bot_state.get_style_index(user_id)
    style = TEXT_STYLES[style_index] if style_index >= 0 else random.choice(TEXT_STYLES)
    shadow_offset = min(font_size // 8, 15)

    # Apply text effects
    for i, line in enumerate(wrapped_text):
        text_bbox = draw.textbbox((0, 0), line, font=font)
        line_width = text_bbox[2] - text_bbox[0]
        x_position = (img_width - line_width) // 2 if not is_rtl else img_width - (line_width + (img_width - line_width) // 2)
        position = (x_position, y_position)

        if style["effect"] == "3d":
            draw.text((position[0] + shadow_offset, position[1] + shadow_offset), line, font=font, fill=style["shadow_color"])
            for offset in range(-style["outline"], style["outline"] + 1):
                for y in range(-style["outline"], style["outline"] + 1):
                    if offset != 0 or y != 0:
                        draw.text((position[0] + offset, position[1] + y), line, font=font, fill=(0, 0, 0, 100))
        elif style["effect"] == "fire":
            for j in range(5):
                offset = shadow_offset * (j + 1) / 5
                draw.text((position[0] + offset, position[1] + offset), line, font=font, fill=(255, 69 + j * 30, 0))
        elif style["effect"] == "lightning":
            for j in range(5):
                offset_x = random.randint(-shadow_offset, shadow_offset)
                offset_y = random.randint(-shadow_offset, shadow_offset)
                draw.text((position[0] + offset_x, position[1] + offset_y), line, font=font, fill=(255, 255, 255, int(255 * (1 - j / 5))))
        elif style["effect"] == "neon":
            for j in range(4):
                offset = style["outline"] * (j + 1) / 4
                for angle in range(0, 360, 45):
                    x_offset = int(offset * 0.5 * (1 + 0.5 * j) * 0.707)
                    y_offset = int(offset * 0.5 * (1 + 0.5 * j) * 0.707)
                    draw.text((position[0] + x_offset, position[1] + y_offset), line, font=font, fill=(style["color"][0], style["color"][1], style["color"][2], int(255 * (1 - j / 4))))
        elif style["effect"] == "gradient":
            for j in range(5):
                offset = shadow_offset * (j + 1) / 5
                r = min(255, style["color"][0] + j * 20)
                g = min(255, style["color"][1] + j * 20)
                b = min(255, style["color"][2] + j * 20)
                draw.text((position[0] + offset, position[1] + offset), line, font=font, fill=(r, g, b))
        elif style["effect"] == "glow":
            for j in range(3):
                offset = shadow_offset * j / 3
                draw.text((position[0] + offset, position[1] + offset), line, font=font, fill=(style["shadow_color"][0], style["shadow_color"][1], style["shadow_color"][2], int(255 * (1 - j / 3))))
        elif style["effect"] == "spark":
            for j in range(5):
                offset_x = random.randint(-shadow_offset, shadow_offset)
                offset_y = random.randint(-shadow_offset, shadow_offset)
                draw.text((position[0] + offset_x, position[1] + offset_y), line, font=font, fill=(255, 215, 0, int(255 * (1 - j / 5))))
        elif style["effect"] == "soft":
            for j in range(3):
                offset = shadow_offset * j / 3
                draw.text((position[0] + offset, position[1] + offset), line, font=font, fill=(style["shadow_color"][0], style["shadow_color"][1], style["shadow_color"][2], int(255 * (1 - j / 3))))
        elif style["effect"] == "metallic":
            for j in range(3):
                offset = shadow_offset * j / 3
                gray = min(255, style["color"][0] + j * 20)
                draw.text((position[0] + offset, position[1] + offset), line, font=font, fill=(gray, gray, gray, 255))

        draw.text(position, line, font=font, fill=style["color"])
        y_position += line_heights[i] + (font_size // 4)

    # Add credit text at the bottom
    credit_text = BOT_USERNAME
    credit_bbox = draw.textbbox((0, 0), credit_text, font=credit_font)
    credit_width = credit_bbox[2] - credit_bbox[0]
    credit_position = ((img_width - credit_width) // 2, img_height - credit_font_size - 10)
    draw.text(credit_position, credit_text, font=credit_font, fill=(255, 255, 255))

    return img

async def add_text(update, context):
    """Handle text input and apply it to a random HD image with selected style and caption."""
    user_id = str(update.message.from_user.id)
    user_text = update.message.text.strip()

    if not user_text:
        await update.message.reply_text(bot_state.get_message("empty_text"))
        return

    font_path = bot_state.get_font_path(user_id)
    if not font_path:
        await update.message.reply_text(bot_state.get_message("no_font"))
        return

    if not IMAGE_URLS:
        await update.message.reply_text(bot_state.get_message("no_images"))
        return

    attempts = 0
    max_attempts = 3
    while attempts < max_attempts:
        base_url = random.choice(IMAGE_URLS)
        try:
            img = fetch_image(base_url)
            img_with_text = apply_text_to_image(img, user_text, font_path, user_id)
            output = BytesIO()
            img_with_text.save(output, format="PNG", quality=95)
            output.seek(0)
            caption = bot_state.get_message("caption", bot_username=BOT_USERNAME)
            await context.bot.send_photo(chat_id=update.message.chat_id, photo=output, caption=caption)
            logger.info(f"HD image with selected style sent to user {user_id} from {base_url}.")
            break
        except Exception as e:
            attempts += 1
            logger.error(f"Attempt {attempts} failed for URL {base_url}: {str(e)}")
            if attempts == max_attempts:
                await update.message.reply_text(bot_state.get_message("image_failed"))

async def broadcast(update, context):
    """Allow admin to broadcast a message to all users."""
    if str(update.message.from_user.id) != str(ADMIN_ID):
        await update.message.reply_text(bot_state.get_message("broadcast_unauthorized"))
        return
    if not context.args:
        await update.message.reply_text(bot_state.get_message("broadcast_no_message"))
        return
    message = " ".join(context.args)
    sent_count = 0
    for user_id in data["users"]:
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
            sent_count += 1
        except Exception as e:
            logger.error(f"Failed to send broadcast to {user_id}: {str(e)}")
    await update.message.reply_text(bot_state.get_message("broadcast_success") + f" (Sent to {sent_count} users)")

# Main function to run the bot
async def main():
    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setfont", set_font))
    application.add_handler(CommandHandler("styles", list_styles))
    application.add_handler(CommandHandler("fonts", list_fonts))
    application.add_handler(CommandHandler("style", set_style))
    application.add_handler(CommandHandler("randomstyle", random_style))
    application.add_handler(CommandHandler("language", set_language))
    application.add_handler(CommandHandler("tutorial", tutorial))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(MessageHandler(filters.Document.ALL, set_font))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_text))
    application.add_handler(telegram.ext.CallbackQueryHandler(button_callback))

    # Start the bot with proper shutdown handling
    try:
        await application.initialize()
        await application.start()
        await application.updater.start_polling(allowed_updates=telegram.Update.ALL_TYPES)
        logger.info("Bot started successfully.")
        while True:
            await asyncio.sleep(3600)
    except Exception as e:
        logger.error(f"Bot failed to start: {str(e)}")
        raise
    finally:
        try:
            await application.updater.stop()
            await application.stop()
            await application.shutdown()
            logger.info("Bot shutdown successfully.")
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    if loop.is_running():
        logger.warning("Event loop is already running. Running in existing loop.")
        loop.create_task(main())
    else:
        try:
            loop.run_until_complete(main())
        except KeyboardInterrupt:
            logger.info("Bot stopped by user.")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
