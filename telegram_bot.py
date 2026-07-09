"""
telegram_bot.py - Telegram Bot with 5W+1H Summary
"""

import requests
import logging
from datetime import datetime
from config import BOT_TOKEN, CHAT_ID
from news import generate_5w1h_summary

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_message(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            logger.info("✅ Message sent")
            return True
        else:
            logger.error(f"❌ Failed: {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

def format_news_with_summary(news, index=None):
    """Format news with 5W+1H summary"""
    
    if isinstance(news, tuple):
        title = news[0] if len(news) > 0 else 'No Title'
        link = news[1] if len(news) > 1 else ''
        source = news[2] if len(news) > 2 else 'Unknown'
        date = news[3] if len(news) > 3 else ''
        summary = news[4] if len(news) > 4 else ''
    else:
        title = news.get('title', 'No Title')
        link = news.get('link', '')
        source = news.get('source', 'Unknown')
        date = news.get('published_date', '')
        summary = news.get('summary', '')
    
    # Generate 5W+1H summary
    smart = generate_5w1h_summary(title, summary)
    
    number = f"<b>{index}.</b> " if index else ""
    
    news_text = f"""
{number}<b>📰 {title[:120]}</b>

📝 <b>Quick Summary:</b>
┌─────────────────────
│ 📌 <b>क्या:</b> {smart['what'][:60]}...
│ 👤 <b>किसके साथ:</b> {smart['who']}
│ 📅 <b>कब:</b> {smart['when']}
│ 📍 <b>कहाँ:</b> {smart['where']}
│ ❓ <b>क्यों:</b> {smart['why']}
│ 🔧 <b>कैसे:</b> {smart['how']}
└─────────────────────

🔗 <a href="{link}">पूरी खबर पढ़ें</a>
📅 {date[:16] if date else 'Recent'}
📰 {source}
"""
    return news_text

def send_news_alert(news_list):
    if not news_list:
        return False
    
    header = f"""
<b>📰 Muslim News Alert</b>
<i>{datetime.now().strftime('%d %B %Y, %I:%M %p')}</i>
━━━━━━━━━━━━━━━━━━━━

<b>📌 {len(news_list)} New News</b>

"""
    
    formatted = []
    for idx, news in enumerate(news_list, 1):
        formatted.append(format_news_with_summary(news, idx))
    
    full = header + "\n━━━━━━━━━━━━━━━━━\n".join(formatted)
    
    if len(full) > 4000:
        parts = []
        current = header
        for text in formatted:
            if len(current + text) > 3500:
                parts.append(current)
                current = "📌 <b>Continued...</b>\n"
            current += text + "\n━━━━━━━━━━━━━━━━━\n"
        if current:
            parts.append(current)
        for part in parts:
            send_message(part)
    else:
        send_message(full)
    
    return True

def send_startup():
    msg = """
<b>🚀 Muslim News Bot Started!</b>

✅ System active
🔍 Monitoring news
⏰ Check: Every 5 minutes

📝 <b>5W+1H Summary:</b>
   क्या, किसके साथ, कब, कहाँ, क्यों, कैसे
"""
    return send_message(msg)

def send_test_news():
    from database import get_all_news
    news_list = get_all_news(limit=10)
    if not news_list:
        return send_message("❌ No news in database")
    return send_news_alert(news_list)