import logging
import requests
from pyrogram import Client, filters
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

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user_name = message.from_user.first_name
    
    welcome_text = (
        f"👋 Hello **{user_name}**!\n\n"
        f"⚡ Welcome to **Gaming Shayan** Automated Store.\n"
        f"Here you can buy high-speed license keys instantly with automated delivery.\n\n"
        f"👇 Select your preferred plan below:"
    )
    
    # Shinigami style inline buttons
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 1 Day - ₹60", callback_data="buy_1_day"),
         InlineKeyboardButton("📅 3 Days - ₹140", callback_data="buy_3_days")],
        [InlineKeyboardButton("📅 7 Days - ₹239", callback_data="buy_7_days"),
         InlineKeyboardButton("📅 15 Days - ₹370", callback_data="buy_15_days")],
        [InlineKeyboardButton("📅 30 Days - ₹589", callback_data="buy_30_days")],
        [InlineKeyboardButton("👤 My Account / Support", callback_data="support")]
    ])
    
    await message.reply_text(welcome_text, reply_markup=keyboard)

@app.on_callback_query(filters.regex("^buy_"))
async def buy_callback(client, callback_query):
    data = callback_query.data
    tier_key = data.replace("buy_", "")
    
    if tier_key not in PRICES:
        await callback_query.answer("Invalid option selected!", show_alert=True)
        return
        
    plan = PRICES[tier_key]
    amount = plan["price"]
    days = plan["days"]
    
    await callback_query.answer(f"Generating payment link for {days} Day(s)...")
    
    # FamPay API integration call simulation to generate payment link
    # Real integration uses FAMPAY_API_KEY for creating dynamic orders
    payment_link = f"https://fampay.in/pay/simulate_order?amount={amount}&key={FAMPAY_API_KEY[:8]}"
    
    checkout_text = (
        f"🛒 **Order Summary:**\n"
        f"• **Product:** License Key ({days} Days)\n"
        f"• **Amount:** ₹{amount}\n\n"
        f"👉 Click the button below to complete your payment securely via FamPay:"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Pay Now", url=payment_link)],
        [InlineKeyboardButton("🔄 Verify Payment", callback_data=f"verify_{tier_key}")],
        [InlineKeyboardButton("« Back to Menu", callback_data="main_menu")]
    ])
    
    await callback_query.message.edit_text(checkout_text, reply_markup=keyboard)

@app.on_callback_query(filters.regex("^main_menu$"))
async def main_menu_callback(client, callback_query):
    welcome_text = "⚡ **Main Menu**\nChoose your required package below:"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 1 Day - ₹60", callback_data="buy_1_day"),
         InlineKeyboardButton("📅 3 Days - ₹140", callback_data="buy_3_days")],
        [InlineKeyboardButton("📅 7 Days - ₹239", callback_data="buy_7_days"),
         InlineKeyboardButton("📅 15 Days - ₹370", callback_data="buy_15_days")],
        [InlineKeyboardButton("📅 30 Days - ₹589", callback_data="buy_30_days")],
        [InlineKeyboardButton("👤 My Account / Support", callback_data="support")]
    ])
    await callback_query.message.edit_text(welcome_text, reply_markup=keyboard)

@app.on_callback_query(filters.regex("^support$"))
async def support_callback(client, callback_query):
    support_text = "💬 For any issues or key activation support, contact owner: @Gamingshayan"
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="main_menu")]])
    await callback_query.message.edit_text(support_text, reply_markup=keyboard)

if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
  
