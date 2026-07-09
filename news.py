"""
news.py - News Scraper with 5W+1H Summary
"""

import feedparser
import logging
import re
from urllib.parse import quote
from datetime import datetime
from config import KEYWORDS
from database import save_news, get_all_saved_links

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_NEWS_PER_KEYWORD = 5
MAX_TOTAL_NEWS = 30

def generate_5w1h_summary(title, summary_text=""):
    """Generate 5W+1H summary from news"""
    full_text = f"{title} {summary_text}"
    
    # Extract basic info
    summary = {
        'what': title[:80],
        'who': extract_who(full_text),
        'when': extract_when(full_text),
        'where': extract_where(full_text),
        'why': extract_why(full_text),
        'how': extract_how(full_text)
    }
    return summary

def extract_who(text):
    """Kiske sath?"""
    who_keywords = ['Muslim', 'Hindu', 'Sikh', 'Christian', 'minority', 
                   'community', 'police', 'government', 'people']
    for word in who_keywords:
        if word.lower() in text.lower():
            return word
    return "People"

def extract_when(text):
    """Kab?"""
    # Check for date patterns
    import re
    date_match = re.search(r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}', text)
    if date_match:
        return date_match.group()
    
    if 'today' in text.lower():
        return 'Today'
    elif 'yesterday' in text.lower():
        return 'Yesterday'
    else:
        return datetime.now().strftime('%d %b %Y')

def extract_where(text):
    """Kahan?"""
    places = ['Delhi', 'Mumbai', 'Kolkata', 'Chennai', 'Bangalore',
             'Hyderabad', 'Ahmedabad', 'Pune', 'Lucknow', 'Kanpur',
             'Uttar Pradesh', 'Maharashtra', 'Gujarat', 'Rajasthan',
             'Bihar', 'West Bengal', 'Tamil Nadu', 'Kerala', 'Karnataka']
    for place in places:
        if place.lower() in text.lower():
            return place
    return "India"

def extract_why(text):
    """Kyun?"""
    why_keywords = ['over', 'due to', 'because of', 'against', 'for', 'demanding']
    words = text.split()
    for i, word in enumerate(words):
        if word.lower() in why_keywords:
            return ' '.join(words[i:i+4])[:60]
    return "Issue/Conflict"

def extract_how(text):
    """Kaise?"""
    how_keywords = ['violent', 'peaceful', 'sudden', 'planned', 'organized']
    for word in how_keywords:
        if word.lower() in text.lower():
            return word.capitalize()
    return "Through protest/demonstration"

def fetch_news(keyword, limit=MAX_NEWS_PER_KEYWORD):
    try:
        encoded = quote(keyword)
        url = f"https://news.google.com/rss/search?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(url)
        
        news_list = []
        count = 0
        
        for entry in feed.entries:
            if count >= limit:
                break
            
            title = entry.get('title', 'No Title')
            link = entry.get('link', '')
            
            if not link:
                continue
            
            published = entry.get('published', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            if published:
                try:
                    published = datetime.strptime(published, '%a, %d %b %Y %H:%M:%S %Z').strftime('%Y-%m-%d %H:%M:%S')
                except:
                    published = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            summary = entry.get('summary', '')
            if summary:
                summary = re.sub(r'<[^>]+>', '', summary)[:300]
            
            # Generate 5W+1H summary
            smart_summary = generate_5w1h_summary(title, summary)
            
            news_list.append({
                'title': title,
                'link': link,
                'source': f'Google News - {keyword}',
                'published_date': published,
                'summary': summary,
                'smart_summary': smart_summary
            })
            count += 1
        
        return news_list
    except Exception as e:
        logger.error(f"Error fetching {keyword}: {e}")
        return []

def get_all_news():
    all_news = []
    seen_links = set()
    
    for keyword in KEYWORDS:
        items = fetch_news(keyword)
        for news in items:
            if news['link'] not in seen_links:
                seen_links.add(news['link'])
                all_news.append(news)
        if len(all_news) >= MAX_TOTAL_NEWS:
            break
    
    logger.info(f"✅ Total {len(all_news)} news fetched")
    return all_news

def get_new_news():
    all_news = get_all_news()
    saved_links = get_all_saved_links()
    
    new_news = []
    for news in all_news:
        if news['link'] not in saved_links:
            new_news.append(news)
    
    logger.info(f"📌 {len(new_news)} new news found")
    return new_news

def scrape_and_save():
    new_news = get_new_news()
    if not new_news:
        return 0
    
    saved = 0
    for news in new_news:
        if save_news(news['title'], news['link'], news['source'], 
                     news['published_date'], news['summary']):
            saved += 1
            logger.info(f"💾 Saved: {news['title'][:40]}...")
    
    return saved