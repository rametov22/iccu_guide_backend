from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from exhibit.models import Hall
from guide.models import Guide, GuideVideo, GuideHallVideo

__all__ = ("MediaBundleView",)


class MediaBundleView(APIView):
    """
    GET /api/v1/guide/media-bundle/

    Возвращает всё медиа тура одним запросом — для предзагрузки на iPad
    перед оффлайн-режимом. Структура: halls -> sections -> exhibits + guides.

    Язык берётся из URL-префикса (/ru/, /en/, /uz/).
    """

    permission_classes = [permissions.AllowAny]

    def _abs(self, url):
        if not url:
            return None
        request = self.request
        return request.build_absolute_uri(url) if request else url

    def _file_url(self, field):
        if not field:
            return None
        return self._abs(field.url)

    def get(self, request):
        halls_qs = (
            Hall.objects.filter(is_active=True)
            .order_by("order")
            .prefetch_related(
                "sections",
                "sections__exhibits",
                "sections__exhibits__images",
                "sections__guide_videos",
            )
        )

        halls_data = []
        for hall in halls_qs:
            sections_data = []
            for sec in hall.sections.filter(is_active=True).order_by("order"):
                exhibits_data = []
                for ex in sec.exhibits.filter(is_active=True).order_by("order"):
                    exhibits_data.append({
                        "id": ex.id,
                        "name": ex.title,
                        "video": self._file_url(ex.video),
                        "audio": self._file_url(ex.audio),
                        "images": [self._file_url(img.image) for img in ex.images.all()],
                    })

                guide_videos_data = [
                    {
                        "id": gv.id,
                        "guide_id": gv.guide_id,
                        "video": self._file_url(gv.video),
                        "transition_video": self._file_url(gv.transition_video),
                    }
                    for gv in sec.guide_videos.all().order_by("order")
                ]

                sections_data.append({
                    "id": sec.id,
                    "name": sec.name,
                    "video": self._file_url(sec.video),
                    "map_image": self._file_url(sec.map_image),
                    "exhibits": exhibits_data,
                    "guide_videos": guide_videos_data,
                })

            # Видео гидов для перехода в этот зал
            hall_guide_videos = [
                {
                    "id": ghv.id,
                    "guide_id": ghv.guide_id,
                    "video": self._file_url(ghv.video),
                }
                for ghv in GuideHallVideo.objects.filter(hall=hall)
            ]

            halls_data.append({
                "id": hall.id,
                "name": hall.name,
                "map_image": self._file_url(hall.map_image),
                "transition_map_image": self._file_url(hall.transition_map_image),
                "guide_videos": hall_guide_videos,
                "sections": sections_data,
            })

        guides_data = [
            {
                "id": g.id,
                "name": g.name,
                "thumbnail": self._file_url(g.thumbnail),
                "preview_video": self._file_url(g.preview_video),
                "exhibits_video": self._file_url(g.exhibits_video),
            }
            for g in Guide.objects.filter(is_active=True).order_by("order", "name")
        ]

        return Response({
            "halls": halls_data,
            "guides": guides_data,
        })
