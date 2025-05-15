import csv
from django.core.management.base import BaseCommand
from dictionary.models import Dictionary

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        filepath = 'dictionary\management\commands\seed_data.csv' 

        # Xóa tất cả bản ghi cũ trong bảng Dictionary
        Dictionary.objects.all().delete()
        self.stdout.write(self.style.WARNING("Deleted all old Dictionary records."))

        with open(filepath, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count_created = 0

            for row in reader:
                gloss = row['gloss']
                videosrc = row['video_link']
                subset = row.get('subset', 'train')

                Dictionary.objects.create(
                    gloss=gloss,
                    videosrc=videosrc,
                    subset=subset
                )
                count_created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seed completed: {count_created} records created."
        ))
