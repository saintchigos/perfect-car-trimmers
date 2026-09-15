from django.urls import path

from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.home, name='home'),
    path('gallery/', views.gallery, name='gallery'),
    path('book/', views.book, name='book'),
    path('booking/<int:pk>/confirmation/', views.confirmation, name='confirmation'),
    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/booking/<int:pk>/update-status/', views.update_booking_status, name='update_booking_status'),
    path('staff/gallery/', views.staff_gallery, name='staff_gallery'),
    path('staff/gallery/<int:pk>/delete/', views.staff_gallery_delete, name='staff_gallery_delete'),
]
