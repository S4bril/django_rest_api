from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from fu_api.features.common.get_matched_ids import get_ids_of_people_matched_with_user
from fu_api.features.common.serializers.friend_serializer import FriendSerializer
from fu_api.features.suggested_friends.matchers.factory import MatcherFactory
from fu_api.features.suggested_friends.matchers.feature_engineer import FeatureEngineer
from fu_api.features.suggested_friends.serializers import (
    LikeSerializer,
    MatchSerializer,
)
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

        suggested_friends_objects = matcher.get_matches(request.user)

        serializer = FriendSerializer(
            suggested_friends_objects,
            many=True,
            context={"current_user": request.user, "request": request},
        )

        return Response(
            {"suggested_friends": serializer.data}, status=status.HTTP_200_OK
        )


class UserLikeCreateView(CreateAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        sender = request.user
        receiver_id = self.kwargs.get("pk")
        receiver = get_object_or_404(CustomUser, id=receiver_id)

        try:
            result = LikeService.create_like(sender=sender, receiver=receiver)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if "match" in result:
            return Response(
                {"detail": "Match created!"}, status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                LikeSerializer(
                    result["like"], context=self.get_serializer_context()
                ).data,
                status=status.HTTP_201_CREATED,
            )


class RecentLikesListView(ListAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Like.objects.filter(receiver=self.request.user).order_by("-created_at")


class MatchesListView(ListAPIView):
    serializer_class = MatchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Match.objects.filter(Q(user1=user) | Q(user2=user)).order_by(
            "-created_at"
        )


class NearYouListView(ListAPIView):
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.location is None:
            return CustomUser.objects.none()

        liked_by_user = Like.objects.filter(sender=user).values_list("receiver_id", flat=True)
        liked_me = Like.objects.filter(receiver=user).values_list("sender_id", flat=True)
        exclusion_query = (
            Q(id=user.id)
            | Q(rejected_users=user)
            | Q(blocked_users=user)
            | Q(id__in=liked_by_user)
            | Q(id__in=liked_me)
            | Q(id__in=get_ids_of_people_matched_with_user(user))
        )

        feature_engineer = FeatureEngineer()

        candidates = CustomUser.objects.exclude(exclusion_query)

        users_with_distance = [
            (candidate, feature_engineer.compute_distance(user, candidate))
            for candidate in candidates
            if candidate.location is not None
        ]

        closest_users = sorted(users_with_distance, key=lambda x: x[1])

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
            return Response(
                {"error": "You cannot reject yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.rejected_users.add(rejected_user)
        return Response(
            {"message": f"{rejected_user.username} added to rejected users"},
            status=status.HTTP_200_OK,
        )
