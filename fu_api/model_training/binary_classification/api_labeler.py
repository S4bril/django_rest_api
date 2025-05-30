import json
import os

import openai

from config import settings
from fu_api.model_training.binary_classification.user_pair import UserPair


class APILabeler:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.prompt_template = """Rate compatibility (0 or 1) for these two profiles:

        User A:
        Bio: {bio_a}
        Passions: {passions_a}
        Age: {age_a}

        User B:
        Bio: {bio_b}
        Passions: {passions_b}
        Age: {age_b}

        Distance between users: {distance} km

        Answer ONLY with 0 (no match) or 1 (good match). 
        Consider shared interests, bio compatibility, age difference, distance separating users and potential connection."""

    def label_with_zero_pair(self, pair: UserPair) -> float:
        if (
            pair.distance >= 100.0
            or abs(pair.user_a.age - pair.user_b.age) >= 10
            or len(pair.user_a.passions_ids & pair.user_b.passions_ids) == 0
        ):
            pair.label = 0.0
            return 0.0
        return None

    def label_pair(self, pair: UserPair) -> float:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": self.prompt_template.format(
                        bio_a=pair.user_a.bio,
                        passions_a=", ".join(
                            self._extract_passions_names(pair.user_a.passions_ids)
                        ),
                        age_a=pair.user_a.age,
                        bio_b=pair.user_b.bio,
                        passions_b=", ".join(
                            self._extract_passions_names(pair.user_b.passions_ids)
                        ),
                        age_b=pair.user_b.age,
                        distance=pair.distance,
                    ),
                }
            ],
            temperature=0.4,
            logit_bias={"0": 20, "1": 20},
            max_tokens=1,
        )
        pair.label = float(response.choices[0].message.content.strip())
        return pair.label

    def _extract_passions_names(self, passions_ids):
        passions_file_path = os.path.join(
            settings.BASE_DIR, "fu_api", "json_forms", "passions.json"
        )
        with open(passions_file_path, "r", encoding="utf-8") as file:
            passions = json.load(file)["passions"]
            return [
                passions.get(str(p_id), {}).get("name", "Unknown")
                for p_id in passions_ids
            ]
