import json
import pandas as pd

class PairsGenerator():
    def __init__(self, path_to_users="users.json", path_to_passions="fu_api\json_forms\passions.json"):
        self.path_to_users = path_to_users
        self.path_to_passions = path_to_passions

    def _load_users(self):
        with open(self.path, "r") as file:
            self.users = json.load(file)

    def _load_passions(self):
        with open(self.path, "r") as file:
            self.users = json.load(file)

    def _generate_pairs(self):
        pass

    def _classify_matches(self):
        pass