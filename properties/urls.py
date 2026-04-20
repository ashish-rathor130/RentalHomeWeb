from django.urls import path
from . import views

urlpatterns = [
    path('become-host/', views.become_host, name='become_host'),
    path('about_us/', views.about_us, name='about_us'),
    path('edit-property/<int:pk>/', views.edit_property, name='edit_property'),
    path('property/<int:pk>/', views.property_detail, name='property_detail'),
    path('book-property/<int:pk>/', views.book_property, name='book_property'), 
    path('my-bookings/', views.booking_history, name='booking_history'),
    path('cancel-booking/<int:pk>/', views.cancel_booking, name='cancel_booking'),
    
    path('subscriptions/', views.subscription_plans, name='subscriptions'),
    path('buy-subscription/<str:plan>/', views.buy_subscription, name='buy_subscription'),
    
    path('payment/<str:plan>/', views.payment_page, name='payment_page'),
    path('confirm-payment/<str:plan>/', views.confirm_payment, name='confirm_payment'),
]
