import os
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from curl_cffi import requests as cf_requests

def generate_rss():
    TARGET_URL = "https://www.ninanews.com/website"
    
    print("Fetching page using Chrome 124 browser impersonation...")
    # Impersonate a real Chrome engine to slide past Cloudflare signatures
    response = cf_requests.get(TARGET_URL, impersonate="chrome124", timeout=30)
    
    if response.status_code != 200:
        raise RuntimeError(f"Cloudflare blocked request. Status Code: {response.status_code}. Response snippet: {response.text[:500]}")

    soup = BeautifulSoup(response.text, 'html.parser')

    # Initialize RSS Feed Generator
    fg = FeedGenerator()
    fg.id(TARGET_URL)
    fg.title('NINA News Custom Feed')
    fg.link(href=TARGET_URL, rel='alternate')
    fg.description('Automated feed bypassing security walls.')
    fg.language('en')

    # Parse hyperlinks
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
        if count >= 20: 
            break

    if count == 0:
        raise ValueError("Fetched page successfully, but failed to extract any qualifying news anchors from the source HTML.")

    fg.rss_file('feed.xml')
    print(f"Successfully generated feed.xml with {count} entries.")

if __name__ == "__main__":
    generate_rss()
