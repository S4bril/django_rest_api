from rest_framework.exceptions import ValidationError

from fu_api.models.private_chat_room_model import PrivateChatRoom


class PrivateChatRoomService:
    @staticmethod
    def create_private_chat(creator, member):
        PrivateChatRoomService._ensure_private_chat_not_exists(creator, member)
        PrivateChatRoomService._ensure_unique(creator, member)

        chat_room = PrivateChatRoom.objects.create()
        chat_room.members.add(creator, member)

        return chat_room

    @staticmethod
    def _ensure_private_chat_not_exists(creator, member):
        if (
            PrivateChatRoom.objects.filter(members=creator)
            .filter(members=member)
            .exists()
        ):
            raise ValidationError(
                {"error_msg": f"Już istnieje chat z {member.username}"}
            )

    @staticmethod
    def _ensure_unique(creator, member):
        if creator == member:
            raise ValidationError(
                {"error_msg": f"Nie możesz utworzyć chatu z samym sobą."}
            )
