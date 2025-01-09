import os
import sys
import json
import django

from tqdm import tqdm
from termcolor import colored

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'foundyou_api')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from app.models import CustomUser, Location

JSON_FILE = "app/json_forms/users.json"
POSITIVE_COLOR = "green"
NEGATIVE_COLOR = "red"

def load_users_from_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            users = json.load(file)
            return users
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: File {file_path} contains invalid JSON.")
        return []

def add_location_to_user(user, user_data):
    try:
        location_data = {
            "latitude": user_data["location"][0],
            "longitude": user_data["location"][1]
        }
        location = Location.objects.create(**location_data)
        user.location = location
        user.save()
    except Exception as e:
        print(colored(f"Error adding location {user_data.get('location')}: {e}", NEGATIVE_COLOR))

def add_users_to_db(users):
    added_users = 0
    for user_data in tqdm(users, desc="Adding users to DB"):
        try:
            user = CustomUser(
                username=user_data["username"],
                email=user_data["email"],
                sex=user_data["sex"],
                birthday=user_data["birthday"],
                bio=user_data["bio"],
                passions=user_data["passions"]
            )
            user.set_password(user_data["password"])
            user.save()
            add_location_to_user(user, user_data)
            if CustomUser.objects.get(email=user_data["email"]):
                added_users += 1

        except Exception as e:
            print(colored(f"Error adding user {user_data.get('username')}: {e}", NEGATIVE_COLOR))
    return added_users

if __name__ == "__main__":
    users = load_users_from_json(JSON_FILE)
    added_users = 0
    print(f"{len(users)} users to add")
    if users:
        added_users = add_users_to_db(users)
    else:
        print("No users to add.")
    print(colored(f"Job is done. Number of added users: {added_users}", POSITIVE_COLOR))
