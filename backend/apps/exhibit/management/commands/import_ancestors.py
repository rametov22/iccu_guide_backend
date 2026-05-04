import os
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.html import strip_tags  # Для очистки от HTML-тегов

# Замени 'exhibit' на имя твоего приложения
from exhibit.models import Exhibit, ExhibitImage, Section


class Command(BaseCommand):
    help = "Парсит 10 предков, очищает описание от HTML и сохраняет все фото"

    def download_file(self, url):
        if not url:
            return None
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return ContentFile(response.content, name=os.path.basename(url))
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"  - Ошибка загрузки файла {url}: {e}")
            )
        return None

    def handle(self, *args, **options):
        # 1. Секция
        section, _ = Section.objects.get_or_create(name_ru="Фойе")

        list_url = "https://api.lh.neovex.uz/ru/api/v1/virtual/heritage/ancestors/"
        detail_base_url = (
            "https://api.lh.neovex.uz/ru/api/v1/virtual/heritage/biography/{}/detail/"
        )

        self.stdout.write(self.style.SUCCESS("Запуск импорта..."))

        try:
            response = requests.get(list_url)
            ancestors = response.json()[:10]
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка API: {e}"))
            return

        for index, item in enumerate(ancestors, 1):
            ancestor_id = item["id"]
            full_name = item["full_name"]
            self.stdout.write(f"[{index}/10] {full_name}")

            # 2. Детали
            try:
                detail_resp = requests.get(detail_base_url.format(ancestor_id))
                detail_data = detail_resp.json()
            except:
                continue

            # 3. Очистка контента от <div> и других тегов
            raw_content = detail_data.get("content", "")
            # strip_tags уберет <div>, но оставит текст внутри.
            # Если нужно заменить <br> на переносы строк, можно сначала сделать .replace('<br>', '\n')
            clean_description = strip_tags(raw_content.replace("<br>", "\n")).strip()

            # 4. Создание Exhibit
            exhibit, created = Exhibit.objects.update_or_create(
                title=full_name,
                defaults={
                    "section": section,
                    "description": clean_description,
                    "is_active": True,
                    "order": index,
                },
            )

            # 5. Видео
            if item.get("video") and not exhibit.video:
                video_file = self.download_file(item["video"])
                if video_file:
                    exhibit.video.save(video_file.name, video_file, save=True)

            # 6. Обработка изображений (Главное из списка + Галерея из деталей)
            if not exhibit.images.exists():
                # А) Главное фото из первого API
                main_img_url = item.get("image")
                if main_img_url:
                    main_img_file = self.download_file(main_img_url)
                    if main_img_file:
                        ExhibitImage.objects.create(
                            exhibit=exhibit, image=main_img_file, order=0
                        )
                        self.stdout.write(f"  + Главное фото сохранено")

                # Б) Остальные фото из деталей
                images_data = detail_data.get("images", [])
                for idx, img_item in enumerate(
                    images_data, 1
                ):  # Начинаем с 1, т.к. 0 уже занят
                    img_url = img_item.get("image")
                    if img_url:
                        img_file = self.download_file(img_url)
                        if img_file:
                            ExhibitImage.objects.create(
                                exhibit=exhibit, image=img_file, order=idx
                            )
                self.stdout.write(self.style.SUCCESS(f"  + Галерея загружена"))

        self.stdout.write(self.style.SUCCESS("Готово!"))
