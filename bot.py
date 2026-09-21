import logging
import asyncio
import re
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '8556051063:AAHk6uGV3hinQwyoVa10LkH7CpNAyYyx164'
ADMIN_ID = 8556051063

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_data = {}
user_balance = {}

# Async 1SecMail Handler
async def get_1secmail_account():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1") as resp:
                res = await resp.json()
                if res:
                    email = res[0]
                    login, domain = email.split('@')
                    return email, login, domain
    except Exception as e:
        print("Mail Gen Error:", e)
    return None, None, None

async def get_1secmail_otp(login, domain):
    try:
        url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                msgs = await resp.json()
                if msgs:
                    msg_id = msgs[0]['id']
                    msg_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={msg_id}"
                    async with session.get(msg_url) as msg_resp:
                        msg_data = await msg_resp.json()
                        body = msg_data.get('body', '') or msg_data.get('textBody', '')
                        match = re.search(r'\b\d{6}\b', body) or re.search(r'\b\d{4}\b', body)
                        if match:
                            return match.group(0)
                        return body[:100]
    except Exception as e:
        print("OTP Check Error:", e)
    return None

def get_main_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🛒 Account Sell", callback_data="acc_sell"),
        InlineKeyboardButton("💰 Balance", callback_data="check_balance"),
        InlineKeyboardButton("💳 Withdraw", callback_data="withdraw"),
        InlineKeyboardButton("💬 Support Admin", callback_data="contact_support")
    )
    return kb

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_data.pop(message.from_user.id, None)
    await message.reply("👋 **Trust ID Store Bot**-এ স্বাগতম!\n\nনিচে থেকে আপনার প্রয়োজনীয় অপশন বেছে নিন:", reply_markup=get_main_keyboard(), parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.data == 'acc_sell')
async def process_acc_sell(callback_query: types.CallbackQuery):
    await callback_query.answer()
    uid = callback_query.from_user.id
    user_data.pop(uid, None)
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🎵 TikTok Sell", callback_data="tiktok_menu"),
        InlineKeyboardButton("📧 Gmail Sell", callback_data="gmail_menu"),
        InlineKeyboardButton("📘 Facebook", callback_data="notice_fb"),
        InlineKeyboardButton("🎮 Free Fire", callback_data="notice_ff"),
        InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")
    )
    try:
        await bot.edit_message_text("অ্যাাকাউন্ট বিক্রি করার জন্য ক্যাটাগরি সিলেক্ট করুন:", 
                                    chat_id=uid, 
                                    message_id=callback_query.message.message_id, 
                                    reply_markup=kb)
    except:
        await bot.send_message(uid, "অ্যাাকাউন্ট বিক্রি করার জন্য ক্যাটাগরি সিলেক্ট করুন:", reply_markup=kb)

# TikTok Menu Handler
@dp.callback_query_handler(lambda c: c.data == 'tiktok_menu')
async def process_tiktok_menu(callback_query: types.CallbackQuery):
    await callback_query.answer()
    uid = callback_query.from_user.id
    user_data[uid] = {'step': 'tiktok_deal'}
    
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📧 Get Temp Mail", callback_data="gen_mail"),
        InlineKeyboardButton("🔄 Get OTP", callback_data="get_otp"),
        InlineKeyboardButton("📤 Submit Deal", callback_data="submit_deal"),
        InlineKeyboardButton("🔙 Back", callback_data="acc_sell")
    )
    
    price_text = (
        "🎵 **TikTok Account Sell Rates & Process**\n\n"
        "📌 **প্রাইস লিস্ট:**\n"
        "• 1k Followers + 10k Likes ➔ **180 BDT**\n"
        "• 2k Followers + 10k Likes ➔ **270 BDT**\n"
        "• 3k Followers + 15k Likes ➔ **330 BDT**\n"
        "• 4k Followers + 20k Likes ➔ **430 BDT**\n"
        "• 5k Followers + 20k Likes ➔ **500 BDT**\n"
        "• 6k Followers + 20k-25k Likes ➔ **550 BDT**\n"
        "• 7k Followers + 20k-25k Likes ➔ **600 BDT**\n"
        "• 8k Followers + 20k-25k Likes ➔ **650 BDT**\n"
        "• 9k Followers + 20k-25k Likes ➔ **700 BDT**\n"
        "• 10k Followers + 20k-25k Likes ➔ **1000 BDT**\n\n"
        "📝 **কাজ করার নিয়ম:**\n"
        "১. 'Get Temp Mail' দিয়ে মেইল নিয়ে টিকটকে বসান।\n"
        "২. 'Get OTP' দিয়ে কোড নিন।\n"
        "৩. অ্যাকাউন্ট তৈরি শেষে 'Submit Deal'-এ পাসওয়ার্ড ও বিস্তারিত পাঠান।"
    )
    
    await bot.send_message(uid, price_text, reply_markup=kb, parse_mode="Markdown")

