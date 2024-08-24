import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta

def get_event_urls(url):
    response = requests.get(url)
    pattern = r'"eventUrl":"(https://www\.meetup\.com/[^/]+/events/\d+/)"'
    event_urls = re.findall(pattern, response.text)

    # Remove duplicates and sort
    event_urls = sorted(set(event_urls))

    print(f"Found {len(event_urls)} unique event URLs. First few URLs:")
    for url in event_urls[:5]:
        print(url)

    return event_urls

def parse_event_page(url):
    response = requests.get(url)
    with open("pg.html", 'w', encoding='utf-8') as f:
        f.write(response.text)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract event data
    title = soup.find('h1', class_='overflow-hidden').text.strip()
    
    date_time = soup.find('time')
    start_time = date_time['datetime'] if date_time else None
    
    # Assuming end time is 1 hour after start time if not provided
    end_time = (datetime.fromisoformat(start_time) + timedelta(hours=1)).isoformat() if start_time else None
    
    description = soup.find('div', class_='break-words').text.strip()
    
    location_elem = soup.find('div', {'data-testid': 'venue-name-value'})
    location = location_elem.text.strip() if location_elem else "Online event"
    
    event_id = url.split('/')[-1]
    
    # Collect event tags
    tags = [tag.text for tag in soup.find_all('a', class_='tag--topic')]
    
    return {
        "start": start_time,
        "end": end_time,
        "id": event_id,
        "summary": title,
        "description": description + "\n\nTags: " + ", ".join(tags),
        "location": location,
        "url": url
    }

def main():
    base_url = "https://www.meetup.com/find/?location=us--wa--Seattle&source=EVENTS&keywords=software&dateRange=next-week&distance=fiftyMiles"
    event_urls = get_event_urls(base_url)
    
    all_events = []
    for url in event_urls:
        event_data = parse_event_page(url)
        all_events.append(event_data)
    
    # Save to JSON file
    with open('meetup_events.json', 'w') as f:
        json.dump(all_events, f, indent=2)

    print(f"Scraped {len(all_events)} events and saved to meetup_events.json")

if __name__ == "__main__":
    main()