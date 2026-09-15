from django import forms
from django.utils import timezone

from .models import Booking, GalleryItem, TimeSlot


class BookingForm(forms.ModelForm):
    # Honeypot: renders as a hidden input (invisible to real visitors), but
    # bots that blindly fill every field in a scraped form will trip it.
    # Cheap, dependency-free spam protection for this public, unauthenticated form.
    website = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Booking
        fields = [
            'customer_name', 'phone_number', 'email',
            'vehicle_make', 'vehicle_model',
            'damage_photo', 'damage_description',
            'timeslot', 'fabric_option', 'service_mode', 'location_notes',
            'deposit_required', 'proof_of_payment',
        ]
        widgets = {
            'damage_description': forms.Textarea(attrs={'rows': 3}),
            'location_notes': forms.TextInput(attrs={
                'placeholder': 'e.g. Noordwyk, Midrand'
            }),
        }

    def clean_website(self):
        value = self.cleaned_data.get('website')
        if value:
            raise forms.ValidationError("Submission rejected.")
        return value

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show upcoming, non-full slots
        available = TimeSlot.objects.filter(date__gte=timezone.localdate())
        self.fields['timeslot'].queryset = available
        self.fields['timeslot'].label_from_instance = lambda s: (
            f"{s.date.strftime('%a %d %b')} · {s.start_time.strftime('%H:%M')}"
            f"–{s.end_time.strftime('%H:%M')} · {s.get_slot_type_display()}"
            f"{' (FULL)' if s.is_full else ''}"
        )
        for name, field in self.fields.items():
            if name not in ('deposit_required',):
                field.widget.attrs.setdefault('class', 'form-control')
        self.fields['deposit_required'].widget.attrs['class'] = 'form-check-input'

    def clean_timeslot(self):
        slot = self.cleaned_data['timeslot']
        if slot.is_full:
            raise forms.ValidationError("That slot is fully booked — please choose another.")
        return slot


class GalleryUploadForm(forms.ModelForm):
    class Meta:
        model = GalleryItem
        fields = ['vehicle_type', 'caption', 'before_image', 'after_image', 'fabric_option', 'featured']
        widgets = {
            'vehicle_type': forms.TextInput(attrs={'placeholder': 'e.g. Sedan, SUV, Luxury'}),
            'caption': forms.TextInput(attrs={'placeholder': 'Optional short caption'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'featured':
                field.widget.attrs.setdefault('class', 'form-control')
        self.fields['featured'].widget.attrs['class'] = 'form-check-input'
        self.fields['featured'].help_text = "Show this photo on the homepage 'Recent Work' section."
