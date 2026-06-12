import os
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import cloudscraper

def generate_rss():
    TARGET_URL = "https://www.ninanews.com/website"
    
    # Bypass Cloudflare and fetch HTML
    scraper = cloudscraper.create_scraper(delay=10)
    response = scraper.get(TARGET_URL)
    
    if response.status_code != 200:
        print(f"Failed to fetch page. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # Initialize RSS Feed Generator
    fg = FeedGenerator()
    fg.id(TARGET_URL)
    fg.title('NINA News Custom Feed')
    fg.link(href=TARGET_URL, rel='alternate')
    fg.description('Automated feed bypassing security walls.')
    fg.language('en')

    # Quick parsing logic (adjust selectors based on target HTML if needed)
    # This looks for standard hyperlinks inside the page body
    articles = soup.find_all('a') 
    
    seen_links = set()
    count = 0
    for article in articles:
        title_text = article.text.strip()
        link_url = article.get('href')
        
        if not link_url or len(title_text) < 15 or link_url in seen_links:
            continue
            
        if not link_url.startswith('http'):
            link_url = f"https://www.ninanews.com{link_url}"

        seen_links.add(link_url)
        
        fe = fg.add_entry()
        fe.id(link_url)
        fe.title(title_text)
        fe.link(href=link_url)
        
        count += 1
        if count >= 20: # Limit to 20 items
            break

    fg.rss_file('feed.xml')
    print("Successfully generated feed.xml")

if __name__ == "__main__":
    generate_rss()
