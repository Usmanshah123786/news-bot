"""
main.py - Main entry point
"""

import time
import logging
import sys
from datetime import datetime
from config import CHECK_INTERVAL
from database import init_db
from news import scrape_and_save
from telegram_bot import send_startup, send_news_alert
from database import get_all_news

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_and_send():
    try:
        logger.info("🔍 Checking for new news...")
        saved = scrape_and_save()
        
        if saved > 0:
            logger.info(f"✅ {saved} new news saved!")
            news = get_all_news(limit=saved)
            send_news_alert(news)
        else:
            logger.info("📭 No new news")
    except Exception as e:
        logger.error(f"❌ Error: {e}")

def run_scheduler():
    logger.info(f"⏰ Checking every {CHECK_INTERVAL} minutes")
    check_and_send()
    
    while True:
        try:
            time.sleep(CHECK_INTERVAL * 60)
            check_and_send()
        except KeyboardInterrupt:
            logger.info("🛑 Stopped")
            break
        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}")
            time.sleep(60)

def main():
    print("=" * 60)
    print("🤖 Muslim News Bot (5W+1H Summary)")
    print("=" * 60)
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")
    print(f"⏰ Check Interval: Every {CHECK_INTERVAL} minutes")
    print("=" * 60)
    print("📝 Features: 5W+1H Summary (क्या, किसके साथ, कब, कहाँ, क्यों, कैसे)")
    print("=" * 60)
    
    try:
        init_db()
        send_startup()
        run_scheduler()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()