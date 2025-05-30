from abc import ABC, abstractmethod

from django.db.models import Q

from fu_api.models.custom_user_model import CustomUser
from fu_api.models.like_model import Like


class BaseMatcher(ABC):
    def get_valid_candidates(self, user, number_of_users):
        exclusion_query = (
            Q(id=user.id)
            | Q(friends=user)
            | Q(rejected_users=user)
            | Q(blocked_users=user)
            | Q(
                id__in=Like.objects.filter(sender=user).values_list(
                    "receiver_id", flat=True
                )
            )
        )

        return CustomUser.objects.exclude(exclusion_query)[:number_of_users]

    @abstractmethod
    def compute_feature_vector(self, user, candidate):
        pass

    @abstractmethod
    def get_matches(self, user):
        pass
