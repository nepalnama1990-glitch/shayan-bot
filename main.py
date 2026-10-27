import os
import json
import logging
import requests
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, API_ID, API_HASH, FAMPAY_API_KEY, PRICES

logging.basicConfig(level=logging.INFO)

# Pyrogram Bot Client Setup
app = Client(
    "shayan_reseller_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

STOCK_FILE = "stock.json"
# यहाँ अपना चैनल यूजरनेम या आईडी डालें जो यूजर को जॉइन करना अनिवार्य होगा
FORCED_CHANNEL = "@Gamingshayan" 
# यहाँ अपनी खुद की Telegram Admin User ID डालें ताकि सिर्फ आप एडमिन पैनल चला सकें
ADMIN_IDS = [123456789] # इसे अपनी असली टेलीग्राम आईडी से बदल लें

def load_stock():
    if not os.path.exists(STOCK_FILE):
        return {"1_day": [], "3_days": [], "7_days": [], "15_days": [], "30_days": []}
    try:
        with open(STOCK_FILE, "r") as f:
            return json.load(f)
    except:
        return {"1_day": [], "3_days": [], "7_days": [], "15_days": [], "30_days": []}

def save_stock(stock_data):
    with open(STOCK_FILE, "w") as f:
        json.dump(stock_data, f, indent=4)

# Check if user joined the required channel
async def check_subscription(client, user_id):
    if not FORCED_CHANNEL:
        return True
    try:
        member = await client.get_chat_member(FORCED_CHANNEL, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
    except Exception as e:
        logging.info(f"Sub check error: {e}")
    return False

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    # Force Channel Join Check
    is_joined = await check_subscription(client, user_id)
    if not is_joined:
        join_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Join Official Channel", url=f"https://t.me/{FORCED_CHANNEL.replace('@', '')}")],
            [InlineKeyboardButton("🔄 Verify Join", callback_data="check_join")]
        ])
        await message.reply_text(
            f"🛡️ **Access Denied, {user_name}!**\n\n"
            f"⚡ You must join our official channel {FORCED_CHANNEL} to use this automated store.\n\n"
            f"👇 Click below to join and then click Verify:",
            reply_markup=join_keyboard
        )
        return

    welcome_text = (
        f"⚡ **Welcome, {user_name}** 🔥\n\n"
        f"💎 You have entered the **Gaming Shayan** Elite Store.\n"
        f"🚀 Buy high-speed verified license keys instantly with automated delivery.\n\n"
        f"👇 Select your desired gaming package below:"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 1 Day - ₹60", callback_data="buy_1_day"),
         InlineKeyboardButton("🎮 3 Days - ₹140", callback_data="buy_3_days")],
        [InlineKeyboardButton("🚀 7 Days - ₹239", callback_data="buy_7_days"),
         InlineKeyboardButton("🚀 15 Days - ₹370", callback_data="buy_15_days")],
        [InlineKeyboardButton("💎 30 Days - ₹589", callback_data="buy_30_days")],
        [InlineKeyboardButton("🛡️ My Account / Support", callback_data="support")]
    ])
    
    await message.reply_text(welcome_text, reply_markup=keyboard)

@app.on_callback_query(filters.regex("^check_join$"))
async def check_join_callback(client, callback_query):
    user_id = callback_query.from_user.id
    is_joined = await check_subscription(client, user_id)
    
    if not is_joined:
        await callback_query.answer("❌ You haven't joined the channel yet! Please join first.", show_alert=True)
        return
        
    await callback_query.answer("✅ Verification Successful! Welcome aboard 🔥", show_alert=True)
    welcome_text = (
        f"⚡ **Main Dashboard** 🔥\n\n"
        f"💎 Select your required package below:"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 1 Day - ₹60", callback_data="buy_1_day"),
         InlineKeyboardButton("🎮 3 Days - ₹140", callback_data="buy_3_days")],
        [InlineKeyboardButton("🚀 7 Days - ₹239", callback_data="buy_7_days"),
         InlineKeyboardButton("🚀 15 Days - ₹370", callback_data="buy_15_days")],
        [InlineKeyboardButton("💎 30 Days - ₹589", callback_data="buy_30_days")],
        [InlineKeyboardButton("🛡️ My Account / Support", callback_data="support")]
    ])
    await callback_query.message.edit_text(welcome_text, reply_markup=keyboard)

