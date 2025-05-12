from django.http import HttpResponse
from .models import *
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render,redirect
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.utils.timezone import localtime
from django.contrib.auth.models import User
from django.contrib import messages 
from django.utils.dateparse import parse_date
import textwrap
import string
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from itertools import chain
from django.contrib.auth.decorators import login_required,user_passes_test
from textblob import TextBlob 
from django.utils import timezone
from django.utils.timezone import now
from django.db.models import Q
# from .utils import analyze_sentiment

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model

def Home_view(request):
    caterings = CateringOption.objects.all()
    return render(request, 'home.html', {'caterings': caterings})


def About_view(request):
    data = About.objects.all()
    return render(request, 'about.html', {'about_info': data})


def Contact_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        message = request.POST.get('message')

        # Save to database
        Contact.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile=mobile,
            message=message
        )
        messages.success(request, "Your message has been submitted successfully!")
        return redirect('home')
    
    return render(request, 'contactus.html')

def Search(request):
    venue_type = request.GET.get('venue_type')
    location = request.GET.get('location')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    attendees = request.GET.get('attendees')
    date_str = request.GET.get('event_date')
    catering = request.GET.get('catering')

    filtered_venues = Venue.objects.all()
    filters_applied = False

    if location:
        filtered_venues = filtered_venues.filter(location__icontains=location)
        filters_applied = True
    if venue_type:
        filtered_venues = filtered_venues.filter(venue_type=venue_type)
        filters_applied = True
    if min_price:
        filtered_venues = filtered_venues.filter(price__gte=min_price)
        filters_applied = True
    if max_price:
        filtered_venues = filtered_venues.filter(price__lte=max_price)
        filters_applied = True
    if attendees:
        filtered_venues = filtered_venues.filter(capacity__gte=attendees)
        filters_applied = True
    if catering:
        filtered_venues = filtered_venues.filter(catering__id=catering)
        filters_applied = True

    if filters_applied and not filtered_venues.exists():
        messages.info(request, "No results found for the selected filters. Showing all venues matching the location, price, or attendees if available.")
        # Try fallback filtering based on individual non-empty fields
        fallback_venues = Venue.objects.all()
        if location:
            fallback_venues = fallback_venues.filter(location__icontains=location)
        elif min_price:
            fallback_venues = fallback_venues.filter(price__gte=min_price)
        elif max_price:
            fallback_venues = fallback_venues.filter(price__lte=max_price)
        elif attendees:
            fallback_venues = fallback_venues.filter(capacity__gte=attendees)
        else:
            fallback_venues = Venue.objects.all()  # Show all if nothing usable
        return render(request, 'results.html', {'venues': fallback_venues, 'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY})
    # Parse event date
    event_date = parse_date(date_str) if date_str else None

    # Find booked venues on that date
    booked_venue_ids = []
    if event_date:
        bookings_on_date = Booking.objects.filter(event_date=event_date)
        booked_venue_ids = list(bookings_on_date.values_list('venue_id', flat=True))

    # Annotate each venue with a boolean: is_booked
    venues_with_status = []
    for venue in filtered_venues:
        venue.is_booked = venue.id in booked_venue_ids
        venues_with_status.append(venue)

    if not venues_with_status:
        messages.info(request, "No results found for the selected filters.")

    return render(request, 'results.html', {
        'venues': venues_with_status,
        'selected_date': date_str,
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY

    })
    
    
    
    # Logout view


# Booking view
@login_required
def Book_event(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        attendees = request.POST.get('attendees')
        event_date_str = request.POST.get('event_date')
        event_date = parse_date(event_date_str)  # convert string to date
        need_transport = request.POST.get('need_transport') == 'yes'
        transport_type = request.POST.get('transport_type') if need_transport else None

        if Booking.objects.filter(venue=venue, event_date=event_date).exists():
            messages.error(request, "This venue is already booked on that date. Please choose another date.")
            return render(request, "booking.html", {"venue": venue})
        
        booking = Booking.objects.create(
            user=request.user, 
            venue=venue,
            name=name,
            email=email,
            phone=phone,
            attendees=attendees,
            event_date=event_date,
            need_transport=need_transport,
            transport_type=transport_type,
            price=venue.price,
            location=venue.location,
            
        )
        booking.save()
        
        booking_time_ist = localtime(booking.timestamp)
        home_url = request.build_absolute_uri('/')
        email_message = textwrap.dedent(f"""
        Hi {name},

        Thank you for booking with us! Your venue reservation has been successfully confirmed.
        Booking Details:
           
          Venue: {venue.for_booking}
          location: {venue.location}
          facilitator: {venue.facilitator}
          Price: ₹{venue.price}
          Event Date: {event_date}
          Booking Time: {booking_time_ist.strftime('%Y-%m-%d %I:%M %p')} 
          Attendees: {attendees}
          Phone: {phone}
          Email: {email}

        We're excited to host your event and ensure everything goes smoothly. If you have any special requests or need assistance, feel free to reach out—we're here to help!

        You can view or manage your booking anytime from your account: {home_url}

        Looking forward to seeing you there!
        Regards,
        Event Team
        """)

        # Send email confirmation
        send_mail(
            subject=' Your Venue Booking is Confirmed! 🎉',
            message=email_message,
            from_email='noreply@example.com',
            recipient_list=[email],
            fail_silently=False,
        )

        return redirect('home')
    return render(request, 'booking.html', {'venue': venue})



@login_required
def My_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    today = now().date()
 
    return render(request, 'booking/my_booking.html', {'bookings': bookings, 'today': today})

@login_required
def Update_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    venues = Venue.objects.all()  # 🛠 ADD THIS

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        attendees = request.POST.get('attendees')
        event_date = parse_date(request.POST.get('event_date'))
        venue_id = request.POST.get('venue')

        # Get selected venue
        selected_venue = get_object_or_404(Venue, id=venue_id)

        # Conflict check (excluding current booking)
        conflict = Booking.objects.filter(
            venue=selected_venue,
            event_date=event_date
        ).exclude(id=booking.id).exists()

        if conflict:
            messages.error(
                request, 
                f"This venue ({selected_venue.for_booking} by {selected_venue.facilitator}) "
                f"is already booked for {event_date} at {selected_venue.location}."
            )
            return render(request, 'booking/update_booking.html', {
                'booking': booking,
                'venues': venues,
            })

        # If no conflict, update the booking
        booking.name = name
        booking.phone = phone
        booking.email = email
        booking.attendees = attendees
        booking.event_date = event_date
        booking.venue = selected_venue
        booking.location = selected_venue.location
        booking.price = selected_venue.price

        # Transport logic
        need_transport = request.POST.get('need_transport') == 'yes'
        transport_type = request.POST.get('transport_type') if need_transport else None
        booking.need_transport = need_transport
        booking.transport_type = transport_type

        booking.save()
        messages.success(request, 'Booking updated successfully!')
        return redirect('my_bookings')

    return render(request, 'booking/update_booking.html', {
        'booking': booking,
        'venues': venues,
    })



@login_required
def Cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booking.delete()
    return redirect('my_bookings')

# Feedback view

@login_required
def Submit_feedback(request):
    if request.method == "POST":
        message = request.POST.get("message")
        # sentiment = analyze_sentiment(message)
        sentiment = TextBlob(message).sentiment.polarity
        sentiment_label = "positive" if sentiment > 0 else "negative" if sentiment < 0 else "neutral"

        Feedback.objects.create(user=request.user, message=message, sentiment=sentiment_label)
        return redirect("feedback")
    feedbacks = Feedback.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "feedback.html",{"feedbacks": feedbacks} )


@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def View_feedback(request):
    feedbacks = Feedback.objects.all().order_by("-created_at")
    return render(request, "view_feedback.html", {"feedbacks": feedbacks})

@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def Reply_feedback(request, feedback_id):
    if request.method == 'POST':
        reply = request.POST.get('admin_reply')
        fb = Feedback.objects.get(id=feedback_id)
        fb.admin_reply = reply
        fb.replied_at = timezone.now()
        fb.save()
        return redirect('view_feedback')
    return render(request, 'reply_feedback.html', {'feedback': Feedback.objects.get(id=feedback_id)})
 
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def Delete_feedback(request, feedback_id):
    fb = get_object_or_404(Feedback, id=feedback_id)
    fb.delete()
    messages.success(request, "Feedback deleted successfully.")
    return redirect("view_feedback") 
# Chat Boat view

def Chat_view(request):
    return render(request, 'home.html')

def Send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '').lower()

        # Try to find a matching stored query
        match = PairMsg.objects.filter(Q(user_query__icontains=message)).first()
        if match:
            return JsonResponse({'response': match.bot_reply})
        else:
            return JsonResponse({'response': "Sorry, I don't understand your question yet."})
   


def Services_view(request):
    
    event_services = Service.objects.filter(category='event') # .prefetch_related('types', 'content_ideas')
    catering_services = Service.objects.filter(category='catering')# .prefetch_related('types', 'content_ideas')
    other_services = Service.objects.filter(category='other')# .prefetch_related('types', 'content_ideas')
    catering_and_other_services = list(chain(catering_services, other_services))# .prefetch_related('types', 'content_ideas')
    return render(request, 'services.html', {
        'event_services': event_services,
        'catering_services': catering_services,
        'other_services': other_services,
        'catering_and_other_services': catering_and_other_services,
    })
    
# LogIn view

def LogIn_view(request):
    if request.method == "POST":
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')
        next_url = request.POST.get('next')

       
        user = authenticate(request, username=username_or_email, password=password)
       
        if user is None:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)
            return redirect(next_url) if next_url else redirect('home')# Redirect to your home/dashboard
        else:
            return render(request, 'login.html', {'message': 'Invalid Username And Password'})

    return render(request, 'login.html', {'next': request.GET.get('next', '')})

