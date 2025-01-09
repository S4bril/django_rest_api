# API Endpoints

| **HTTP Method** | **Endpoint**                     | **Description**                       | **Authentication** | **Request Body Params**                                                                    |
| --------------- | -------------------------------- | ------------------------------------- | ------------------ | ------------------------------------------------------------------------------------------ |
| **GET**         | `/login/`                        | Log in user.                          | Yes                | `{"username", "password"}`                                                                 |
| **GET**         | `/token/refresh/`                | Refresh jwt token.                    | No                 | `{"refresh"}`                                                                              |
| **GET**         | `/logout/`                       | Logout user.                          | Yes                | None                                                                                       |
| **POST**        | `/user/`                         | Create a new user.                    | No                 | `{ "username", "email", "password", "sex", "birthday", "bio", "profile_image": "base64" }` |
| **GET**         | `/user/get-profile/`             | Retrieve logged in user's profile     | Yes                | None                                                                                       |
| **PUT**         | `/user/`                         | Update user details.                  | Yes                | `{ "email", "bio", ... }`                                                                  |
| **DELETE**      | `/user/`                         | Delete a user.                        | Yes                | None                                                                                       |
| **GET**         | `/user/friends/`                 | List user's friends                   | Yes                | None                                                                                       |
| **DELETE**      | `/user/friends/<id>/`            | Remove a friend.                      | Yes                | `{ "friend_id": <int> }`                                                                   |
| **DELETE**      | `/user/friends/add-friend/<id>/` | Add a friend.                         | Yes                | None                                                                                       |
| **PUT**         | `/user/location/`                | Update user's location.               | Yes                | `{"latitude": float, "longitude": float}`                                                  |
| **GET**         | `/user/get_location/`            | Get user's location.                  | Yes                | None                                                                                       |
| **POST**        | `/events/`                       | Create a new event.                   | Yes                | `{ "title", "description", "latitude", "longitude": float, ... }`                          |
| **GET**         | `/events/`                       | List all events.                      | Yes                | `?search=<query>` (optional)                                                               |
| **GET**         | `/events/<id>/`                  | Retrieve details of a specific event. | Yes                | None                                                                                       |
| **PUT**         | `/events/<id>/`                  | Update event details.                 | Yes                | `{ "title": "string", "description": "string", ... }`                                      |
| **DELETE**      | `/events/<id>/`                  | Delete an event.                      | Yes                | None                                                                                       |
