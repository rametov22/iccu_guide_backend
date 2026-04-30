"""
Сборка manifest'а — списка всех медиа-файлов в системе для скачивания на iPad.

Каждый файл идентифицируется тройкой (kind, ref_id, lang) и абсолютным URL.
Если URL изменился (файл заменили в админке) — фронт по этому ключу видит
расхождение с локальным состоянием и перекачивает.

Переводимые поля (video/audio у Exhibit, GuideVideo, GuideHallVideo, Guide)
выдаются как 3 отдельные записи — по одной на язык (ru/en/uz). iPad качает
все три, потому что туристы переключают язык на лету.
"""

from collections import Counter

from exhibit.models import Hall
from guide.models import Guide, GuideHallVideo, GuideVideo

__all__ = ("build_manifest",)

LANGUAGES = ("ru", "en", "uz")


def _abs(request, url):
    if not url:
        return None
    return request.build_absolute_uri(url) if request else url


def _file_meta(request, field):
    if not field:
        return None
    try:
        size = field.size
    except (FileNotFoundError, ValueError):
        size = 0
    return {"url": _abs(request, field.url), "size": size}


def _entry(kind, ref_id, file_meta, lang=""):
    if not file_meta or not file_meta.get("url"):
        return None
    return {
        "kind": kind,
        "ref_id": ref_id,
        "lang": lang,
        "url": file_meta["url"],
        "size": file_meta["size"],
    }


def _emit_translatable(files, kind, ref_id, instance, base_field, request):
    """Эмитит до 3 записей — по одной на каждый язык переводимого FileField."""
    for lang in LANGUAGES:
        field = getattr(instance, f"{base_field}_{lang}", None)
        meta = _file_meta(request, field)
        entry = _entry(kind, ref_id, meta, lang=lang)
        if entry:
            files.append(entry)


def _emit_single(files, kind, ref_id, instance, base_field, request):
    """Эмитит одну запись для непереводимого FileField."""
    field = getattr(instance, base_field, None)
    meta = _file_meta(request, field)
    entry = _entry(kind, ref_id, meta, lang="")
    if entry:
        files.append(entry)


def build_manifest(request=None):
    """
    Возвращает:
      {
        "total": <int>,
        "by_kind": {<kind>: <int>, ...},
        "files": [
          {"kind": "...", "ref_id": <int>, "lang": "ru"|"en"|"uz"|"",
           "url": "...", "size": <int>}
        ]
      }

    Манифест дедуплицируется по URL: каждый уникальный URL возвращается
    ровно один раз. Если один и тот же файл «всплывает» в нескольких kind
    (например, Section.video и GuideVideo.video указывают на один путь),
    остаётся первое встреченное вхождение.

    kind:
      hall_map / hall_transition_map           — карты залов (без языка)
      section_map                              — карта раздела (без языка)
      section_video                            — видео раздела (без языка)
      section_immersion                        — фото иммерсивной комнаты (без языка)
      exhibit_video / exhibit_audio            — медиа экспоната (3 языка)
      exhibit_image                            — фото экспоната (без языка)
      guide_thumb                              — превью-картинка гида
      guide_preview / guide_exhibits           — глобальные видео гида (3 языка)
      guide_video / guide_transition_video     — видео раздела от гида (3 языка)
      guide_hall_video                         — видео перехода в зал (3 языка)
    """
    raw = []

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
        _emit_single(raw, "hall_map", hall.id, hall, "map_image", request)
        _emit_single(raw, "hall_transition_map", hall.id, hall, "transition_map_image", request)

        for sec in hall.sections.filter(is_active=True).order_by("order"):
            _emit_single(raw, "section_map", sec.id, sec, "map_image", request)
            _emit_single(raw, "section_video", sec.id, sec, "video", request)
            _emit_single(raw, "section_immersion", sec.id, sec, "immersion_photo", request)

            for ex in sec.exhibits.filter(is_active=True).order_by("order"):
                _emit_translatable(raw, "exhibit_video", ex.id, ex, "video", request)
                _emit_translatable(raw, "exhibit_audio", ex.id, ex, "audio", request)
                for img in ex.images.all():
                    _emit_single(raw, "exhibit_image", img.id, img, "image", request)

            for gv in sec.guide_videos.all():
                _emit_translatable(raw, "guide_video", gv.id, gv, "video", request)
                _emit_translatable(raw, "guide_transition_video", gv.id, gv, "transition_video", request)

    for ghv in GuideHallVideo.objects.all().select_related("guide", "hall"):
        _emit_translatable(raw, "guide_hall_video", ghv.id, ghv, "video", request)

    for g in Guide.objects.filter(is_active=True).order_by("order", "name"):
        _emit_single(raw, "guide_thumb", g.id, g, "thumbnail", request)
        _emit_translatable(raw, "guide_preview", g.id, g, "preview_video", request)
        _emit_translatable(raw, "guide_exhibits", g.id, g, "exhibits_video", request)

    seen = set()
    files = []
    for entry in raw:
        url = entry["url"]
        if url in seen:
            continue
        seen.add(url)
        files.append(entry)

    by_kind = Counter(f["kind"] for f in files)

    return {
        "total": len(files),
        "by_kind": dict(by_kind),
        "files": files,
    }
