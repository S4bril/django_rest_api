from django.db.models import Case, IntegerField, Q, When

from fu_api.models.match_model import Match


def get_ids_of_people_matched_with_user(user):
    matched_user_ids = (
        Match.objects.filter(Q(user1=user) | Q(user2=user))
        .annotate(
            other_user=Case(
                When(user1=user, then="user2"),
                When(user2=user, then="user1"),
                output_field=IntegerField(),
            )
        )
        .values_list("other_user", flat=True)
    )

    return matched_user_ids
