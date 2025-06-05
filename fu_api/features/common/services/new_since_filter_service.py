from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from django.core.exceptions import ValidationError


class NewSinceFilterService:
    PAGE_SIZE = 20

    @staticmethod
    def filter(request, queryset, date_field="created_at"):
        last_check_str = request.query_params.get("last_check")
        before_str = request.query_params.get("before")

        if last_check_str and before_str:
            raise ValidationError("Nie możesz użyć 'last_check_str' i 'before_str' jednocześnie.")

        if last_check_str:
            dt = NewSinceFilterService._parse_datetime_or_raise(last_check_str)
            return queryset.filter(**{f"{date_field}__gt": dt}).order_by(date_field)[:NewSinceFilterService.PAGE_SIZE]

        if before_str:
            dt = NewSinceFilterService._parse_datetime_or_raise(before_str)
            return queryset.filter(**{f"{date_field}__lt": dt}).order_by(f"-{date_field}")[:NewSinceFilterService.PAGE_SIZE]

        return queryset.order_by(f"-{date_field}")[:NewSinceFilterService.PAGE_SIZE]

    @staticmethod
    def _parse_datetime_or_raise(value):
        dt = parse_datetime(value)
        if dt is None:
            raise ValidationError("Nieprawidłowy format daty. Użyj formatu ISO 8601.")
        if dt.tzinfo is None:
            dt = make_aware(dt)
        return dt
