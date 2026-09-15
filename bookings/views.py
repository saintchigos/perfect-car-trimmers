from urllib.parse import quote

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages as django_messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import BookingForm, GalleryUploadForm
from .models import Booking, GalleryItem, TimeSlot


def home(request):
    featured_gallery = GalleryItem.objects.filter(featured=True)[:4]
    upcoming_slots = TimeSlot.objects.filter(date__gte=timezone.localdate())[:6]
    context = {
        'featured_gallery': featured_gallery,
        'upcoming_slots': upcoming_slots,
    }
    return render(request, 'bookings/home.html', context)


def gallery(request):
    items = GalleryItem.objects.all()
    return render(request, 'bookings/gallery.html', {'items': items})


def book(request):
    if request.method == 'POST':
        form = BookingForm(request.POST, request.FILES)
        if form.is_valid():
            booking = form.save()
            return redirect('bookings:confirmation', pk=booking.pk)
    else:
        form = BookingForm()
    return render(request, 'bookings/book.html', {'form': form})


def confirmation(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    whatsapp_url = (
        f"https://wa.me/{settings.SHOP_WHATSAPP_NUMBER}"
        f"?text={quote(booking.whatsapp_message)}"
    )
    context = {
        'booking': booking,
        'whatsapp_url': whatsapp_url,
    }
    return render(request, 'bookings/confirmation.html', context)


@staff_member_required
def staff_dashboard(request):
    """Activity view for shop admins/workers — separate from the Django admin,
    built for a quick glance at today's schedule and pending work."""
    today = timezone.localdate()

    status_filter = request.GET.get('status', '')
    bookings = Booking.objects.select_related('timeslot', 'fabric_option')
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    todays_bookings = bookings.filter(timeslot__date=today)
    upcoming_bookings = bookings.filter(timeslot__date__gt=today)[:20]

    context = {
        'today': today,
        'todays_bookings': todays_bookings,
        'upcoming_bookings': upcoming_bookings,
        'stats': {
            'pending': Booking.objects.filter(status=Booking.Status.PENDING).count(),
            'confirmed_today': Booking.objects.filter(
                timeslot__date=today, status=Booking.Status.CONFIRMED
            ).count(),
            'deposit_pending': Booking.objects.filter(
                deposit_required=True, deposit_paid=False
            ).exclude(status=Booking.Status.CANCELLED).count(),
            'total_upcoming': Booking.objects.filter(timeslot__date__gte=today).exclude(
                status=Booking.Status.CANCELLED
            ).count(),
        },
        'status_choices': Booking.Status.choices,
        'status_filter': status_filter,
    }
    return render(request, 'bookings/staff_dashboard.html', context)


@staff_member_required
def update_booking_status(request, pk):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, pk=pk)
        new_status = request.POST.get('status')
        if new_status in Booking.Status.values:
            booking.status = new_status
            if new_status == Booking.Status.CONFIRMED and booking.deposit_required:
                booking.deposit_paid = request.POST.get('deposit_paid') == 'on'
            booking.save()
            django_messages.success(request, f"Updated {booking.customer_name}'s booking to {booking.get_status_display()}.")
    return redirect(request.POST.get('next') or 'bookings:staff_dashboard')


@staff_member_required
def staff_gallery(request):
    """Lets shop staff add/remove before-after work photos without needing
    a full Django admin login — the day-to-day task of keeping the gallery
    current shouldn't require the full admin."""
    if request.method == 'POST':
        form = GalleryUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            django_messages.success(request, "Photo added to the gallery.")
            return redirect('bookings:staff_gallery')
    else:
        form = GalleryUploadForm()

    items = GalleryItem.objects.all()
    return render(request, 'bookings/staff_gallery.html', {'form': form, 'items': items})


@staff_member_required
def staff_gallery_delete(request, pk):
    if request.method == 'POST':
        item = get_object_or_404(GalleryItem, pk=pk)
        item.delete()
        django_messages.success(request, "Photo removed from the gallery.")
    return redirect('bookings:staff_gallery')
