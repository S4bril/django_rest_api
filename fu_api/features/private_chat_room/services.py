from rest_framework.exceptions import ValidationError

from fu_api.models.match_model import Match
from fu_api.models.private_chat_room_model import PrivateChatRoom


class PrivateChatRoomService:
    @staticmethod
    def create_private_chat(creator, member):
        user_1, user_2 = (
            (creator, member) if creator.id <= member.id else (member, creator)
        )
        PrivateChatRoomService._ensure_private_chat_not_exists(creator, member)
        PrivateChatRoomService._ensure_are_matched(user_1, user_2)
        PrivateChatRoomService._ensure_unique(creator, member)

        Match.objects.filter(user1=user_1, user2=user_2).delete()
        chat_room = PrivateChatRoom.objects.create()
        chat_room.members.add(creator, member)

        return chat_room

    @staticmethod
    def _ensure_are_matched(user_1, user_2):
        if not Match.objects.filter(user1=user_1, user2=user_2).exists():
            raise ValidationError(
                {"error_msg": f"Możesz utworzyć chat tylko ze swoim matchem."}
            )

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
