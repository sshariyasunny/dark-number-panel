"""
DARK BOOSTER NUMBER PANEL - TELEGRAM BOT DAEMON
Automated OTP Group Verification & Web Panel Gateway
Developer: Shariya Sunny
"""
import sys
import os
import time
import json
import urllib.request
import urllib.error
import urllib.parse

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

BOT_TOKEN = "8858961278:AAFtxfv1BFx-QvSSqqoI-rzSvc0RadjQNIM"
GROUP_CHAT_ID = "-1003823185963"
GROUP_INVITE_URL = "https://t.me/+koExPRjJH11iOTFl"
WEB_APP_URL = "https://sshariyasunny.github.io/dark-number-panel/"

# File to store users who have already verified so they are NEVER asked again
VERIFIED_USERS_FILE = os.path.join(os.path.dirname(__file__), "verified_users.json")

def load_verified_users():
    if os.path.exists(VERIFIED_USERS_FILE):
        try:
            with open(VERIFIED_USERS_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_verified_user(user_id):
    users = load_verified_users()
    users.add(str(user_id))
    try:
        with open(VERIFIED_USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(users), f)
    except Exception as e:
        print("Error saving verified user:", e)

def is_user_already_saved(user_id):
    users = load_verified_users()
    return str(user_id) in users

API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

def api_call(method, payload=None):
    url = f"{API_BASE}/{method}"
    headers = {"Content-Type": "application/json"}
    data = json.dumps(payload).encode("utf-8") if payload else None
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=35) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        return json.loads(err_body) if err_body.startswith("{") else None
    except Exception as e:
        print(f"Network error in api_call ({method}):", e)
        return None

def is_user_member_of_group(user_id):
    res = api_call("getChatMember", {"chat_id": GROUP_CHAT_ID, "user_id": user_id})
    if res and res.get("ok"):
        status = res.get("result", {}).get("status")
        if status in ["creator", "administrator", "member", "restricted"]:
            return True
    return False

def send_welcome_panel(chat_id, user_first_name):
    text = (
        f"⚡ <b>DARK BOOSTER NUMBER PANEL</b> ⚡\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👋 হ্যালো <b>{user_first_name}</b>, স্বাগতম!\n"
        f"✅ আপনি একজন অথরাইজড মেম্বার।\n\n"
        f"এখন আপনি যেকোনো কান্ট্রির ভার্চুয়াল নম্বর এবং লাইভ ওটিপি নিয়ে সরাসরি কাজ করতে পারবেন।\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👑 <b>Developer:</b> <b>Shariya Sunny</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 নিচে <b>'🚀 Open Dark Booster Panel'</b> বাটনে ক্লিক করে প্যানেল ওপেন করুন:"
    )
    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "🚀 Open Dark Booster Panel",
                    "web_app": {"url": WEB_APP_URL}
                }
            ],
            [
                {
                    "text": "📢 Official OTP Group",
                    "url": GROUP_INVITE_URL
                }
            ]
        ]
    }
    api_call("sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": keyboard
    })

def send_join_group_prompt(chat_id, user_first_name):
    text = (
        f"⚠️ <b>ACCESS RESTRICTED • ওটিপি গ্রুপে জয়েন আবশ্যক</b> ⚠️\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👋 হ্যালো <b>{user_first_name}</b>,\n"
        f"<b>Dark Booster Number Panel</b> ব্যবহার করতে হলে প্রথমবার আমাদের অফিসিয়াল ওটিপি গ্রুপে যুক্ত হতে হবে!\n\n"
        f"১️⃣ নিচে <b>'📢 ১. ওটিপি গ্রুপে জয়েন করুন'</b> বাটনে ক্লিক করে জয়েন করুন।\n"
        f"২️⃣ জয়েন করার পর <b>'✅ ২. ভেরিফাই ও আনলক'</b> বাটনে ক্লিক করুন।\n\n"
        f"<i>(একবার ভেরিফাই করলে পরবর্তীতে আর কখনো ভেরিফাই করা লাগবে না)</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👑 <b>Developer:</b> <b>Shariya Sunny</b>"
    )
    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "📢 ১. ওটিপি গ্রুপে জয়েন করুন",
                    "url": GROUP_INVITE_URL
                }
            ],
            [
                {
                    "text": "✅ ২. ভেরিফাই ও আনলক",
                    "callback_data": "check_membership"
                }
            ]
        ]
    }
    api_call("sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": keyboard
    })

