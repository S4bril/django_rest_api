from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from rest_framework import status
from rest_framework.response import Response


class NewSinceFilterService:
    @staticmethod
    def filter(request, queryset, date_field="created_at"):
        last_check_str = request.query_params.get("last_check")

        if last_check_str:
            dt = parse_datetime(last_check_str)

            if dt is None:
                return NewSinceFilterService._build_result(
                    None,
                    False,
                    Response(
                        {
                            "error": "Invalid datetime format for 'last_check'. Use ISO 8601."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    ),
                )

            if dt.tzinfo is None:
                dt = make_aware(dt)

            filtered_qs = queryset.filter(**{f"{date_field}__gt": dt})
            return NewSinceFilterService._build_result(
                filtered_qs, filtered_qs.exists()
            )

        return NewSinceFilterService._build_result(queryset, True)

    @staticmethod
    def _build_result(queryset, has_new, error=None):
        return {
            "queryset": queryset,
            "has_new": has_new,
            "error": error,
        }
