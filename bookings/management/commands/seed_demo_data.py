import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from bookings.models import FabricOption, TimeSlot


class Command(BaseCommand):
    help = "Creates sample fabric options and the next 14 days of time slots."

    def handle(self, *args, **options):
        fabrics = [
            ("Standard OEM Fabric", "Factory-match replacement fabric.", 0),
            ("Blackout Package", "Full black headliner + trim upgrade.", 450),
            ("Alcantara", "Premium suede-style finish.", 950),
            ("Contrast Stitching", "Add-on stitching detail in a contrast colour.", 250),
        ]
        for name, desc, cost in fabrics:
            FabricOption.objects.get_or_create(
                name=name, defaults={"description": desc, "extra_cost": cost}
            )
        self.stdout.write(self.style.SUCCESS(f"Fabric options ready ({len(fabrics)})."))

        today = timezone.localdate()
        created = 0
        slot_templates = [
            (TimeSlot.SlotType.MORNING, datetime.time(8, 0), datetime.time(10, 0)),
            (TimeSlot.SlotType.EXPRESS, datetime.time(10, 30), datetime.time(13, 30)),
            (TimeSlot.SlotType.AFTERNOON, datetime.time(14, 0), datetime.time(16, 0)),
        ]
        for day_offset in range(14):
            day = today + datetime.timedelta(days=day_offset)
            if day.weekday() == 6:  # skip Sundays
                continue
            for slot_type, start, end in slot_templates:
                _, was_created = TimeSlot.objects.get_or_create(
                    date=day, start_time=start, slot_type=slot_type,
                    defaults={"end_time": end, "capacity": 2},
                )
                created += was_created

        self.stdout.write(self.style.SUCCESS(f"Created {created} new time slots."))