def handle_update(update):
    # 1. Message update
    if "message" in update:
        msg = update["message"]
        chat = msg.get("chat", {})
        chat_id = chat.get("id")
        user = msg.get("from", {})
        user_id = user.get("id")
        user_name = user.get("first_name", "User")

        # Ignore group messages
        if chat.get("type") in ["group", "supergroup"]:
            return

        if not user_id:
            return

        # Check if already verified previously
        if is_user_already_saved(user_id):
            send_welcome_panel(chat_id, user_name)
            return

        # If not saved yet, check membership now
        if is_user_member_of_group(user_id):
            save_verified_user(user_id)
            send_welcome_panel(chat_id, user_name)
        else:
            send_join_group_prompt(chat_id, user_name)

    # 2. Callback query update (When user taps "Verify & Unlock")
    elif "callback_query" in update:
        cb = update["callback_query"]
        cb_id = cb.get("id")
        data = cb.get("data")
        user = cb.get("from", {})
        user_id = user.get("id")
        user_name = user.get("first_name", "User")
        message = cb.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        msg_id = message.get("message_id")

        if data == "check_membership":
            if is_user_member_of_group(user_id):
                save_verified_user(user_id)
                api_call("answerCallbackQuery", {
                    "callback_query_id": cb_id,
                    "text": "🎉 অভিনন্দন! আপনি সফলভাবে ভেরিফাই হয়েছেন। প্যানেল পার্মানেন্টলি আনলক হয়েছে!",
                    "show_alert": True
                })
                # Edit message to welcome with WebApp button
                text = (
                    f"⚡ <b>ACCESS GRANTED • DARK BOOSTER PANEL</b> ⚡\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🎉 অভিনন্দন <b>{user_name}</b>!\n"
                    f"আপনি সফলভাবে আমাদের ওটিপি গ্রুপে যুক্ত হয়েছেন।\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"👑 <b>Developer:</b> <b>Shariya Sunny</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"👇 নিচে <b>'🚀 Open Dark Booster Panel'</b> বাটনে ক্লিক করে কাজ শুরু করুন:"
                )
                keyboard = {
                    "inline_keyboard": [
                        [
                            {
                                "text": "🚀 Open Dark Booster Panel",
                                "web_app": {"url": WEB_APP_URL}
                            }
                        ]
                    ]
                }
                api_call("editMessageText", {
                    "chat_id": chat_id,
                    "message_id": msg_id,
                    "text": text,
                    "parse_mode": "HTML",
                    "reply_markup": keyboard
                })
            else:
                api_call("answerCallbackQuery", {
                    "callback_query_id": cb_id,
                    "text": "❌ আপনি এখনো ওটিপি গ্রুপে জয়েন করেননি!\n\nঅনুগ্রহ করে আগে '১. ওটিপি গ্রুপে জয়েন করুন' বাটনে ক্লিক করে গ্রুপে যুক্ত হোন।",
                    "show_alert": True
                })

def main():
    print("Dark Booster Telegram Bot Gateway is active...")
    offset = None
    while True:
        try:
            params = {"timeout": 30}
            if offset is not None:
                params["offset"] = offset

            res = api_call("getUpdates", params)
            if res and res.get("ok"):
                for update in res.get("result", []):
                    offset = update["update_id"] + 1
                    handle_update(update)
            time.sleep(1)
        except Exception as e:
            print("Polling loop error:", e)
            time.sleep(3)

if __name__ == "__main__":
    main()
