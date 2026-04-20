# views.py
from urllib import request

from django.shortcuts import render, redirect,get_object_or_404, redirect
from .forms import PropertyForm
from django.contrib import messages
from .models import Property
from django.contrib.auth.decorators import login_required
from bookings.models import Booking
from django.conf import settings
from datetime import date
from .forms import BookingForm   # make sure this exists
from .models import Subscription



def become_host(request):
    subscription, created = Subscription.objects.get_or_create(
    user=request.user,
    defaults={'plan': 'free'}
    )

    total_properties = Property.objects.filter(host=request.user).count()

    if total_properties >= subscription.home_limit:
        messages.error(request, "You reached your plan limit. Upgrade your plan.")
        return redirect('subscriptions')
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    if not request.user.phone:
        return redirect('send_mobile_otp',user_id=request.user.id)
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property = form.save(commit=False)
            property.host = request.user
            property.save()

            user = request.user
            user.is_host = True
            user.save()
            
            messages.success(request, 'Your home has been listed successfully!')
            return redirect('home')
    else:
        form = PropertyForm(request.POST, request.FILES)

    return render(request, 'properties/become_host.html', {'form': form})

@login_required
def edit_property(request, pk):
    property = get_object_or_404(Property, id=pk, host=request.user)

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property)
        if form.is_valid():
            form.save()
            return redirect('profile')   # or property detail page
    else:
        form = PropertyForm(instance=property)

    return render(request, 'properties/edit_property.html', {'form': form})

def property_detail(request, pk):
    property = get_object_or_404(Property, id=pk)
    return render(request, 'properties/property_detail.html', {'property': property})





@login_required
def book_property(request, pk):
    property = get_object_or_404(Property, id=pk)

    if request.method == 'POST':
        if request.user.is_phone_verified == False:
            messages.warning(request, "Please verify your phone number before booking.")
            return redirect('send_mobile_otp', user_id=request.user.id) 
        
        
        form = BookingForm(request.POST)

        if form.is_valid():
            check_in = form.cleaned_data['check_in']
            check_out = form.cleaned_data['check_out']

            # ✅ 1. Past date check
            if check_in < date.today():
                messages.error(request, "Check-in date cannot be in the past.")
                return redirect('book_property', pk=pk)

            # ✅ 2. Check-out validation
            if check_out <= check_in:
                messages.error(request, "Check-out must be after check-in.")
                return redirect('book_property', pk=pk)

            # ✅ 3. Prevent overlapping bookings
            overlap = Booking.objects.filter(
                property=property,
                check_in__lt=check_out,
                check_out__gt=check_in,
                status='booked'   # important (ignore cancelled)
            ).exists()

            if overlap:
                messages.warning(request, "This property is already booked for selected dates.")
                return redirect('book_property', pk=pk)

            # ✅ 4. Save booking
            booking = form.save(commit=False)
            booking.user = request.user
            booking.property = property
            booking.status = 'booked'  # optional if default already set
            booked = booking.save()
            
            property.is_available = False
            property.save()

            messages.success(request, "🎉 Booking confirmed successfully!")
            return redirect('booking_history')

    else:
        form = BookingForm()

    return render(request, 'properties/book_property.html', {
        'form': form,
        'property': property,
    })

# 📜 Booking History
@login_required
def booking_history(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booked_at')
    return render(request, 'properties/booking_history.html', {'bookings': bookings})


# ❌ Cancel Booking
@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, id=pk, user=request.user)
    property = get_object_or_404(Property, id=booking.property.id)

    if booking.status == 'cancelled':
        messages.warning(request, "Booking already cancelled.")
    else:
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, "Booking cancelled successfully!")
        
        property.is_available = True
        property.save()

    return redirect('booking_history')

def about_us(request):
    return render(request, 'ui/aboutus.html')


from .models import Subscription

@login_required
def subscription_plans(request):
    return render(request, 'properties/subscription.html')


@login_required
def buy_subscription(request, plan):
    subscription, created = Subscription.objects.get_or_create(user=request.user)

    subscription.plan = plan
    subscription.save()

    messages.success(request, f"{plan.capitalize()} plan activated successfully!")
    return redirect('profile', user_id=request.user.id)

# views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def payment_page(request, plan):
    plans = {
        'free': 0,
        'recommended': 199,
        'pro': 499
    }

    amount = plans.get(plan, 0)

    return render(request, 'properties/payment.html', {
        'plan': plan,
        'amount': amount
    })


@login_required
def confirm_payment(request, plan):
    from .models import Subscription

    subscription, created = Subscription.objects.get_or_create(user=request.user)

    subscription.plan = plan
    subscription.save()

    return redirect('profile')