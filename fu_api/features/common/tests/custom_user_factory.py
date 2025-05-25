from fu_api.models.custom_user_model import CustomUser

def create_test_user(username, **kwargs):
    defaults = {
        "email": f"{username}@example.com",
        "password": "password",
        "sex_id": 0,
        "birthday": "2002-10-26",
        "bio": "",
        "passions": [1, 2, 3, 4],
        "bio_embedding": [0.0],
    }
    defaults.update(kwargs)
    user = CustomUser.objects.create_user(username=username, **defaults)
    return user
