from django.contrib import admin
from .models import Movie, Theater, Seat, Booking, Genre, Language

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    # Changed 'movie_name' to 'name' to match your updated models.py
    list_display = ('name', 'rating', 'release_date', 'cast','description')




@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    list_display = ['name', 'movie', 'time']

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['theater', 'seat_number', 'is_booked']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'seat', 'movie','theater','booked_at']



