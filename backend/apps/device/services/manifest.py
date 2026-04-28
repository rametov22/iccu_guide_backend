"""
Сборка manifest'а — списка всех медиа-файлов в системе для скачивания на iPad.

Каждый файл идентифицируется парой (kind, ref_id) и его абсолютным URL.
Если URL изменился (файл заменили в админке) — фронт по этому ключу видит
расхождение с локальным состоянием и перекачивает.
"""

from exhibit.models import Hall
from guide.models import Guide, GuideHallVideo, GuideVideo

__all__ = ("build_manifest",)


def _abs(request, url):
    if not url:
        return None
    return request.build_absolute_uri(url) if request else url


def _file(request, field):
    if not field:
        return None
    try:
        size = field.size
    except (FileNotFoundError, ValueError):
        size = 0
    return {"url": _abs(request, field.url), "size": size}


def _entry(kind, ref_id, file_obj):
    if not file_obj or not file_obj.get("url"):
        return None
    return {
        "kind": kind,
        "ref_id": ref_id,
        "url": file_obj["url"],
        "size": file_obj["size"],
    }


def build_manifest(request=None):
    """
    Возвращает {"files": [...]} — плоский список файлов с типом и id.

    kind:
      hall_map / hall_transition_map  — карты залов
      section_map / section_video      — карта и видео раздела
      exhibit_video / exhibit_audio / exhibit_image  — медиа экспоната
      guide_thumb / guide_preview / guide_exhibits   — медиа гида
      guide_video / guide_transition_video           — видео раздела (на гида)
      guide_hall_video                               — видео перехода в зал
    """
    files = []

    halls = (
        Hall.objects.filter(is_active=True)
        .order_by("order")
        .prefetch_related(
            "sections",
            "sections__exhibits",
            "sections__exhibits__images",
            "sections__guide_videos",
        )
    )

    for hall in halls:
        files.append(_entry("hall_map", hall.id, _file(request, hall.map_image)))
        files.append(
            _entry(
                "hall_transition_map", hall.id, _file(request, hall.transition_map_image)
            )
        )

        for sec in hall.sections.filter(is_active=True).order_by("order"):
            files.append(_entry("section_map", sec.id, _file(request, sec.map_image)))
            files.append(_entry("section_video", sec.id, _file(request, sec.video)))

            for ex in sec.exhibits.filter(is_active=True).order_by("order"):
                files.append(_entry("exhibit_video", ex.id, _file(request, ex.video)))
                files.append(_entry("exhibit_audio", ex.id, _file(request, ex.audio)))
                for img in ex.images.all():
                    files.append(
                        _entry("exhibit_image", img.id, _file(request, img.image))
                    )

            for gv in sec.guide_videos.all():
                files.append(_entry("guide_video", gv.id, _file(request, gv.video)))
                files.append(
                    _entry(
                        "guide_transition_video",
                        gv.id,
                        _file(request, gv.transition_video),
                    )
                )

    for ghv in GuideHallVideo.objects.all().select_related("guide", "hall"):
        files.append(_entry("guide_hall_video", ghv.id, _file(request, ghv.video)))

    for g in Guide.objects.filter(is_active=True).order_by("order", "name"):
        files.append(_entry("guide_thumb", g.id, _file(request, g.thumbnail)))
        files.append(_entry("guide_preview", g.id, _file(request, g.preview_video)))
        files.append(_entry("guide_exhibits", g.id, _file(request, g.exhibits_video)))

    return {"files": [f for f in files if f]}
