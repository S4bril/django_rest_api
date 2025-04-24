from geopy.distance import great_circle
from typing import List
from fu_api.matching_models.binary_classification.user_pair import UserPair
from fu_api.matching_models.binary_classification.user import User


class PairFactory:
    def __init__(self, users: List[User]):
        self.users = users

    def generate_pairs(
        self,
        max_age_diff: int = 5,
        min_common_passions: int = 1,
        max_distance_km: float = 50.0
    ) -> List[UserPair]:
        pairs = []

        for i in range(len(self.users)):
            user_a = self.users[i]
            for j in range(i+1, len(self.users)):
                user_b = self.users[j]

                if abs(user_a.age - user_b.age) > max_age_diff:
                    continue

                common = len(user_a.passions & user_b.passions)
                if common < min_common_passions:
                    continue
                distance = great_circle(
                    user_a.location,
                    user_b.location
                ).kilometers
                if distance > max_distance_km:
                    continue

                pairs.append(UserPair(user_a, user_b))

        return pairs
