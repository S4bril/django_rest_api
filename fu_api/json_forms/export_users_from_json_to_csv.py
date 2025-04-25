import json
import csv
import random

with open("users.json", "r", encoding="utf-8") as json_file:
    users = json.load(json_file)

random.shuffle(users)

with open("users.csv", "w", encoding="utf-8", newline="") as csv_file:
    writer = csv.writer(csv_file)

    writer.writerow([
        "username", "password", "email", "sex_id", "birthday",
        "bio", "passions", "location"
    ])

    for user in users:
        writer.writerow([
            user.get("username", ""),
            user.get("password", ""),
            user.get("email", ""),
            user.get("sex_id", ""),
            user.get("birthday", ""),
            user.get("bio", ""),
            ";".join(map(str, user.get("passions", []))),
            ",".join(map(str, user.get("location", [])))
        ])
