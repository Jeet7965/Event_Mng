from django.urls import path
from .views import * 
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', Home_view, name='home'),
    path('about/', About_view, name='about'),
    path('contact/', Contact_view, name='contact'),
    path('login/', LogIn_view, name='login'),  
    path('logout/', LogOut_view, name='logout'),  
    path('signup/', Singup_view, name='signup'),
    path('search/', Search, name='search'),
    path('book/<int:venue_id>/',Book_event, name='book_event'),
    path('chat/',Chat_view, name='chat'),
    path('chatbot-response/', Send_message, name='chatbot-response'),
    path('services/', Services_view, name='services'),
    path('my-bookings/',My_bookings, name='my_bookings'),
    path('update/<int:booking_id>/', Update_booking, name='update_booking'),
    path('cancel/<int:booking_id>/', Cancel_booking, name='cancel_booking'),
    
    path("feedback/", Submit_feedback, name="feedback"),
    path("view_feedback/", View_feedback, name="view_feedback"),
    path('feedback/reply/<int:feedback_id>/', Reply_feedback, name='reply_feedback'),
    path('delete-feedback/<int:feedback_id>/', Delete_feedback, name='delete_feedback'),

    path('forgot-password/', Forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', Reset_password, name='reset_password'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