# Gmail Menu Handler
@dp.callback_query_handler(lambda c: c.data == 'gmail_menu')
async def process_gmail_menu(callback_query: types.CallbackQuery):
    await callback_query.answer()
    uid = callback_query.from_user.id
    user_data[uid] = {'step': 'waiting_for_gmail'}
    
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🔙 Back", callback_data="acc_sell"))
    
    text = (
        "📧 **Gmail Account Sell Section**\n\n"
        "💰 **প্রতিটি জিমেইলের দাম: ৩০ টাকা**\n\n"
        "📝 **নিয়মাবলী:**\n"
        "আপনার বিক্রয় করার জিমেইলটি এখানে লিখে সেন্ড করুন (পাঠিয়ে দিন)।"
    )
    await bot.send_message(uid, text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.data == 'contact_support')
async def process_contact_support(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await bot.send_message(callback_query.from_user.id, "💬 যেকোনো সাহায্যের জন্য যেকোনো প্রশ্ন লিখে মেসেজ দিন, অ্যাডমিন সরাসরি মেসেজ পেয়ে যাবে।")

@dp.callback_query_handler(lambda c: c.data in ['notice_fb', 'notice_ff'])
async def process_notices(callback_query: types.CallbackQuery):
    services = {'notice_fb': 'Facebook', 'notice_ff': 'Free Fire'}
    name = services.get(callback_query.data, 'এই')
    await callback_query.answer(f"⚠️ দুঃখিত! {name} অ্যাকাউন্ট নেওয়া বর্তমানে সাময়িকভাবে বন্ধ আছে।", show_alert=True)

@dp.callback_query_handler(lambda c: c.data == 'main_menu')
async def process_main_menu(callback_query: types.CallbackQuery):
    await callback_query.answer()
    uid = callback_query.from_user.id
    user_data.pop(uid, None)
    kb = get_main_keyboard()
    try:
        await bot.edit_message_text("👋 **Trust ID Store Bot**-এ স্বাগতম!\n\nনিচে থেকে আপনার প্রয়োজনীয় অপশন বেছে নিন:", 
                                    chat_id=uid, 
                                    message_id=callback_query.message.message_id, 
                                    reply_markup=kb, parse_mode="Markdown")
    except:
        await bot.send_message(uid, "👋 **Trust ID Store Bot**-এ স্বাগতম!\n\nনিচে থেকে আপনার প্রয়োজনীয় অপশন বেছে নিন:", reply_markup=kb, parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.data == 'check_balance')
async def process_balance(callback_query: types.CallbackQuery):
    await callback_query.answer()
    uid = callback_query.from_user.id
    bal = user_balance.get(uid, 0.0)
    await bot.send_message(uid, f"💰 **আপনার বর্তমান ব্যালেন্স:** `{bal:.2f} BDT`", parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.data == 'withdraw')
async def process_withdraw(callback_query: types.CallbackQuery):
    await callback_query.answer()
    uid = callback_query.from_user.id
    bal = user_balance.get(uid, 0.0)
    if bal < 50:
        await bot.send_message(uid, f"❌ উইথড্র করতে সর্বনিম্ন ৫০ টাকা ব্যালেন্স লাগবে। আপনার আছে: `{bal:.2f} BDT`", parse_mode="Markdown")
    else:
        await bot.send_message(uid, "বিকাশ/নগদ নম্বর এবং টাকার পরিমাণ লিখে মেসেজ দিন। অ্যাডমিন এটি যাচাই করে পেমেন্ট দেবে।")

@dp.callback_query_handler(lambda c: c.data == 'gen_mail')
async def process_gen_mail(callback_query: types.CallbackQuery):
    await callback_query.answer("মেইল তৈরি হচ্ছে...")
    uid = callback_query.from_user.id
    email, login, domain = await get_1secmail_account()
    if email:
        if uid not in user_data:
            user_data[uid] = {}
        user_data[uid]['temp_email'] = email
        user_data[uid]['login'] = login
        user_data[uid]['domain'] = domain
        await bot.send_message(uid, f"আপনার টেম্প মেইল:\n`{email}`\n\nএটি টিকটকে ব্যবহার করে OTP পাঠান।", parse_mode="Markdown")
    else:
        await bot.send_message(uid, "মেইল তৈরিতে সমস্যা হয়েছে। আবার চেষ্টা করুন।")

@dp.callback_query_handler(lambda c: c.data == 'get_otp')
async def process_get_otp(callback_query: types.CallbackQuery):
    await callback_query.answer("ওটিপি চেক করা হচ্ছে...")
    uid = callback_query.from_user.id
    data = user_data.get(uid, {})
    if 'login' not in data:
        await bot.send_message(uid, "আগে 'Get Temp Mail' দিয়ে একটি মেইল তৈরি করুন।")
        return
    otp = await get_1secmail_otp(data['login'], data['domain'])
    if otp:
        await bot.send_message(uid, f"আপনার ওটিপি কোড: `{otp}`", parse_mode="Markdown")
    else:
        await bot.send_message(uid, "এখনো কোনো ওটিপি আসেনি। আবার চেষ্টা করুন।")

@dp.callback_query_handler(lambda c: c.data == 'submit_deal')
async def process_submit_deal(callback_query: types.CallbackQuery):
    await callback_query.answer()
    uid = callback_query.from_user.id
    if uid not in user_data:
        user_data[uid] = {}
    user_data[uid]['step'] = 'waiting_for_tiktok_pass'
    await bot.send_message(uid, "আপনার টিকটক অ্যাকাউন্টের পাসওয়ার্ড লিখে পাঠান।")

# User Message Handler
@dp.message_handler()
async def handle_user_messages(message: types.Message):
    uid = message.from_user.id
    user_state = user_data.get(uid, {}).get('step')

    # 1. Gmail Step 1: User sends Gmail address
    if user_state == 'waiting_for_gmail':
        gmail_address = message.text
        user_data[uid] = {'step': 'waiting_for_gmail_pass', 'gmail': gmail_address}
        await message.reply("ধন্যবাদ! এখন এই জিমেইলের **পাসওয়ার্ড** লিখে সেন্ড করুন।")
        return

    # 2. Gmail Step 2: User sends Gmail Password
    elif user_state == 'waiting_for_gmail_pass':
        gmail_pass = message.text
        gmail_addr = user_data.get(uid, {}).get('gmail', 'N/A')
        
        admin_msg = (
            f"🚨 **নতুন জিমেইল ডিল এসেছে!** (মূল্য: ৩০ টাকা)\n\n"
            f"👤 ইউজার: {message.from_user.full_name} (@{message.from_user.username})\n"
            f"🆔 ID: `{uid}`\n"
            f"📧 জিমেইল: `{gmail_addr}`\n"
            f"🔑 পাসওয়ার্ড: `{gmail_pass}`"
        )
        await bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
        user_data.pop(uid, None)
        
        reply_text = (
            "✅ আপনার জিমেইল এবং পাসওয়ার্ড সফলভাবে অ্যাডমিনের কাছে পাঠানো হয়েছে!\n\n"
            "⚠️ **জরুরী নির্দেশ:** অনুগ্রহ করে আপনার ডিভাইস বা ব্রাউজার থেকে এই জিমেইলটি **লগআউট (Log out) করে দিন**।"
        )
        await message.reply(reply_text)
        return

    # 3. TikTok Password Submission Step
    elif user_state == 'waiting_for_tiktok_pass':
        tiktok_pass = message.text
        mail_info = user_data.get(uid, {}).get('temp_email', 'N/A')
        
        admin_msg = (
            f"🚨 **নতুন টিকটক ডিল এসেছে!**\n\n"
            f"👤 ইউজার: {message.from_user.full_name} (@{message.from_user.username})\n"
            f"🆔 ID: `{uid}`\n"
            f"📧 মেইল: `{mail_info}`\n"
            f"🔑 পাসওয়ার্ড: `{tiktok_pass}`"
        )
        await bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
        user_data.pop(uid, None)
        await message.reply("আপনার টিকটকের তথ্য অ্যাডমিনের কাছে পাঠানো হয়েছে!")
        return

    # Default General Support / Inquiry Message Handler
    else:
        admin_msg = (
            f"💬 **সাধারণ মেসেজ/প্রশ্ন এসেছে!**\n\n"
            f"👤 ইউজার: {message.from_user.full_name} (@{message.from_user.username})\n"
            f"🆔 ID: `{uid}`\n"
            f"📝 মেসেজ: {message.text}"
        )
        await bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
        await message.reply("আপনার মেসেজটি অ্যাডমিনের কাছে পাঠানো হয়েছে!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