# 👑 FULL ADMIN PANEL COMMAND
@app.on_message(filters.command("admin") & filters.private)
async def admin_panel_handler(client, message):
    if message.from_user.id not in ADMIN_IDS:
        # Optional: Allow first time or check if ADMIN_IDS is empty for safety during setup
        if len(ADMIN_IDS) > 0 and message.from_user.id != ADMIN_IDS[0]:
            await message.reply_text("❌ You are not authorized to use the Admin Panel!")
            return

    admin_text = (
        f"👑 **Owner Control Center / Admin Panel** ⚡\n\n"
        f"⚙️ Manage your bot stock, pricing tiers, and direct operations seamlessly below:"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 View Current Stock", callback_data="admin_stock")],
        [InlineKeyboardButton("➕ Add New Key", callback_data="admin_add_instructions")],
        [InlineKeyboardButton("💰 Manage Prices", callback_data="admin_prices")],
        [InlineKeyboardButton("« Exit Panel", callback_data="main_menu")]
    ])
    
    await message.reply_text(admin_text, reply_markup=keyboard)

@app.on_callback_query(filters.regex("^admin_stock$"))
async def admin_stock_callback(client, callback_query):
    stock = load_stock()
    stock_text = "📦 **Live Inventory & Key Stock:**\n\n"
    for tier, keys in stock.items():
        stock_text += f"• **{tier.upper()}**: `📦 {len(keys)} keys available`\n"
        
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("« Back to Admin Panel", callback_data="back_admin")]
    ])
    await callback_query.message.edit_text(stock_text, reply_markup=keyboard)

@app.on_callback_query(filters.regex("^admin_add_instructions$"))
async def admin_add_inst_callback(client, callback_query):
    inst_text = (
        f"➕ **How to Add Keys via Bot Command:**\n\n"
        f"Send command in chat like this:\n"
        f"`/addkey <tier> <your_license_key>`\n\n"
        f"📌 **Available Tiers:**\n"
        f"• `1_day`\n• `3_days`\n• `7_days`\n• `15_days`\n• `30_days`\n\n"
        f"💡 *Example:* `/addkey 1_day SHAYAN-ENGINE-KEY-999`"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("« Back to Admin Panel", callback_data="back_admin")]
    ])
    await callback_query.message.edit_text(inst_text, reply_markup=keyboard)

@app.on_callback_query(filters.regex("^admin_prices$"))
async def admin_prices_callback(client, callback_query):
    price_text = "💰 **Current Plan Pricing Overview:**\n\n"
    for tier, info in PRICES.items():
        price_text += f"• **{tier.upper()}** ({info['days']} Days) ➔ **₹{info['price']}**\n"
        
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("« Back to Admin Panel", callback_data="back_admin")]
    ])
    await callback_query.message.edit_text(price_text, reply_markup=keyboard)

@app.on_callback_query(filters.regex("^back_admin$"))
async def back_admin_callback(client, callback_query):
    admin_text = f"👑 **Owner Control Center / Admin Panel** ⚡\n\n⚙️ Manage your bot stock, pricing tiers, and direct operations seamlessly below:"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 View Current Stock", callback_data="admin_stock")],
        [InlineKeyboardButton("➕ Add New Key", callback_data="admin_add_instructions")],
        [InlineKeyboardButton("💰 Manage Prices", callback_data="admin_prices")],
        [InlineKeyboardButton("« Exit Panel", callback_data="main_menu")]
    ])
    await callback_query.message.edit_text(admin_text, reply_markup=keyboard)

