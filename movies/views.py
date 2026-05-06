from django.shortcuts import render, redirect ,get_object_or_404
from django.db.models import Count,Q
from .models import Movie,Theater,Seat,Booking, Genre
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.paginator import Paginator

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

def theater_list(request,movie_id):
    movie = get_object_or_404(Movie,id=movie_id)
    theater=Theater.objects.filter(movie=movie)
    return render(request,'movies/theater_list.html',{'movie':movie,'theaters':theater})

def home(request):
    # 1. Capture multiple filters from the URL
    query = request.GET.get('search')
    selected_genres = request.GET.getlist('genre') # This gets the LIST of checked boxes
    
    print(f"DEBUG: Search: {query} | Genres: {selected_genres}")

    # 2. Start with all movies and optimize with prefetch_related
    # This prevents 5,000 separate database calls for genre names (N+1 problem)
    movies = Movie.objects.all().prefetch_related('genres').order_by('id')

    # 3. Apply Search (if any)
    if query:
        movies = movies.filter(name__icontains=query)

    # 4. Apply Multi-select Genre Filter (if any)
    if selected_genres:
        # .distinct() prevents the same movie from appearing twice if it has multiple genres
        movies = movies.filter(genres__name__in=selected_genres).distinct()

    # --- NEW PAGINATION LOGIC ---
    paginator = Paginator(movies, 12) # Show 12 movies per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # -----------------------------
    
    # 5. Requirement: Dynamic Filter Counts
    # Calculates movie counts for the sidebar based on the CURRENT filtered list
    genre_counts = Genre.objects.annotate(
        num_movies=Count('movies', filter=Q(movies__in=movies))
    )

    # 6. Limit results to 24 for faster page loading
    movies_list = movies[:24]

    context = {
        # 'movies': movies_list,
        'page_obj': page_obj,
        'genre_counts': genre_counts,
        'selected_genres': selected_genres,
    }
    return render(request, 'home.html', context)
@login_required(login_url='/login/')
def book_seats(request,theater_id):
    theaters=get_object_or_404(Theater,id=theater_id)
    seats=Seat.objects.filter(theater=theaters)
    if request.method=='POST':
        selected_Seats= request.POST.getlist('seats')
        error_seats=[]
        if not selected_Seats:
            return render(request,"movies/seat_selection.html",{'theater':theaters,"seats":seats,'error':"No seat selected"})
        for seat_id in selected_Seats:
            seat=get_object_or_404(Seat,id=seat_id,theater=theaters)
            if seat.is_booked:
                error_seats.append(seat.seat_number)
                continue
            try:
                Booking.objects.create(
                    user=request.user,
                    seat=seat,
                    movie=theaters.movie,
                    theater=theaters
                )
                seat.is_booked=True
                seat.save()
            except IntegrityError:
                error_seats.append(seat.seat_number)
        if error_seats:
            error_message=f"The following seats are already booked:{','.join(error_seats)}"
            return render(request,'movies/seat_selection.html',{'theater':theaters,"seats":seats,'error':"No seat selected"})
        return redirect('profile')
    return render(request,'movies/seat_selection.html',{'theaters':theaters,"seats":seats})




