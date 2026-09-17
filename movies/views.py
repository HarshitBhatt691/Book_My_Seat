from django.shortcuts import render, redirect ,get_object_or_404
from django.db.models import Count,Q
from .models import Movie,Theater,Seat,Booking, Genre, Language
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.paginator import Paginator
from django_q.tasks import async_task
import uuid
import time 

def index(request):
    # This will now work even if the table is empty
    movies = Movie.objects.all()
    return render(request, 'index.html', {'movies': movies})

def movie_list(request):
    search_query=request.GET.get('search')
    if search_query:
        movies=Movie.objects.filter(name__icontains=search_query)
    else:
        movies=Movie.objects.all()
    return render(request,'movies/movie_list.html',{'movies':movies})

def theater_list(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    theater = Theater.objects.filter(movie=movie)
    
    # TEMPORARY TEST BLOCK: If this fake movie has no theater, just grab the first theater in your database
    if not theater.exists():
        theater = Theater.objects.all()[:1] 
        
    return render(request, 'movies/theater_list.html', {'movie': movie, 'theaters': theater})

def home(request):
    # 1. Capture multiple filters from the URL
    query = request.GET.get('search')
    selected_genres = request.GET.getlist('genre')
    selected_languages = request.GET.getlist('language')
    sort_by = request.GET.get('sort', 'id') # Default sort

    print(f"DEBUG: Search: {query} | Genres: {selected_genres} | Languages: {selected_languages} | Sort: {sort_by}")

    # 2. Start with all movies and optimize with prefetch_related for both genres and languages
    movies = Movie.objects.all().prefetch_related('genres', 'languages')

    # 3. Apply Search (if any)
    if query:
        # Optimized for scalability: __istartswith can utilize standard DB indexes, 
        # whereas __icontains does a full table scan.
        movies = movies.filter(name__istartswith=query)

    # 4. Apply Multi-select Filters
    if selected_genres:
        movies = movies.filter(genres__name__in=selected_genres).distinct()
        
    if selected_languages:
        movies = movies.filter(languages__name__in=selected_languages).distinct()

    # 5. Apply Dynamic Sorting
    # Provide a safe mapping to prevent SQL injection or invalid sorts
    sort_mapping = {
        'id': 'id',
        'rating_desc': '-rating',
        'rating_asc': 'rating',
        'date_desc': '-release_date',
        'date_asc': 'release_date'
    }
    order_field = sort_mapping.get(sort_by, 'id')
    movies = movies.order_by(order_field)

    # 6. Requirement: Dynamic Filter Counts
    genre_counts = Genre.objects.annotate(
        num_movies=Count('movies', filter=Q(movies__in=movies))
    )
    language_counts = Language.objects.annotate(
        num_movies=Count('movies', filter=Q(movies__in=movies))
    )

    # --- PAGINATION LOGIC ---
    paginator = Paginator(movies, 12) # Show 12 movies per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'genre_counts': genre_counts,
        'language_counts': language_counts,
        'selected_genres': selected_genres,
        'selected_languages': selected_languages,
        'sort_by': sort_by,
    }
    return render(request, 'home.html', context)
