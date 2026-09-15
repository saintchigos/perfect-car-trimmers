from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand

from bookings.models import GalleryItem

SEED_DIR = Path(__file__).resolve().parent.parent.parent / 'seed_assets' / 'gallery'


class Command(BaseCommand):
    help = "Loads the client-supplied completed-work photos into the gallery."

    def handle(self, *args, **options):
        if not SEED_DIR.exists():
            self.stdout.write(self.style.ERROR(f"No seed images found at {SEED_DIR}"))
            return

        if GalleryItem.objects.exists():
            self.stdout.write(self.style.WARNING(
                "Gallery already has items — skipping to avoid duplicates. "
                "Delete existing GalleryItem rows first if you want to reload."
            ))
            return

        photos = sorted(SEED_DIR.glob('*.jpg'))
        created = 0
        for i, photo_path in enumerate(photos):
            with open(photo_path, 'rb') as f:
                item = GalleryItem(
                    caption="Completed roof lining repair",
                    featured=(i < 4),
                )
                item.after_image.save(photo_path.name, File(f), save=True)
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Loaded {created} gallery photos ({min(created, 4)} featured on homepage)."))
