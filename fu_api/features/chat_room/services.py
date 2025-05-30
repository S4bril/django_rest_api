from rest_framework.exceptions import ValidationError

from fu_api.models.chat_room_model import ChatRoom
from fu_api.models.custom_user_model import CustomUser


class ChatRoomService:
    @staticmethod
    def create_chat(creator, name, is_group, member_ids):
        ChatRoomService._ensure_private_chat_constraints(creator, is_group, member_ids)

        chat_room = ChatRoom.objects.create(name=name, is_group=is_group)
        members = CustomUser.objects.filter(id__in=member_ids)
        chat_room.members.add(creator, *members)

        if is_group:
            chat_room.admins.add(creator)

        return chat_room

    @staticmethod
    def add_member(chat_room, request_user, target_user):
        ChatRoomService._ensure_admin(chat_room, request_user)
        ChatRoomService._ensure_reqest_and_target_unique(request_user, target_user)
        ChatRoomService._ensure_not_already_member(chat_room, target_user)

        chat_room.members.add(target_user)

    @staticmethod
    def remove_member(chat_room, request_user, target_user):
        ChatRoomService._ensure_admin(chat_room, request_user)
        ChatRoomService._ensure_member_exists(chat_room, target_user)

        chat_room.members.remove(target_user)

    @staticmethod
    def promote_member(chat_room, request_user, target_user):
        ChatRoomService._ensure_admin(chat_room, request_user)
        ChatRoomService._ensure_member_exists(chat_room, target_user)
        ChatRoomService._ensure_not_already_admin(chat_room, target_user)

        chat_room.admins.add(target_user)

    @staticmethod
    def leave_chat(chat_room, user):
        chat_room.members.remove(user)
        chat_room.admins.remove(user)

        if chat_room.members.count() == 0:
            chat_room.delete()

        elif chat_room.admins.count() == 0:
            new_admin = chat_room.members.first()
            chat_room.admins.add(new_admin)

    @staticmethod
    def _ensure_admin(chat_room, user):
        if not chat_room.admins.filter(id=user.id).exists():
            raise ValidationError(
                {"error_msg": "Tylko administrator może wykonać tę operację."}
            )

    @staticmethod
    def _ensure_reqest_and_target_unique(request_user, target):
        if request_user == target:
            raise ValidationError({"error_msg": "Nie możesz dodać siebie do czatu."})

    @staticmethod
    def _ensure_not_already_member(chat_room, user):
        if chat_room.members.filter(id=user.id).exists():
            raise ValidationError(
                {"error_msg": f"{user.username} już jest członkiem czatu."}
            )

    @staticmethod
    def _ensure_not_already_admin(chat_room, user):
        if chat_room.admins.filter(id=user.id).exists():
            raise ValidationError(
                {"error_msg": f"{user.username} już jest administratorem."}
            )

    @staticmethod
    def _ensure_member_exists(chat_room, user):
        if not chat_room.members.filter(id=user.id).exists():
            raise ValidationError(
                {"error_msg": f"{user.username} nie należy do tego czatu."}
            )

    @staticmethod
    def _ensure_private_chat_constraints(creator, is_group, member_ids):
        if not is_group:
            if len(member_ids) != 1:
                raise ValidationError(
                    {
                        "error_msg": "Do czatu prywatnego trzeba dodać dokładnie jednego użytkownika."
                    }
                )
            if creator.id in member_ids:
                raise ValidationError(
                    {"error_msg": "Nie możesz utworzyć czatu prywatnego z samym sobą."}
                )
