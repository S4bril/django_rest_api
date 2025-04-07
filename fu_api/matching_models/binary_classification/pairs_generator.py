from itertools import combinations
import json
import math
import pandas as pd

DEFAULT_USERS_DATASET_FILE_PATH = r"fu_api\matching_models\binary_classification\data\users_dataset.json"
DEFAULT_PASSIONS_FILE_PATH = r"fu_api\json_forms\passions.json"

class PairsGenerator():
    def __init__(self, path_to_users=DEFAULT_USERS_DATASET_FILE_PATH, path_to_passions=DEFAULT_PASSIONS_FILE_PATH):
        self._load_users(path_to_users)
        self._load_passions(path_to_passions)

    def generate_pairs(self):
        passion_map = {pid: p["name"] for pid, p in self.passions.items()}

        self.users_df["passion_names"] = self.users_df["passions"].apply(
            lambda ids: [passion_map[str(i)] for i in ids if str(i) in passion_map]
        )

        self.users_df["sex"] = self.users_df["sex_id"].apply(
            lambda id: "Mężczyzna" if id == "0" else "Kobieta"
        )

        self.users_df = self.users_df.drop(columns=["email", "birthday", "password", "username"])

        pairs = [list(pair) for pair in combinations(self.users_df.to_dict("records"), 2)]

        self._add_euclidean_distance(pairs)

        return pairs

    def _add_euclidean_distance(self, pairs):
        for pair in pairs:
            user1, user2 = pair

            lat1 = float(user1["location"][0])
            lon1 = float(user1["location"][1])
            lat2 = float(user2["location"][0])
            lon2 = float(user2["location"][1])

            # distance = math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
            distance = self._haversine(lat1, lon1, lat2, lon2)
            pair.append({"distance": round(distance, 2)})

    def _haversine(self, lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        R = 6371
        return R * c

    def _load_users(self, path):
        with open(path, "r", encoding="utf-8") as file:
            self.users_df = pd.DataFrame(json.load(file))

    def _load_passions(self, path):
        with open(path, "r", encoding="utf-8") as file:
            self.passions = json.load(file)["passions"]
            passions_list = [{"id": pid, **data} for pid, data in self.passions.items()]
            self.passions_df = pd.DataFrame(passions_list)
