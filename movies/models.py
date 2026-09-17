from django.db import models
from django.contrib.auth.models import User 
from datetime import datetime

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

import re

class Movie(models.Model):
    name= models.CharField(max_length=255, db_index = True)
    image= models.ImageField(upload_to="movies/")
    rating = models.DecimalField(max_digits=3,decimal_places=1)
    cast= models.TextField()
    description= models.TextField(blank=True,null=True) 
    # 2. Add these relationships for Task 1
    genres = models.ManyToManyField(Genre, related_name="movies")
    languages = models.ManyToManyField(Language, related_name="movies")
    
    # 3. Add release_date to handle the 'Sorting' requirement in Task 1
    release_date = models.DateField(auto_now_add=True, db_index=True)
    
    # Task 3: Secure YouTube Trailer Integration
    trailer_url = models.URLField(blank=True, null=True, help_text="YouTube Trailer URL")

    def get_youtube_video_id(self):
        if not self.trailer_url:
            return None
        # Strict regex prevents XSS by only allowing exactly 11 base64url characters
        match = re.search(r'(?:v=|/)([0-9A-Za-z_-]{11})(?:\?|&|/|$)', self.trailer_url)
        if match:
            return match.group(1)
        return None

    def get_youtube_embed_url(self):
        video_id = self.get_youtube_video_id()
        if video_id:
            # Use privacy-enhanced mode to prevent browser blocking and tracker issues
            return f"https://www.youtube-nocookie.com/embed/{video_id}"
        return None

    def get_youtube_thumbnail(self):
        video_id = self.get_youtube_video_id()
        if video_id:
            return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        return None

    def __str__(self):
        return self.name

class Theater(models.Model):
    name = models.CharField(max_length=255)
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE,related_name='theaters')
    time= models.DateTimeField()

    def __str__(self):
        return f'{self.theater_name} - {self.name} at {self.time}'

class Seat(models.Model):
    theater = models.ForeignKey(Theater,on_delete=models.CASCADE,related_name='seats')
    seat_number = models.CharField(max_length=10)
    is_booked=models.BooleanField(default=False)

    def __str__(self):
        return f'{self.seat_number} in {self.theater}'

class Booking(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
    ]

    user=models.ForeignKey(User,on_delete=models.CASCADE)
    seat=models.OneToOneField(Seat,on_delete=models.CASCADE)
    movie=models.ForeignKey(Movie,on_delete=models.CASCADE)
    theater=models.ForeignKey(Theater,on_delete=models.CASCADE)
    booked_at=models.DateTimeField(auto_now_add=True)
    
    # Task 4: Payment Gateway Tracking
    stripe_checkout_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f'Booking by {self.user.username} for {self.seat.seat_number} at {self.theater} ({self.payment_status})'
