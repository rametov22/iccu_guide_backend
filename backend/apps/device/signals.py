"""
Сигналы: при сохранении любого медиа-объекта (видео гида, экспонат, фото)
шлём push-уведомление всем устройствам через OneSignal.

Push отправляется через transaction.on_commit — чтобы не дёргать API,
если транзакция в итоге будет откачена.
"""

import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from exhibit.models import Exhibit, ExhibitImage
from guide.models import Guide, GuideHallVideo, GuideVideo

from .services import send_push_to_all

log = logging.getLogger(__name__)

PUSH_TITLE = "Новый контент"
PUSH_BODY = "Доступно новое медиа для скачивания"


def _notify():
    log.info("Sending OneSignal media-update push")
    send_push_to_all(
        title=PUSH_TITLE,
        body=PUSH_BODY,
        data={"action": "media_updated"},
    )


def _schedule_push(sender, instance, created, **kwargs):
    transaction.on_commit(_notify)


for model in (Guide, GuideVideo, GuideHallVideo, Exhibit, ExhibitImage):
    post_save.connect(_schedule_push, sender=model, dispatch_uid=f"device_push_{model.__name__}")
