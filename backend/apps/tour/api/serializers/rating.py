from rest_framework import serializers

from tour.models import TourRating, TouristSession

__all__ = ("TourRatingCreateSerializer",)


class TourRatingCreateSerializer(serializers.ModelSerializer):
    device_token = serializers.UUIDField(write_only=True)

    class Meta:
        model = TourRating
        fields = ("device_token", "rating", "comment")

    def validate(self, attrs):
        device_token = attrs.pop("device_token")
        try:
            tourist = TouristSession.objects.get(device_token=device_token)
        except TouristSession.DoesNotExist:
            raise serializers.ValidationError({"device_token": "Токен не найден"})

        if hasattr(tourist, "rating"):
            raise serializers.ValidationError({"device_token": "Оценка уже оставлена"})

        attrs["tourist_session"] = tourist
        return attrs

    def create(self, validated_data):
        return TourRating.objects.create(**validated_data)
