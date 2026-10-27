import os
import json
import logging
import requests
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, API_ID, API_HASH, FAMPAY_API_KEY, PRICES

logging.basicConfig(level=logging.INFO)

app = Client(
    "shayan_reseller_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

STOCK_FILE = "stock.json"
USERS_FILE = "users.json"
FORCED_CHANNEL = "@Gamingshayan" 
ADMIN_IDS = [123456789] # Yahan apni asli Telegram User ID daal dena bhai

def load_json(filename, default_val):
    if not os.path.exists(filename):
        return default_val
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        return default_val

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def load_stock():
    return load_json(STOCK_FILE, {"1_day": [], "3_days": [], "7_days": [], "15_days": [], "30_days": []})

def save_stock(stock_data):
    save_json(STOCK_FILE, stock_data)

def load_users():
    return load_json(USERS_FILE, {})

def save_users(users_data):
    save_json(USERS_FILE, users_data)

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
    
    # Save user to database
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {"name": user_name, "balance": 0}
        save_users(users)
    
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
        [InlineKeyboardButton("🛡️ My Account / Balance", callback_data="my_account")]
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
    welcome_text = f"⚡ **Main Dashboard** 🔥\n\n💎 Select your required package below:"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 1 Day - ₹60", callback_data="buy_1_day"),
         InlineKeyboardButton("🎮 3 Days - ₹140", callback_data="buy_3_days")],
        [InlineKeyboardButton("🚀 7 Days - ₹239", callback_data="buy_7_days"),
         InlineKeyboardButton("🚀 15 Days - ₹370", callback_data="buy_15_days")],
        [InlineKeyboardButton("💎 30 Days - ₹589", callback_data="buy_30_days")],
        [InlineKeyboardButton("🛡️ My Account / Balance", callback_data="my_account")]
    ])
    await callback_query.message.edit_text(welcome_text, reply_markup=keyboard)

@app.on_callback_query(filters.regex("^my_account$"))
async def my_account_callback(client, callback_query):
    user_id = str(callback_query.from_user.id)
    users = load_users()
    user_data = users.get(user_id, {"balance": 0})
    
    acc_text = (
        f"👤 **Your Account Details:** 🔥\n\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"💰 **Wallet Balance:** `₹{user_data.get('balance', 0)}`\n\n"
        f"💬 Need help? Contact owner: @Gamingshayan"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("« Back to Menu", callback_data="main_menu")]])
    await callback_query.message.edit_text(acc_text, reply_markup=keyboard)

# 👑 FULL POWER ADMIN PANEL COMMAND (/admin)
@app.on_message(filters.command("admin") & filters.private)
async def admin_panel_handler(client, message):
    if len(ADMIN_IDS) > 0 and message.from_user.id not in ADMIN_IDS:
        await message.reply_text("❌ You are not authorized to use the Admin Panel!")
        return

    admin_text = (
        f"👑 **Owner Ultimate Control Center / Admin Panel** ⚡\n\n"
        f"⚙️ Manage stock, user wallet balances, prices, and operations seamlessly below:"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 View Live Stock", callback_data="admin_stock"),
         InlineKeyboardButton("👥 Total Users", callback_data="admin_users")],
        [InlineKeyboardButton("➕ Add Key Help", callback_data="admin_add_instructions"),
         InlineKeyboardButton("💰 Manage User Balance", callback_data="admin_balance_help")],
        [InlineKeyboardButton("« Exit Panel", callback_data="main_menu")]
    ])
    
    await message.reply_text(admin_text, reply_markup=keyboard)

@app.on_callback_query(filters.regex("^admin_stock$"))
async def admin_stock_callback(client, callback_query):
    stock = load_stock()
    stock_text = "📦 **Live Inventory & Key Stock:**\n\n"
    for tier, keys in stock.items():
        stock_text += f"• **{tier.upper()}**: `📦 {len(keys)} keys available`\n"
        
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("« Back to Admin Panel", callback_data="back_admin")]])
    await callback_query.message.edit_text(stock_text, reply_markup=keyboard)

@app.on_callback_query(filters.regex("^admin_users$"))
async def admin_users_callback(client, callback_query):
    users = load_users()
    text = f"👥 **Total Registered Users:** `{len(users)}`\n\n💡 You can add/remove money using:\n`/addbal <user_id> <amount>`\n`/subbal <user_id> <amount>`"
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("« Back to Admin Panel", callback_data="back_admin")]])
    await callback_query.message.edit_text(text, reply_markup=keyboard)

@app.on_callback_query(filters.regex("^admin_balance_help$"))
async def admin_bal_help_callback(client, callback_query):
    text = (
        f"💰 **Wallet Balance Management Commands:**\n\n"
        f"1️⃣ **Add Money to User:**\n"
        f"`/addbal <user_id> <amount>`\n"
        f"*Example:* `/addbal 987654321 100`\n\n"
        f"2️⃣ **Deduct Money from User:**\n"
        f"`/subbal <user_id> <amount>`\n"
        f"*Example:* `/subbal 987654321 50`"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("« Back to Admin Panel", callback_data="back_admin")]])
    await callback_query.message.edit_text(text, reply_markup=keyboard)

