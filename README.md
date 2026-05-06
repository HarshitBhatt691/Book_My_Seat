# BookMyShow Clone

A Django-based cinema ticket booking system inspired by BookMyShow. Browse movies, select theaters, choose seats, and book tickets.

## Features

- 🎬 Browse movies and cinema halls
- 🎭 View available shows for each theater
- 💺 Interactive seat selection with real-time availability
- 👤 User authentication (register, login, logout)
- 📋 Booking history and profile management
- ✅ Responsive UI with Django templates

## Tech Stack

- **Backend**: Django 4.x
- **Database**: SQLite
- **Frontend**: HTML, CSS (Django Templates)
- **Python**: 3.x

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
- Movies
- Theaters
- Shows
- Bookings

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

Your Name - [GitHub Profile](https://github.com/YOUR_USERNAME)