# Logout view
def LogOut_view(request):
    logout(request)
    return redirect('login')  # Use named URL pattern 'login'

# Signup view
def Singup_view(request):
    
    if request.method == "POST":
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
       
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                
            )
            user.save()

            # Send confirmation email
            send_mail(
                "Welcome to Our Site!",
                f"Hi {first_name}, thanks for registering.",
                settings.EMAIL_HOST_USER ,
                [email],
                fail_silently=False,
            )

            messages.success(request, "Account created successfully. Check your email!")
            login(request, user)
            return render(request,'home.html')
    
    return render(request, 'signup.html')


def Forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            link = request.build_absolute_uri(f"/reset-password/{uid}/{token}/")

            send_mail(
                "Reset Your Password",
                f"Click the link to reset your password: {link}",
                "noreply@example.com",
                [email],
                fail_silently=False,
            )
            messages.success(request, "Password reset link has been sent.")
        else:
            messages.error(request, "Email not found.")
        return redirect("forgot_password")
    return render(request, "forget.html")


def Reset_password(request, uidb64, token):
    User = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            password = request.POST.get("password")
            confirm = request.POST.get("confirm")
            if password == confirm:
                user.set_password(password)
                user.save()
                messages.success(request, "Password has been reset.")
                return redirect("login")
            else:
                messages.error(request, "Passwords do not match.")
        return render(request, "reset.html")
    else:
        messages.error(request, "Invalid or expired link.")
        return redirect("forgot_password")