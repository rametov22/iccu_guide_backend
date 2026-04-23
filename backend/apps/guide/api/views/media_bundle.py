from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from exhibit.models import Hall
from guide.models import Guide, GuideVideo

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
                        "title": ex.title,
                        "description": ex.description,
                        "video": self._file_url(ex.video),
                        "audio": self._file_url(ex.audio),
                        "images": [self._file_url(img.image) for img in ex.images.all()],
                    })

                guide_videos_data = [
                    {
                        "id": gv.id,
                        "guide_id": gv.guide_id,
                        "video": self._file_url(gv.video),
                        "subtitles": gv.subtitles,
                        "order": gv.order,
                    }
                    for gv in sec.guide_videos.all().order_by("order")
                ]

                sections_data.append({
                    "id": sec.id,
                    "name": sec.name,
                    "description": sec.description,
                    "duration_seconds": sec.duration_seconds,
                    "break_duration_seconds": sec.break_duration_seconds,
                    "transition_seconds": sec.transition_seconds,
                    "video": self._file_url(sec.video),
                    "map_image": self._file_url(sec.map_image),
                    "exhibits": exhibits_data,
                    "guide_videos": guide_videos_data,
                })

            halls_data.append({
                "id": hall.id,
                "name": hall.name,
                "description": hall.description,
                "transition_seconds": hall.transition_seconds,
                "map_image": self._file_url(hall.map_image),
                "transition_map_image": self._file_url(hall.transition_map_image),
                "sections": sections_data,
            })

        guides_data = [
            {
                "id": g.id,
                "name": g.name,
                "thumbnail": self._file_url(g.thumbnail),
                "preview_video": self._file_url(g.preview_video),
                "is_sign_language": g.is_sign_language,
            }
            for g in Guide.objects.filter(is_active=True).order_by("order", "name")
        ]

        return Response({
            "halls": halls_data,
            "guides": guides_data,
        })
