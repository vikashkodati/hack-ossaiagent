import requests
from icalendar import Calendar
from datetime import datetime
import json
import re

print("hi!")

def fetch_ics_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def extract_luma_url(description):
    urls = re.findall(r'https://lu\.ma/\S+', description)
    return urls[0] if urls else ""

def parse_ics_and_extract_events(ics_data):
    cal = Calendar.from_ical(ics_data)
    events = []

    for component in cal.walk():
        if component.name == "VEVENT":
            description = str(component.get('description', ''))
            event = {
                "start": component.get('dtstart').dt.isoformat(),
                "end": component.get('dtend').dt.isoformat(),
                "id": str(component.get('uid')),
                "summary": str(component.get('summary', '')),
                "description": description,
                "location": str(component.get('location', '')),
                "url": extract_luma_url(description)
            }
            events.append(event)

    return events

def write_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    url = "https://api.lu.ma/ics/get?entity=discover&id=discplace-FQ4E58PeBMHGTKK"
    output_file = "luma.json"
    
    try:
        ics_data = fetch_ics_data(url)
        events = parse_ics_and_extract_events(ics_data)
        write_to_json(events, output_file)
        
        print(f"Successfully extracted {len(events)} events and wrote them to {output_file}")
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
    except ValueError as e:
        print(f"Error parsing ICS data: {e}")
    except IOError as e:
        print(f"Error writing to file: {e}")

if __name__ == "__main__":
    main()