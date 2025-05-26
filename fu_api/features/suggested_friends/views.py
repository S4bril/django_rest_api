from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, ListAPIView
from fu_api.features.common.serializers.friend_serializers import FriendSerializer
from fu_api.features.suggested_friends.matchers.factory import MatcherFactory
from fu_api.features.suggested_friends.matchers.feature_engineer import FeatureEngineer
from fu_api.features.suggested_friends.serializers import LikeSerializer, MatchSerializer, FriendSerializer
from fu_api.models.custom_user_model import CustomUser
from fu_api.models.like_model import Like
from fu_api.models.match_model import Match
from .services import LikeService


class UserSuggestedFriendsRetrieveView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        method = request.query_params.get("method", "knn")
        try:
            matcher = MatcherFactory.get_matcher(method=method)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        suggested_friends = matcher.get_matches(request.user)
        return Response({"suggested_friends": suggested_friends}, status=status.HTTP_200_OK)


class UserLikeListCreateView(ListCreateAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Like.objects.filter(receiver=self.request.user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sender = request.user
        receiver = serializer.validated_data['receiver']

        try:
            result = LikeService.create_like(sender=sender, receiver=receiver)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if 'match' in result:
            return Response({'detail': 'Match created!'}, status=status.HTTP_201_CREATED)
        else:
            return Response(LikeSerializer(result['like'], context=self.get_serializer_context()).data,
                            status=status.HTTP_201_CREATED)


class MatchesListView(ListAPIView):
    serializer_class = MatchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Match.objects.filter(Q(first_user=user) | Q(second_user=user)).order_by('-created_at')


class NearYouListView(ListAPIView):
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user

        if user.location.latitude is None or user.location.longitude is None:
            return CustomUser.objects.none()

        feature_engineer = FeatureEngineer()

        candidates = CustomUser.objects.exclude(id=user.id)

        users_with_distance = [
            (candidate, feature_engineer.compute_distance(user, candidate))
            for candidate in candidates
            if candidate.location.latitude is not None and candidate.location.longitude is not None
        ]

        closest_users = sorted(users_with_distance, key=lambda x: x[1])[:10]

        return [user for user, _ in closest_users]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["current_user"] = self.request.user
        return context


class UserRejectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        rejected_user = get_object_or_404(CustomUser, pk=pk)

        if request.user == rejected_user:
            return Response({"error": "You cannot reject yourself."}, status=status.HTTP_400_BAD_REQUEST)

        request.user.rejected_users.add(rejected_user)
        return Response({"message": f"{rejected_user.username} added to rejected users"}, status=status.HTTP_200_OK)
