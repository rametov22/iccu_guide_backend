from rest_framework import serializers

from ...models import Exhibit

__all__ = ("ExhibitSerializer",)


class ExhibitSerializer(serializers.ModelSerializer):
    video = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Exhibit
        fields = ("id", "title", "description", "video", "thumbnail", "order")

    def _abs(self, url):
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url

    def get_video(self, obj):
        return self._abs(obj.video.url) if obj.video else None

    def get_thumbnail(self, obj):
        return self._abs(obj.thumbnail.url) if obj.thumbnail else None
