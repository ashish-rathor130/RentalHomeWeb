from django.shortcuts import render, redirect

from bookings.models import Booking
from .models import OTP, CustomUser
from .utils import generate_otp, verify_otp
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import authenticate, login,logout
from django.utils.crypto import get_random_string
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm
from .models import Profile

def signup_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        username = request.POST['username']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        try:
            user = CustomUser.objects.create_user(username = username,email=email, password=password)
            otp = generate_otp()
            user.email_otp = otp
            user.save()
            send_mail(
                'Your OTP Code',
                f'Your OTP is: {otp}',
                settings.DEFAULT_USER_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, "An OTP has been sent to your email.")
            return redirect('verify_otp', user_id=user.id)
        
        except Exception as e:
            messages.error(request,f"{e} Go to Forgot password")
            return redirect('signup')

    return render(request, 'auth/signup.html')

def verify_user_otp(request, user_id):
   user = CustomUser.objects.get(id=user_id)
   print(user)
   if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        print(f"User entered OTP: {entered_otp}, Actual OTP: {user.email_otp}")
        
        if entered_otp == user.email_otp:
            user.is_email_verified = True
            user.email_otp = None
            user.save()
            messages.success(request, "Email verified successfully! You can now log in.")
            return redirect('login')
        else:
            return render(request, 'auth/verify_otp.html', {'error': 'Invalid OTP','user_id': user.id})
   return render(request, 'auth/verify_otp.html', {'user_id': user.id})


def resend_otp(request, user_id):
    user = CustomUser.objects.get(id=user_id)

    # Optional: throttle resends (e.g., allow only after 60 seconds)
    if hasattr(user, "otp_last_sent") and user.otp_last_sent:
        if timezone.now() - user.otp_last_sent < timedelta(seconds=60):
            messages.error(request, "Please wait before requesting another OTP.")
            return redirect('verify_otp', user_id=user.id)

    # Generate new OTP
    otp = generate_otp()
    user.email_otp = otp
    user.otp_last_sent = timezone.now()  # add this field in your model
    user.save()

    # Send OTP via email
    send_mail(
        'Your OTP Code',
        f'Your new OTP is: {otp}',
        settings.DEFAULT_USER_EMAIL,
        [user.email],
        fail_silently=False,
    )
    messages.success(request, "A new OTP has been sent to your email.")
    return redirect('verify_otp', user_id=user.id)

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = CustomUser.objects.get(email=email)
            if user.check_password(password):
                if user.is_email_verified:
                    print(login(request, user))
                    messages.success(request, "Login successful!")
                    return redirect('home')
                else:
                    messages.error(request, "Please verify your email before logging in.")
                    return redirect('login')
            else:
                messages.error(request, "Invalid credentials.")
                return redirect('login')
        except CustomUser.DoesNotExist:
            messages.error(request, "User does not exist.")
            return redirect('login')

    return render(request, 'auth/login.html')

def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')

def reset_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = CustomUser.objects.get(email=email)
            print(user)
            # Generate a temporary password
            temp_password = get_random_string(length=8)
            user.set_password(temp_password)
            user.save()

            # Send email with new password
            subject = "Password Reset Request"
            message = f"Hello {user.username},\n\nYour temporary password is: {temp_password}\nPlease log in and change it immediately."
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

            # Success message
            messages.success(request, "A temporary password has been sent to your registered email.")
            return redirect("login")

        except CustomUser.DoesNotExist:
            messages.error(request, "No account found with this email address.")
            return redirect("reset_password")

    return render(request, "auth/reset_password.html")

@login_required
def change_password_view(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        user = request.user

        # Check old password
        if not user.check_password(old_password):
            messages.error(request, "Your old password is incorrect.")
            return redirect("change_password")

        # Check new password match
        if new_password != confirm_password:
            messages.error(request, "New password and confirmation do not match.")
            return redirect("change_password")

        # Update password
        user.set_password(new_password)
        user.save()

        messages.success(request, "Your password has been changed successfully. Please log in again.")
        return redirect("login")

    return render(request, "auth/change_password.html")

@login_required
def profile(request,user_id):
    user = CustomUser.objects.get(pk = user_id)
    property = user.property_set.all()
    bookings = Booking.objects.filter(user=request.user).order_by('-booked_at')
    
    return render(request,'./auth/profile.html',{'user':user, 'rooms': property, 'bookings': bookings})

@login_required
def update_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')   # no need for user_id
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, './auth/update_profile_img.html', {'form': form})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import EditProfileForm

@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile' , user_id=request.user.id)  # pass user_id to profile view
    else:
        form = EditProfileForm(instance=user)

    return render(request, 'auth/edit_profile.html', {'form': form})
    
from django.conf import settings
from twilio.rest import Client
import random, time

OTP_EXPIRY_SECONDS = 300  # 5 minutes

def send_mobile_otp(request,user_id):
    user = CustomUser.objects.get(pk=user_id)
    if request.method == "POST":
        phone = request.POST.get("mobile")
        # ✅ Fix 1: Proper validation
        if not phone or not phone.isdigit() or len(phone) != 10:
            messages.error(request, "Enter valid 10-digit mobile number")
            return redirect("send_mobile_otp",user_id=user.id)

        phone = "+91" + phone
        user.phone = phone
        user.save() 
        print(user.phone)
        

        # ✅ Fix 2: Generate OTP
        otp = str(random.randint(100000, 999999))

        # ✅ Fix 3: Store with expiry
        request.session["otp"] = otp
        request.session["phone"] = phone
        request.session["otp_time"] = time.time()

        try:
            client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )

            client.messages.create(
                body=f"Your OTP is {otp}",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone
            )

            messages.success(request, "OTP sent successfully")
            return redirect("verify_mobile_otp", user_id=user.id)

        except Exception as e:
            print("Twilio Error:", e)
            messages.error(request, "Failed to send OTP")

    return render(request, "auth/send_mobile_otp.html")

def verify_mobile_otp(request,user_id):
    user = CustomUser.objects.get(pk=user_id)
    if request.method == "POST":
        user_otp = request.POST.get("otp")

        session_otp = request.session.get("otp")
        otp_time = request.session.get("otp_time")

        # ✅ Fix 4: Check if OTP exists
        if not session_otp or not otp_time:
            messages.error(request, "Session expired. Request new OTP.")
            return redirect("send_mobile_otp", user_id=user.id)

        # ✅ Fix 5: Expiry check
        if time.time() - otp_time > OTP_EXPIRY_SECONDS:
            request.session.flush()
            messages.error(request, "OTP expired. Please request a new one.")
            return redirect("send_mobile_otp", user_id=user.id)

        # ✅ Fix 6: Match OTP
        if user_otp == session_otp:
            user.is_phone_verified = True
            user.save()

            request.session.flush()  # clear OTP after success
            return redirect("profile", user_id=request.user.id)
            messages.success(request, "Mobile verified successfully")

        else:
            messages.error(request, "Invalid OTP")

    return render(request, "auth/verify_mobile_otp.html")

def resend_mobile_otp(request):
    last_sent = request.session.get("otp_time")

    # ✅ Fix 7: Prevent spam resend
    if last_sent and time.time() - last_sent < 60:
        messages.error(request, "Wait 60 seconds before resending OTP")
        return redirect("verify_otp")

    return redirect("send_mobile_otp")
