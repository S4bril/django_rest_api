from fu_api.features.user_profile.serializers import UserSerializer


def create_test_user(username, **kwargs):
    defaults = {
        "email": f"{username}@example.com",
        "password": "password",
        "sex_id": 0,
        "birthday": "2000-01-01",
        "bio": "I love writing unit tests.",
        "passions_ids": [1, 2, 3, 4],
        "bio_embedding": [0.0],
    }
    defaults.update(kwargs)

    data = {"username": username, **defaults}
    serializer = UserSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.save()