import stripe
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required(login_url='/login/')
def book_seats(request, theater_id):
    from django.db import transaction
    theaters = get_object_or_404(Theater, id=theater_id)
    seats = Seat.objects.filter(theater=theaters)
    
    if request.method == 'POST':
        selected_Seats = request.POST.getlist('seats')
        
        if not selected_Seats:
            return render(request, "movies/seat_selection.html", {'theaters': theaters, "seats": seats, 'error': "No seat selected"})
        
        # 1. Verify availability BEFORE creating anything using Concurrency-Safe locks
        seats_to_book = []
        try:
            with transaction.atomic():
                # select_for_update() locks the rows until transaction is committed/rolled back
                locked_seats = Seat.objects.select_for_update().filter(id__in=selected_Seats, theater=theaters)
                
                if len(locked_seats) != len(selected_Seats):
                    return render(request, 'movies/seat_selection.html', {'theaters': theaters, "seats": seats, 'error': "Invalid seat selection."})
                
                for seat in locked_seats:
                    if seat.is_booked:
                        return render(request, 'movies/seat_selection.html', {'theaters': theaters, "seats": seats, 'error': f"Seat {seat.seat_number} is already booked or pending payment."})
                    seats_to_book.append(seat)
                
                # 3. Soft-lock seats immediately within the transaction
                for seat in seats_to_book:
                    seat.is_booked = True
                    seat.save()
                    
                booking_reference = str(uuid.uuid4())[:8].upper()
                
                # 2. Create Stripe Checkout Session (inside transaction is generally fine if fast, but to be safer, do it outside? It's fine here)
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': f"{theaters.movie.name} Ticket(s) at {theaters.name}",
                            },
                            'unit_amount': 1500, # $15.00 per ticket
                        },
                        'quantity': len(seats_to_book),
                    }],
                    mode='payment',
                    success_url=request.build_absolute_uri(reverse('payment_success')),
                    cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
                    client_reference_id=booking_reference, 
                    expires_at=int(time.time()) + 1800, # expires in 30 mins minimum by Stripe, but we can have our own scheduler
                )

                # Create PENDING bookings
                for seat in seats_to_book:
                    Booking.objects.create(
                        user=request.user,
                        seat=seat,
                        movie=theaters.movie,
                        theater=theaters,
                        stripe_checkout_id=checkout_session.id,
                        payment_status='PENDING'
                    )
                    
                # Schedule auto-timeout release for these bookings after 2 minutes
                from django_q.tasks import schedule
                from django.utils import timezone
                import datetime
                schedule(
                    'movies.utils.release_expired_seats',
                    checkout_session.id,
                    schedule_type='O',  # Once
                    next_run=timezone.now() + datetime.timedelta(minutes=2)
                )

        except Exception as e:
            return render(request, 'movies/seat_selection.html', {'theaters': theaters, "seats": seats, 'error': str(e)})

        return redirect(checkout_session.url)
        
    return render(request, 'movies/seat_selection.html', {'theaters': theaters, "seats": seats})

def payment_success(request):
    return render(request, 'movies/payment_success.html')

def payment_cancel(request):
    return render(request, 'movies/payment_cancel.html')

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        checkout_id = session.get('id')
        booking_ref = session.get('client_reference_id')

        # Idempotency: Get bookings for this session
        bookings = Booking.objects.filter(stripe_checkout_id=checkout_id)
        if bookings.exists():
            first_booking = bookings.first()
            if first_booking.payment_status != 'PAID':
                # Mark as PAID
                bookings.update(payment_status='PAID')

                # Prepare context and trigger email
                booked_seat_numbers = [b.seat.seat_number for b in bookings]
                theater = first_booking.theater
                
                email_context = {
                    'user': first_booking.user,
                    'movie': theater.movie,
                    'theater': theater,
                    'show_time': theater.time,
                    'seat_numbers': ", ".join(booked_seat_numbers),
                    'booking_id': booking_ref
                }
                
                async_task(
                    'movies.utils.send_html_email',
                    subject=f"Booking Confirmed: {theater.movie.name}",
                    template_name="emails/ticket_confirmation.html",
                    context=email_context,
                    recipient_list=[first_booking.user.email]
                )

    elif event['type'] in ['checkout.session.expired', 'checkout.session.async_payment_failed']:
        session = event['data']['object']
        checkout_id = session.get('id')
        
        # Handle failures and timeouts gracefully
        bookings = Booking.objects.filter(stripe_checkout_id=checkout_id, payment_status='PENDING')
        if bookings.exists():
            # Release the soft-locked seats
            for booking in bookings:
                booking.seat.is_booked = False
                booking.seat.save()
            # Mark bookings as failed
            bookings.update(payment_status='FAILED')

    return HttpResponse(status=200)




