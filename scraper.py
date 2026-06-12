import os
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from curl_cffi import requests as cf_requests

def generate_rss():
    TARGET_URL = "https://www.ninanews.com/website"
    
    # Alternative free proxy gate to mask the GitHub Actions Datacenter IP
    # This routes the request through a residential-looking node
    PROXY_URL = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
    
    proxies = None
    try:
        print("Fetching a fresh proxy list to bypass datacenter blocking...")
        proxy_res = cf_requests.get(PROXY_URL, timeout=10)
        if proxy_res.status_code == 200 and proxy_res.text.strip():
            list_proxies = proxy_res.text.strip().split("\r\n")
            if list_proxies:
                chosen_proxy = list_proxies[0]
                proxies = {"http": f"http://{chosen_proxy}", "https": f"http://{chosen_proxy}"}
                print(f"Using proxy: {chosen_proxy}")
    except Exception as e:
        print(f"Proxy fetch failed or timed out ({e}), proceeding with direct connection...")

    print("Fetching NINA News via browser engine impersonation...")
    try:
        response = cf_requests.get(
            TARGET_URL, 
            impersonate="chrome124", 
            proxies=proxies,
            timeout=25,
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1"
            }
        )
    except Exception as err:
        raise RuntimeError(f"Connection dropped completely: {err}")
    
    if response.status_code != 200:
        raise RuntimeError(f"Cloudflare blocked request. Status Code: {response.status_code}. Response snippet: {response.text[:300]}")

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
        
        # Look for standard news item links
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
        raise ValueError("Connected successfully, but no news elements matched the criteria inside the HTML layout.")

    fg.rss_file('feed.xml')
    print(f"Successfully generated feed.xml with {count} entries.")

if __name__ == "__main__":
    generate_rss()