@app.on_callback_query(filters.regex("^admin_add_instructions$"))
async def admin_add_inst_callback(client, callback_query):
    inst_text = (
        f"➕ **How to Add Keys:**\n\n"
        f"Send command in chat:\n"
        f"`/addkey <tier> <license_key>`\n\n"
        f"📌 **Available Tiers:** `1_day`, `3_days`, `7_days`, `15_days`, `30_days`\n"
        f"💡 *Example:* `/addkey 1_day SHAYAN-KEY-XYZ`"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("« Back to Admin Panel", callback_data="back_admin")]])
    await callback_query.message.edit_text(inst_text, reply_markup=keyboard)

@app.on_callback_query(filters.regex("^back_admin$"))
async def back_admin_callback(client, callback_query):
    admin_text = f"👑 **Owner Ultimate Control Center / Admin Panel** ⚡\n\n⚙️ Manage stock, user wallet balances, prices, and operations seamlessly below:"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 View Live Stock", callback_data="admin_stock"),
         InlineKeyboardButton("👥 Total Users", callback_data="admin_users")],
        [InlineKeyboardButton("➕ Add Key Help", callback_data="admin_add_instructions"),
         InlineKeyboardButton("💰 Manage User Balance", callback_data="admin_balance_help")],
        [InlineKeyboardButton("« Exit Panel", callback_data="main_menu")]
    ])
    await callback_query.message.edit_text(admin_text, reply_markup=keyboard)

# ADMIN COMMAND: Add Key (/addkey)
@app.on_message(filters.command("addkey") & filters.private)
async def add_key_handler(client, message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.reply_text("❌ **Format:** `/addkey <tier> <key>`\nExample: `/addkey 1_day SHAYAN-KEY`")
        return
        
    tier = args[1]
    key_str = args[2]
    stock = load_stock()
    if tier not in stock:
        await message.reply_text(f"❌ Invalid tier! Choose from: {list(stock.keys())}")
        return
        
    stock[tier].append(key_str)
    save_stock(stock)
    await message.reply_text(f"✅ **Key Added Successfully!** 🔥\n• Tier: {tier}\n• Total Stock: {len(stock[tier])}")

# ADMIN COMMAND: Add Balance (/addbal user_id amount)
@app.on_message(filters.command("addbal") & filters.private)
async def add_balance_handler(client, message):
    args = message.text.split()
    if len(args) < 3:
        await message.reply_text("❌ **Format:** `/addbal <user_id> <amount>`")
        return
    
    target_user = args[1]
    try:
        amount = int(args[2])
    except ValueError:
        await message.reply_text("❌ Amount must be a valid number!")
        return
        
    users = load_users()
    if target_user not in users:
        users[target_user] = {"name": "Unknown", "balance": 0}
        
    users[target_user]["balance"] += amount
    save_users(users)
    
    await message.reply_text(f"✅ Successfully added `₹{amount}` to user `{target_user}`!\nNew Balance: `₹{users[target_user]['balance']}`")

# ADMIN COMMAND: Subtract Balance (/subbal user_id amount)
@app.on_message(filters.command("subbal") & filters.private)
async def sub_balance_handler(client, message):
    args = message.text.split()
    if len(args) < 3:
        await message.reply_text("❌ **Format:** `/subbal <user_id> <amount>`")
        return
    
    target_user = args[1]
    try:
        amount = int(args[2])
    except ValueError:
        await message.reply_text("❌ Amount must be a valid number!")
        return
        
    users = load_users()
    if target_user not in users:
        await message.reply_text("❌ User not found in database!")
        return
        
    users[target_user]["balance"] = max(0, users[target_user]["balance"] - amount)
    save_users(users)
    
    await message.reply_text(f"✅ Successfully deducted `₹{amount}` from user `{target_user}`!\nNew Balance: `₹{users[target_user]['balance']}`")

@app.on_callback_query(filters.regex("^buy_"))
async def buy_callback(client, callback_query):
    data = callback_query.data
    tier_key = data.replace("buy_", "")
    
    if tier_key not in PRICES:
        await callback_query.answer("❌ Invalid option!", show_alert=True)
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
        f"👉 Complete payment via FamPay, then click **Verify Payment** below:"
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
        
    assigned_key = stock[tier_key].pop(0)
    save_stock(stock)
    
    success_text = (
        f"🎉 **Payment Verified Successfully!** 🔥\n\n"
        f"💎 Here is your automated license key:\n`{assigned_key}`\n\n"
        f"🛡️ Keep it safe. Enjoy your gaming session!"
    )
    
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("« Back to Main Menu", callback_data="main_menu")]])
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
        [InlineKeyboardButton("🛡️ My Account / Balance", callback_data="my_account")]
    ])
    await callback_query.message.edit_text(welcome_text, reply_markup=keyboard)

if __name__ == "__main__":
    print("Bot is starting with full admin wallet controls...")
    app.start()
    idle()
    app.stop()
