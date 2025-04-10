import csv
from tqdm import tqdm
from termcolor import colored
from fu_api.models.custom_user_model import CustomUser
from fu_api.models.location_model import Location

CSV_FILE = "fu_api/json_forms/users.csv"
GREEN = "green"
RED = "red"

def load_users_from_csv(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            users = []
            for row in reader:
                user = dict(row)

                raw_passions = user.get("passions", "")
                if isinstance(raw_passions, str):
                    user["passions"] = [int(pid) for pid in raw_passions.split(";") if pid.strip().isdigit()]
                else:
                    user["passions"] = []

                raw_location = user.get("location", "")
                if isinstance(raw_location, str) and "," in raw_location:
                    try:
                        lat_str, lon_str = raw_location.split(",")
                        user["location"] = [float(lat_str.strip()), float(lon_str.strip())]
                    except ValueError:
                        user["location"] = []
                else:
                    user["location"] = []

                user["sex_id"] = int(user.get("sex_id", 0)) if user.get("sex_id", "").isdigit() else None

                users.append(user)
            return users
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return []
    except csv.Error as e:
        print(f"CSV parsing error: {e}")
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
        print(colored(f"Error adding location {user_data.get('location')}: {e}", RED))

def add_users_to_db(users):
    added_users = 0
    for user_data in tqdm(users, desc="Adding test users to DB"):
        try:
            user = CustomUser(
                username=user_data["username"],
                email=user_data["email"],
                sex_id=user_data["sex_id"],
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
            print(colored(f"Error adding user {user_data.get('username')}: {e}", RED))
    return added_users

def load_users():
    users = load_users_from_csv(CSV_FILE)
    added_users = 0
    print(f"{len(users)} users to add")
    if users:
        added_users = add_users_to_db(users)
    else:
        print("No users to add.")
    print(colored(f"Job is done. Number of added users: {added_users}", GREEN))

def remove_users():
    users = load_users_from_csv(CSV_FILE)
    deleted_users = 0
    for user_data in tqdm(users, desc="Removing test users from DB"):
        try:
            user = CustomUser.objects.get(email=user_data["email"])
            user.delete()
            if not CustomUser.objects.filter(email=user_data["email"]).exists():
                deleted_users += 1
        except Exception as e:
            print(colored(f"Error deleting user {user_data.get('username')}: {e}", RED))
    print(colored(f"Job is done. Number of deleted users: {deleted_users}", GREEN))
