from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils.timezone import now
from datetime import timedelta
from myapp.models import Booking

class Command(BaseCommand):
    help = 'Send reminder emails to users 2 days before event'

    def handle(self, *args, **kwargs):
        target_date = now().date() + timedelta(days=2)
        bookings = Booking.objects.filter(event_date=target_date)

        for booking in bookings:
            message = f"""
            Hi {booking.name},

            Just a reminder that your event at {booking.venue.for_booking} is coming up in 2 days!

            📍 Venue: {booking.venue.for_booking}
            📍 Location: {booking.venue.location}
            👥 Facilitator: {booking.venue.facilitator}
            📅 Date: {booking.event_date}
            👥 Attendees: {booking.attendees}

            We’re excited to host you!

            Best,
            Event Team
            
            """
            send_mail(
                subject='Upcoming Event Reminder',
                message=message,
                from_email='noreply@example.com',
                recipient_list=[booking.email],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f'Reminder sent to {booking.email}'))
