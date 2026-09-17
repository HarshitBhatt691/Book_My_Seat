from django.urls import path
from . import views
from . import admin_views

urlpatterns=[
    
    path('',views.movie_list,name='movie_list'),
    path('<int:movie_id>/theaters',views.theater_list,name='theater_list'),
    path('theater/<int:theater_id>/seats/book/',views.book_seats,name='book_seats'),
    
    # Task 4: Payment endpoints
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
    
    # Task 6: Admin Analytics Dashboard
    path('analytics/', admin_views.analytics_dashboard, name='analytics_dashboard'),
]
