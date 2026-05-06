# BookMyShow Clone

A Django-based cinema ticket booking system inspired by BookMyShow. Browse movies, select theaters, choose seats, and book tickets.

## Features

### 🎬 Movie Browsing
- Browse all available movies with descriptions
- View movie details and ratings
- See all theaters screening each movie

### 🎭 Theater & Show Management
- Multiple theaters with different capacities
- Multiple show timings per day
- Check seat availability in real-time

### 💺 Interactive Seat Selection
- Visual seat layout with color-coded availability
- Real-time seat status (available, booked, selected)
- Multi-seat selection with instant price calculation
- View seat pricing tiers if applicable

### 👤 User Authentication
- User registration with email validation
- Secure login/logout
- Password reset functionality
- Profile management and booking history

### 📋 Booking System
- Complete booking workflow
- View past and upcoming bookings
- Booking confirmation and details
- User dashboard with all reservations

### ✅ Admin Dashboard
- Manage movies, theaters, and shows
- Monitor all bookings
- Update seat availability
- User management

## Tech Stack

- **Backend**: Django 4.x
- **Database**: SQLite
- **Frontend**: HTML, CSS (Django Templates)
- **Python**: 3.x

## How It Works

### Architecture
```
User Interface (HTML Templates)
         ↓
Django Views (URLs → Views)
         ↓
Models & Database (SQLite)
         ↓
Admin Panel & User Authentication
```

### Database Models
- **User**: Extended Django user with booking history
- **Movie**: Movie details (title, genre, duration, poster)
- **Theater**: Cinema hall information (name, location, capacity)
- **Show**: Movie screenings (theater, time, date)
- **Seat**: Individual seats with availability status
- **Booking**: User reservations with payment info

### User Journey
1. **Browse** → View all movies on the home page
2. **Select** → Choose a movie to see available theaters
3. **Pick Theater** → Select a theater and show time
4. **Choose Seats** → Click seats to reserve (visual feedback updates instantly)
5. **Confirm** → Login/register and finalize booking
6. **Receive** → Booking confirmation with ticket details
7. **Manage** → View all bookings in user profile

## Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/django-bookmyshow-clone.git
   cd django-bookmyshow-clone
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Load sample data (optional)**
   ```bash
   python seed_movies.py
   ```

7. **Create a superuser (optional, for admin panel)**
   ```bash
   python manage.py createsuperuser
   ```

## Running the Application

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

## Project Structure

```
.
├── bookmyseat/        # Main Django project settings
├── movies/            # Movie and theater management
├── users/             # User authentication and profiles
├── templates/         # HTML templates
├── media/             # Uploaded files (movies, images)
├── manage.py          # Django management script
├── requirements.txt   # Project dependencies
└── db.sqlite3         # SQLite database
```

## Usage

1. **Home Page**: View all available movies
2. **Select Movie**: Click on a movie to see available theaters
3. **Choose Theater**: Pick a theater and show time
4. **Select Seats**: Choose your seats and confirm booking
5. **Login**: Create an account or log in to complete booking

## Admin Panel

Access the admin panel at `/admin` with superuser credentials to manage:
- **Movies**: Add, edit, delete movies with descriptions and posters
- **Theaters**: Create theater locations and define seating capacity
- **Shows**: Schedule movie screenings at different times
- **Seats**: Manage seat availability and pricing
- **Bookings**: View and manage user reservations
- **Users**: Manage user accounts and permissions

## Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'django'`
- **Solution**: Make sure virtual environment is activated and run `pip install -r requirements.txt`

**Issue**: Database errors after first run
- **Solution**: Run `python manage.py migrate` to apply all migrations

**Issue**: Media files not showing up
- **Solution**: Ensure media folder exists and `MEDIA_ROOT` is correctly set in settings.py

**Issue**: Static files not loading
- **Solution**: Run `python manage.py collectstatic` for production

## Future Enhancements

- Payment gateway integration
- Email notifications
- Advanced filtering and search
- Reviews and ratings
- Multiple seat price categories

## Contributing

Feel free to fork this project and submit pull requests for improvements!

## License

This project is open source and available under the MIT License.

## Author

Built as a learning project to understand:
- Django MVT (Model-View-Template) architecture
- User authentication and authorization
- Database modeling for real-world scenarios
- Form handling and validation
- Django admin customization

Feel free to reach out with questions or suggestions!

---

**Star ⭐ this repo if you found it helpful!**
