# API Endpoints

| **HTTP Method** | **Endpoint**                           | **Description**                       | **Authentication** | **Request Body Params**                                                                                                                                    |
| --------------- | -------------------------------------- | ------------------------------------- | ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **GET**         | `/login/`                              | Log in user.                          | Yes                | `{"username": string, "password": string}`                                                                                                                 |
| **GET**         | `/token/refresh/`                      | Refresh jwt token.                    | Yes                | `{"refresh": string}`                                                                                                                                      |
| **GET**         | `/logout/`                             | Logout user.                          | Yes                | None                                                                                                                                                       |
| **POST**        | `/users/`                              | Create a new user.                    | No                 | `{ "username": "string", "email": "string", "password": "string", "sex": "string", "birthday": "YYYY-MM-DD", "bio": "string", "profile_image": "base64" }` |
| **GET**         | `/users/<id>/`                         | Retrieve a specific user by ID.       | Yes                | None                                                                                                                                                       |
| **PUT**         | `/users/<id>/`                         | Update user details.                  | Yes                | `{ "email": "string", "bio": "string", ... }`                                                                                                              |
| **DELETE**      | `/users/<id>/`                         | Delete a user.                        | Yes                | None                                                                                                                                                       |
| **GET**         | `/users/<id>/friends/`                 | List user's friends                   | Yes                | None                                                                                                                                                       |
| **DELETE**      | `/users/<id>/friends/<id>/`            | Remove a friend.                      | Yes                | `{ "friend_id": <integer> }`                                                                                                                               |
| **DELETE**      | `/users/<id>/friends/add-friend/<id>/` | Add a friend.                         | Yes                | None                                                                                                                                                       |
| **PUT**         | `/users/<id>/location/`                | Update user's location.               | Yes                | `{"latitude": float, "longitude": float}`                                                                                                                  |
| **GET**         | `/users/<id>/get_location/`            | Get user's location.                  | Yes                | None                                                                                                                                                       |
| **POST**        | `/events/`                             | Create a new event.                   | Yes                | `{ "title": "string", "description": "string", "latitude": float, "longitude": float, ... }`                                                               |
| **GET**         | `/events/`                             | List all events.                      | Yes                | `?search=<query>` (optional)                                                                                                                               |
| **GET**         | `/events/<id>/`                        | Retrieve details of a specific event. | Yes                | None                                                                                                                                                       |
| **PUT**         | `/events/<id>/`                        | Update event details.                 | Yes                | `{ "title": "string", "description": "string", ... }`                                                                                                      |
| **DELETE**      | `/events/<id>/`                        | Delete an event.                      | Yes                | None                                                                                                                                                       |

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    profile_image = Base64ImageField(required=False)
    # image_url = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'sex', 'birthday', 'bio', 'password', 'profile_image']
        read_only_fields = ['id', 'account_creation_date']
        
    # def create(self, validated_data):
    #     password = validated_data.pop('password')
    #     user = CustomUser(**validated_data)
    #     user.set_password(password)
    #     user.save()
    #     return user

    # def update(self, instance, validated_data):
    #     if 'password' in validated_data:
    #         instance.set_password(validated_data.pop('password', None))

    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)

    #     instance.save()

    #     return instance
    
    # def get_image_url(self, obj):
    #     if obj.profile_image:
    #         return self.context['request'].build_absolute_uri(obj.profile_image.url)
    #     return None
    