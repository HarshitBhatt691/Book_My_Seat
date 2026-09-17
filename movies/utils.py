import logging
import time
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

def send_html_email(subject, template_name, context, recipient_list, max_retries=3, delay=2):
    """
    Renders an HTML email template and sends it.
    Includes an automatic retry mechanism with exponential backoff if the SMTP server fails.
    Designed to be run via a background task queue like Django-Q.
    """
    current_attempt = 0
    current_delay = delay
    html_content = render_to_string(template_name, context)

    while current_attempt < max_retries:
        try:
            current_attempt += 1
            email = EmailMessage(
                subject=subject,
                body=html_content,
                to=recipient_list
            )
            email.content_subtype = "html"
            email.send()
            
            # If successful, log it and break the loop
            logger.info(f"SUCCESS: Confirmation email successfully sent to {recipient_list} on attempt {current_attempt}")
            return 
            
        except Exception as e:
            logger.warning(f"WARNING: Email delivery attempt {current_attempt} failed for {recipient_list}. Error: {str(e)}")
            
            if current_attempt < max_retries:
                logger.info(f"Retrying email delivery in {current_delay} seconds...")
                time.sleep(current_delay)
                current_delay *= 2  # Exponential backoff (2s -> 4s -> 8s)
            else:
                # Final ultimate failure log for monitoring
                logger.error(f"CRITICAL FAILURE: Email delivery completely failed to {recipient_list} after {max_retries} attempts.")

def release_expired_seats(checkout_session_id):
    from .models import Booking
    from django.db import transaction
    
    with transaction.atomic():
        bookings = Booking.objects.select_for_update().filter(stripe_checkout_id=checkout_session_id, payment_status='PENDING')
        if bookings.exists():
            for booking in bookings:
                booking.seat.is_booked = False
                booking.seat.save()
            bookings.update(payment_status='FAILED')
            logger.info(f'Released expired seats for checkout session {checkout_session_id}')
