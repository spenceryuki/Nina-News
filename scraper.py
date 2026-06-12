import os
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

def generate_rss():
    TARGET_URL = "https://www.ninanews.com/website"
    
    # Retrieve the secret token from your GitHub Actions environment
    api_key = os.getenv("SCRAPER_API_KEY")
    
    if not api_key:
        raise ValueError("SCRAPER_API_KEY secret is missing from GitHub repository settings.")

    print("Routing request through proxy gateway to clear Cloudflare...")
    # The API handles browser fingerprints, rotation, and residential IPs automatically
    gateway_url = f"http://api.scraperapi.com?api_key={api_key}&url={TARGET_URL}"
    
    try:
        response = requests.get(gateway_url, timeout=60)
    except Exception as err:
        raise RuntimeError(f"Gateway connection failed: {err}")
    
    if response.status_code != 200:
        raise RuntimeError(f"Proxy gateway returned status code: {response.status_code}")

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
        
        if not link_url or len(title_text) < 12 or link_url in seen_links:
            continue
            
        if not link_url.startswith('http'):
            link_url = f"https://www.ninanews.com{link_url}"

        seen_links.add(link_url)
        
        fe = fg.add_entry()
        fe.id(link_url)
        fe.title(title_text)
        fe.link(href=link_url)
        
        count += 1
        if count >= 25: 
            break

    if count == 0:
        raise ValueError("Connected successfully, but no news elements matched the parser filters.")

    fg.rss_file('feed.xml')
    print(f"Successfully generated feed.xml with {count} entries.")

if __name__ == "__main__":
    generate_rss()
