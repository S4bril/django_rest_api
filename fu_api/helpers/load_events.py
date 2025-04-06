import os
import sys
import json
import django

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'fu_api')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from fu_api.models.custom_user_model import CustomUser
from fu_api.models.event_model import Event
from fu_api.models.location_model import Location

JSON_FILE = "app/json_forms/events.json"
POSITIVE_COLOR = "green"
NEGATIVE_COLOR = "red"

def load_events_from_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: File {file_path} contains invalid JSON.")
        return []

def add_events_to_db(user, events):
    for event_data in events:
        lat = event_data.get('location', {}).get('latitude')
        long = event_data.get('location', {}).get('longitude')
        
        if lat and long:
            location, created = Location.objects.get_or_create(
                latitude=lat, longitude=long
            )
        else:
            location = None
        # event = Event.objects.create(**e)
        user.owned_events = location
        user.save()

if __name__ == "__main__":
    events = load_events_from_json(JSON_FILE)
