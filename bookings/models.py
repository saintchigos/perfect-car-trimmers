from django.db import models
from django.urls import reverse

from .validators import validate_image_upload


class SiteContent(models.Model):
    """Singleton row holding all the text/images an admin should be able to
    edit from the front-end business side without touching code — hero copy,
    the about blurb, and the Google rating badge shown on the homepage.
    There is only ever one row (pk=1); see SiteContent.load()."""

    # Hero section
    hero_heading = models.CharField(
        max_length=120, default="Sagging Roof Lining?",
        help_text="Main hero line (kept short — this is the big bold text).",
    )
    hero_heading_accent = models.CharField(
        max_length=60, default="Fixed Today.",
        help_text="Second part of the hero line, shown in the accent colour.",
    )
    hero_subheading = models.TextField(
        default=(
            "Trusted headliner & car roof lining repair in Midrand — book your "
            "slot online in under a minute, or message us on WhatsApp for an "
            "instant quote."
        ),
    )
    hero_banner_image = models.ImageField(
        upload_to='site_content/', blank=True, null=True,
        validators=[validate_image_upload],
        help_text="Optional wide photo behind the hero section. If left blank, recent gallery photos are used instead.",
    )

    # Trust / motivation badge (Google rating)
    show_google_rating = models.BooleanField(
        default=True, help_text="Show the Google rating badge on the homepage.",
    )
    google_rating = models.DecimalField(
        max_digits=2, decimal_places=1, default=4.9,
        help_text="e.g. 4.9 — update this to match your current Google Business rating.",
    )
    google_review_count = models.PositiveIntegerField(
        default=0, help_text="Number of Google reviews behind the rating.",
    )
    google_review_url = models.URLField(
        blank=True, help_text="Optional: link straight to your Google reviews.",
    )

    # About section
    about_heading = models.CharField(max_length=120, default="Why Midrand Trusts Us")
    about_text = models.TextField(
        default=(
            "Years of hands-on craftsmanship, honest quotes, and a shop that "
            "actually picks up the phone. From sagging headliners to full "
            "interior refreshes, we treat every car like it's our own."
        ),
    )
    about_image = models.ImageField(upload_to='site_content/', blank=True, null=True, validators=[validate_image_upload])

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Content"
        verbose_name_plural = "Site Content"

    def __str__(self):
        return "Homepage content"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # singleton — never actually delete the one row

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class FabricOption(models.Model):
    """Upsell options from the proposal's 'Fabric & Style Customizer'."""
    name = models.CharField(max_length=100)  # e.g. Standard OEM, Blackout, Alcantara
    description = models.TextField(blank=True)
    extra_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    swatch_image = models.ImageField(upload_to='fabric_swatches/', blank=True, null=True, validators=[validate_image_upload])
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['extra_cost']

    def __str__(self):
        return self.name


class TimeSlot(models.Model):
    """A single bookable drop-off slot on a given day."""

    class SlotType(models.TextChoices):
        MORNING = 'MORNING', 'Morning Drop-off'
        EXPRESS = 'EXPRESS', 'Same-Day 3-Hour Express'
        AFTERNOON = 'AFTERNOON', 'Afternoon Drop-off'

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_type = models.CharField(max_length=20, choices=SlotType.choices, default=SlotType.MORNING)
    capacity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ('date', 'start_time', 'slot_type')

    def __str__(self):
        return f"{self.date} {self.start_time.strftime('%H:%M')} - {self.get_slot_type_display()}"

    @property
    def bookings_count(self):
        return self.booking_set.exclude(status=Booking.Status.CANCELLED).count()

    @property
    def is_full(self):
        return self.bookings_count >= self.capacity


class GalleryItem(models.Model):
    """Showcase images — before/after pair, or a single completed-work photo."""
    vehicle_type = models.CharField(max_length=100, blank=True)  # e.g. Sedan, SUV, Luxury
    caption = models.CharField(max_length=200, blank=True)
    before_image = models.ImageField(upload_to='gallery/before/', blank=True, null=True, validators=[validate_image_upload])
    after_image = models.ImageField(upload_to='gallery/after/', validators=[validate_image_upload])
    fabric_option = models.ForeignKey(FabricOption, on_delete=models.SET_NULL, null=True, blank=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-featured', '-created_at']

    def __str__(self):
        return f"{self.vehicle_type or 'Completed work'} - {self.caption or 'Untitled'}"


class Booking(models.Model):
    """A customer's booked repair slot — the core object of the proposal."""

    class ServiceMode(models.TextChoices):
        DROP_OFF = 'DROP_OFF', 'Bring vehicle to shop'
        PICK_UP = 'PICK_UP', 'Request pick-up'
        ON_SITE = 'ON_SITE', 'On-site / mobile repair'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending confirmation'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    # Customer details
    customer_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)

    # Vehicle details
    vehicle_make = models.CharField(max_length=100)
    vehicle_model = models.CharField(max_length=100, blank=True)
    damage_photo = models.ImageField(upload_to='damage_photos/', blank=True, null=True, validators=[validate_image_upload])
    damage_description = models.TextField(blank=True)

    # Booking specifics
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.PROTECT)
    fabric_option = models.ForeignKey(FabricOption, on_delete=models.SET_NULL, null=True, blank=True)
    service_mode = models.CharField(max_length=20, choices=ServiceMode.choices, default=ServiceMode.DROP_OFF)
    location_notes = models.CharField(
        max_length=255, blank=True,
        help_text="Address/area for pick-up or on-site requests (e.g. suburb in Midrand)."
    )

    # Deposit (optional upfront payment, per proposal)
    deposit_required = models.BooleanField(default=False)
    deposit_paid = models.BooleanField(default=False)
    proof_of_payment = models.ImageField(
        upload_to='proof_of_payment/', blank=True, null=True,
        validators=[validate_image_upload],
        help_text="Screenshot of an EFT/bank transfer, if the customer paid a deposit that way.",
    )

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer_name} - {self.timeslot} ({self.get_status_display()})"

    def get_absolute_url(self):
        return reverse('bookings:confirmation', args=[self.pk])

    @property
    def whatsapp_message(self):
        """Pre-populated message for the '1-Click WhatsApp Direct' feature."""
        lines = [
            "Hi, I've just booked a repair slot.",
            f"Name: {self.customer_name}",
            f"Vehicle: {self.vehicle_make} {self.vehicle_model}".strip(),
            f"Slot: {self.timeslot}",
        ]
        if self.fabric_option:
            lines.append(f"Fabric option: {self.fabric_option.name}")
        if self.damage_description:
            lines.append(f"Details: {self.damage_description}")
        return "\n".join(lines)
