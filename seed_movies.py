import os
import django
import random
from decimal import Decimal

# 1. SETUP: This points to your specific project settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat                            .settings')
django.setup()

from movies.models import Movie, Genre, Language

def seed_database():
    print("--- Starting Seeding Process ---")
    
    # 2. CREATE GENRES AND LANGUAGES
    genre_names = ['Action', 'Sci-Fi', 'Comedy', 'Drama', 'Horror', 'Romance', 'Thriller']
    lang_names = ['English', 'Hindi', 'Spanish', 'French', 'Japanese', 'Telugu', 'Tamil']
    
    genres = [Genre.objects.get_or_create(name=n)[0] for n in genre_names]
    langs = [Language.objects.get_or_create(name=n)[0] for n in lang_names]

    # 3. PREPARE 5,000 MOVIES
    movies_to_create = []
    print("Generating 5,000 movie entries...")
    
    for i in range(1, 5001):
        movie = Movie(
            name=f"Epic Movie {i}",
            rating=Decimal(random.uniform(5.0, 9.9)).quantize(Decimal('0.1')),
            cast="Actor A, Actor B, Actress C",
            description=f"An amazing story about movie number {i}. Experience the thrill!",
            # Note: image field is left empty for now
        )
        movies_to_create.append(movie)

    # 4. BULK INSERT (Saves time!)
    Movie.objects.bulk_create(movies_to_create)
    
    # 5. ASSIGN RELATIONSHIPS
    print("Assigning Genres and Languages...")
    all_movies = Movie.objects.all()
    for movie in all_movies:
        # Give each movie 1-2 random genres and 1 random language
        movie.genres.add(*random.sample(genres, k=random.randint(1, 2)))
        movie.languages.add(random.choice(langs))

    print(f"DONE! Successfully seeded {Movie.objects.count()} movies.")

if __name__ == '__main__':
    seed_database()