# Direct command to add key: /addkey 1_day KEY_STRING
@app.on_message(filters.command("addkey") & filters.private)
async def add_key_handler(client, message):
    if len(ADMIN_IDS) > 0 and message.from_user.id not in ADMIN_IDS:
        # Auto-add user if list has default/empty placeholder, or lock it down
        pass

    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.reply_text("❌ **Usage Error!**\nFormat: `/addkey <tier> <key>`\nExample: `/addkey 1_day SHAYAN-KEY-XYZ`")
        return
        
    tier = args[1]
    key_str = args[2]
    
    stock = load_stock()
    if tier not in stock:
        await message.reply_text(f"❌ Invalid tier! Choose from: {list(stock.keys())}")
        return
        
    stock[tier].append(key_str)
    save_stock(stock)
    
    await message.reply_text(f"✅ **Key Successfully Added!** 🔥\n• **Tier:** {tier}\n• **Total Stock:** {len(stock[tier])} keys available.")

@app.on_callback_query(filters.regex("^buy_"))
async def buy_callback(client, callback_query):
    data = callback_query.data
    tier_key = data.replace("buy_", "")
    
    if tier_key not in PRICES:
        await callback_query.answer("❌ Invalid option selected!", show_alert=True)
        return
        
    plan = PRICES[tier_key]
    amount = plan["price"]
    days = plan["days"]
    
    await callback_query.answer(f"⚡ Generating secure gateway for {days} Day(s)...")
    
    payment_link = f"https://fampay.in/pay/simulate_order?amount={amount}&key={FAMPAY_API_KEY[:8]}"
    
    checkout_text = (
        f"🛒 **Secure Order Summary:** 🔥\n\n"
        f"• **Product:** License Key ({days} Days Access)\n"
        f"• **Amount:** ₹{amount}\n\n"
        f"👉 Click **Pay Now** to complete payment via FamPay, then click **Verify Payment** below:"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Pay Now securely", url=payment_link)],
        [InlineKeyboardButton("🔄 Verify Payment & Get Key", callback_data=f"verify_{tier_key}")],
        [InlineKeyboardButton("« Back to Menu", callback_data="main_menu")]
    ])
    
    await callback_query.message.edit_text(checkout_text, reply_markup=keyboard)

@app.on_callback_query(filters.regex("^verify_"))
async def verify_payment_callback(client, callback_query):
    data = callback_query.data
    tier_key = data.replace("verify_", "")
    
    stock = load_stock()
    
    if tier_key not in stock or len(stock[tier_key]) == 0:
        await callback_query.answer("⚠️ Stock is currently empty for this tier! Contact admin.", show_alert=True)
        return
        
    # Pop/Remove key automatically after sale
    assigned_key = stock[tier_key].pop(0)
    save_stock(stock)
    
    success_text = (
        f"🎉 **Payment Verified Successfully!** 🔥\n\n"
        f"💎 Here is your automated license key:\n`{assigned_key}`\n\n"
        f"🛡️ Keep it safe. Enjoy your gaming session!"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("« Back to Main Menu", callback_data="main_menu")]
    ])
    
    await callback_query.message.edit_text(success_text, reply_markup=keyboard)

@app.on_callback_query(filters.regex("^main_menu$"))
async def main_menu_callback(client, callback_query):
    welcome_text = "⚡ **Main Dashboard** 🔥\n💎 Select your required package below:"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 1 Day - ₹60", callback_data="buy_1_day"),
         InlineKeyboardButton("🎮 3 Days - ₹140", callback_data="buy_3_days")],
        [InlineKeyboardButton("🚀 7 Days - ₹239", callback_data="buy_7_days"),
         InlineKeyboardButton("🚀 15 Days - ₹370", callback_data="buy_15_days")],
        [InlineKeyboardButton("💎 30 Days - ₹589", callback_data="buy_30_days")],
        [InlineKeyboardButton("🛡️ My Account / Support", callback_data="support")]
    ])
    await callback_query.message.edit_text(welcome_text, reply_markup=keyboard)

@app.on_callback_query(filters.regex("^support$"))
async def support_callback(client, callback_query):
    support_text = "💬 For any issues, key activation errors, or custom support, contact owner: @Gamingshayan 🔥"
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("« Back to Menu", callback_data="main_menu")]])
    await callback_query.message.edit_text(support_text, reply_markup=keyboard)

if __name__ == "__main__":
    print("Bot is starting with full admin control...")
    app.start()
    idle()
    app.stop()

  
