from rest_framework import serializers

from guide.models import Guide, GuideVideo

__all__ = ("GuideSerializer", "GuideVideoSerializer")


class GuideVideoSerializer(serializers.ModelSerializer):
    video = serializers.SerializerMethodField()

    class Meta:
        model = GuideVideo
        fields = ("id", "video", "subtitles", "order", "section")

    def get_video(self, obj):
        if not obj.video:
            return None
        request = self.context.get("request")
        url = obj.video.url
        return request.build_absolute_uri(url) if request else url


class GuideSerializer(serializers.ModelSerializer):
    """Лёгкий сериализатор для списка гидов (выбор перед туром)."""
    video = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Guide
        fields = ("id", "name", "video", "thumbnail", "is_sign_language")

    def get_video(self, obj):
        """Первое видео гида (превью)."""
        first = obj.videos.order_by("order").first()
        if not first or not first.video:
            return None
        request = self.context.get("request")
        url = first.video.url
        return request.build_absolute_uri(url) if request else url

    def get_thumbnail(self, obj):
        if not obj.thumbnail:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.thumbnail.url) if request else obj.thumbnail.url
