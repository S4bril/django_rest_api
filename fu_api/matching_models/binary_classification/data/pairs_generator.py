from itertools import combinations
import json
import pandas as pd


class PairsGenerator():
    def __init__(self, path_to_users="users.json", path_to_passions="fu_api\json_forms\passions.json"):
        self.users_df = self._load_users(path_to_users)
        self.passions_df = self._load_passions(path_to_passions)

    def generate_pairs(self):
        passion_map = {p['id']: p['name'] for p in self.passions}

        self.users_df['passion_names'] = self.users_df['passions'].apply(
            lambda ids: [passion_map[i] for i in ids if i in passion_map]
        )

        return list(combinations(self.users_df.to_dict('records'), 2))

    def _load_users(self, path):
        with open(path, "r") as file:
            self.users_df = pd.DataFrame(json.load(file))

    def _load_passions(self, path):
        with open(path, "r") as file:
            self.passions = json.load(file)
            self.passions_df = pd.DataFrame(self.passions)

if __name__ == "__main__":
    generator = PairsGenerator()