from django.contrib import admin
import os
from django import forms
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline

from ..models import Guide, GuideVideo, GuideHallVideo

__all__ = ("GuideAdmin", "GuideHallVideoAdmin")


class ServerVideoMixin:
    """
    Добавляет поле выбора видео с сервера к любой форме.
    """

    def add_server_video_field(self):
        # Относительный путь в папке media
        video_rel_path = "exhibits/videos/"
        video_full_path = os.path.join(settings.MEDIA_ROOT, video_rel_path)

        choices = [("", "--- " + str(_("Загрузить локально")) + " ---")]

        if os.path.exists(video_full_path):
            # Получаем список файлов и сортируем для удобства
            files = sorted(
                [
                    f
                    for f in os.listdir(video_full_path)
                    if os.path.isfile(os.path.join(video_full_path, f))
                ]
            )
            for f in files:
                choices.append((f"{video_rel_path}{f}", f))

        self.fields["server_video"] = forms.ChoiceField(
            choices=choices,
            required=False,
            label=_("Использовать видео с сервера"),
            help_text=_(
                "Если выбрано, файл загруженный с компьютера будет проигнорирован."
            ),
        )

    def handle_server_video(self, instance):
        server_video = self.cleaned_data.get("server_video")
        if server_video:
            # Записываем путь в основное поле модели
            instance.video = server_video
        return instance


class GuideVideoForm(forms.ModelForm, ServerVideoMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_server_video_field()

    def save(self, commit=True):
        instance = super().save(commit=False)
        self.handle_server_video(instance)
        if commit:
            instance.save()
        return instance


class GuideHallVideoForm(forms.ModelForm, ServerVideoMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_server_video_field()

    def save(self, commit=True):
        instance = super().save(commit=False)
        self.handle_server_video(instance)
        if commit:
            instance.save()
        return instance


######


class GuideVideoInline(TranslationTabularInline):
    model = GuideVideo
    form = GuideVideoForm
    extra = 1
    ordering = ("section", "order")
    autocomplete_fields = ("section",)


class GuideHallVideoInline(TranslationTabularInline):
    model = GuideHallVideo
    form = GuideHallVideoForm
    extra = 1
    autocomplete_fields = ("hall",)


@admin.register(Guide)
class GuideAdmin(TabbedTranslationAdmin):
    list_display = (
        "id",
        "name",
        "avatar_thumb",
        "is_sign_language",
        "order",
        "is_active",
    )
    list_display_links = ("id", "name")
    list_editable = ("is_sign_language", "order", "is_active")
    list_filter = ("is_active", "is_sign_language")
    search_fields = ("name",)
    ordering = ("order",)
    inlines = [GuideVideoInline, GuideHallVideoInline]

    @admin.display(description="Фото")
    def avatar_thumb(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="max-height:50px;border-radius:50%">',
                obj.thumbnail.url,
            )
        return "—"


@admin.register(GuideHallVideo)
class GuideHallVideoAdmin(TabbedTranslationAdmin):
    list_display = ("guide", "hall", "has_video")
    list_filter = ("guide", "hall")
    autocomplete_fields = ("guide", "hall")

    @admin.display(description="Видео", boolean=True)
    def has_video(self, obj):
        return bool(obj.video)
