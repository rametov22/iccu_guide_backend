from rest_framework import serializers

from guide.models import Background

__all__ = ("BackgroundSerializer",)


class BackgroundSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Background
        fields = ("id", "image", "order")

    def get_image(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url) if request else obj.image.url
