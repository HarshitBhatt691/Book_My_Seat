from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, F, FloatField, ExpressionWrapper, Q
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, ExtractHour
from .models import Booking, Movie, Theater
from django.core.cache import cache
from datetime import timedelta
from django.utils import timezone

@staff_member_required(login_url='/login/')
def analytics_dashboard(request):
    cache_key = 'admin_analytics_dashboard_data'
    context = cache.get(cache_key)

    if not context:
        now = timezone.now()
        TICKET_PRICE = 15
        
        daily_revenue = Booking.objects.filter(payment_status='PAID', booked_at__date=now.date()).count() * TICKET_PRICE
        weekly_revenue = Booking.objects.filter(payment_status='PAID', booked_at__gte=now - timedelta(days=7)).count() * TICKET_PRICE
        monthly_revenue = Booking.objects.filter(payment_status='PAID', booked_at__gte=now - timedelta(days=30)).count() * TICKET_PRICE

        popular_movies = Movie.objects.annotate(
            total_bookings=Count('booking', filter=Q(booking__payment_status='PAID'))
        ).order_by('-total_bookings')[:5]

        busiest_theaters = Theater.objects.annotate(
            total_bookings=Count('booking', filter=Q(booking__payment_status='PAID'))
        ).order_by('-total_bookings')[:5]

        peak_hours = Booking.objects.filter(payment_status='PAID').annotate(
            hour=ExtractHour('booked_at')
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        total_bookings_count = Booking.objects.count()
        failed_bookings_count = Booking.objects.filter(payment_status='FAILED').count()
        cancellation_rate = (failed_bookings_count / total_bookings_count * 100) if total_bookings_count > 0 else 0

        context = {
            'daily_revenue': daily_revenue,
            'weekly_revenue': weekly_revenue,
            'monthly_revenue': monthly_revenue,
            'popular_movies': popular_movies,
            'busiest_theaters': busiest_theaters,
            'peak_hours': peak_hours,
            'cancellation_rate': round(cancellation_rate, 2)
        }
        
        cache.set(cache_key, context, 300)

    return render(request, 'movies/admin_dashboard.html', context)
