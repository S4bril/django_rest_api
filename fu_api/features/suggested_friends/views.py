from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from fu_api.features.common.serializers.friend_serializers import FriendSerializer
from fu_api.features.suggested_friends.services import get_suggested_friends

class UserSuggestedFriendsRetrieveView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        suggested_friends = get_suggested_friends(request.user)
        serialized_suggested_friends = FriendSerializer(suggested_friends, many=True)
        return Response({"suggested_friends": serialized_suggested_friends.data}, status=HTTP_200_OK)
