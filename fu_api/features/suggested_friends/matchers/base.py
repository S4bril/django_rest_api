from abc import ABC, abstractmethod
from django.db.models import Q
from fu_api.models.custom_user_model import CustomUser


class BaseMatcher(ABC):
    def get_valid_candidates(self, user, number_of_users):
        excluded = Q(id=user.id) | Q(friends=user) | Q(rejected_users=user)
        return CustomUser.objects.exclude(
            id__in=CustomUser.objects.filter(excluded).values_list('id', flat=True)
        )[:number_of_users]

    @abstractmethod
    def compute_feature_vector(self, user, candidate):
        pass

    @abstractmethod
    def get_matches(self, user):
        pass
