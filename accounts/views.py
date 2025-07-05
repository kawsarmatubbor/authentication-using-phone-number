from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Verification
import random

# Create your views here.
def sign_up_view(request):
    if request.method == "POST":
        phone_number = request.POST.get('phone_number')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        password_1 = request.POST.get('password_1')
        password_2 = request.POST.get('password_2')

        if not all([phone_number, first_name, last_name, email, address, password_1, password_2]):
            return render(request, 'sign-up.html', { 'error': "Fill all required fields" })
        
        if len(password_1) < 8 and len(password_2) < 8:
            return render(request, 'sign-up.html', { 'error': "Passwords are too small" })
        
        if password_1 != password_2:
            return render(request, 'sign-up.html', { 'error': "Passwords do not match" })
        
        if CustomUser.objects.filter(phone_number = phone_number).exists():
            return render(request, 'sign-up.html', { 'error': "Phone number already exist" })
        
        try:
            user = CustomUser.objects.create_user(
            phone_number = phone_number,
            first_name = first_name,
            last_name = last_name,
            email = email,
            address = address,
            password = password_1
        )
        except Exception as e:
            return render(request, 'sign-up.html', { 'error': e })
        
        login(request, user)
        return redirect('index')
    
    else:
        return render(request, 'sign-up.html')
        
def sign_in_view(request):
    if request.method == "POST":
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')

        if not all([phone_number, password]):
            return render(request, 'sign-in.html', {'error':'Fill all required fields'})
        
        user = authenticate(request, phone_number = phone_number, password = password)

        if user is not None:
            login(request, user)
            if not request.POST.get('remember_me'):
                request.session.set_expiry(0)
            return redirect('index')
        else:
            return render(request, 'sign-in.html', {'error':'User does not exists'})

    else:
        if request.user.is_authenticated:
            return redirect('index')
        return render(request, 'sign-in.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('index')

def forgot_password_view(request):
    if request.method == "POST":
        phone_number = request.POST.get('phone_number')

        if not phone_number:
            return render(request, 'forgot-password.html', { 'error': "Fill all required fields" })

        try:
            user = CustomUser.objects.get(phone_number = phone_number)
            Verification.objects.filter(user=user).delete()

            if user is not None:
                otp = random.randint(100000, 999999)
                Verification.objects.create(
                    user = user,
                    otp = otp
                )
                request.session['reset_user_id'] = user.id
                return redirect('verification')
            
        except CustomUser.DoesNotExist:
            return render(request, 'forgot-password.html', {'error': 'User number not found'})

    else:
        return render(request, 'forgot-password.html')

def verification_view(request):
    reset_user_id = request.session.get('reset_user_id')
    if not reset_user_id:
        return redirect('forgot-password')
    
    if request.method == "POST":
        try:
            user = CustomUser.objects.get(id=reset_user_id)
        except CustomUser.DoesNotExist:
            return redirect('forgot-password')

        user_otp = request.POST.get('otp')
        
        if not user_otp:
            return render(request, 'verification.html', {'error': 'Fill all required fields'})

        try:
            db_otp = Verification.objects.get(user = user).otp

            if user_otp == db_otp:
                return redirect('reset-password')
            else:
                return render(request, 'verification.html', {'error': 'OTP does not match'})
        
        except Verification.DoesNotExist:
            return render(request, 'forgot-password.html', {'error': 'OTP not found'})

    else:
        return render(request, 'verification.html')

def reset_password_view(request):
    reset_user_id = request.session.get('reset_user_id')
    if not reset_user_id:
        return redirect('forgot-password')
    
    if request.method == "POST":
        password_1 = request.POST.get('password_1')
        password_2 = request.POST.get('password_2')

        if not all([password_1, password_2]):
            return render(request, 'reset-password.html', {'error': 'Fill all required fields'})
        
        if len(password_1) < 8 and len(password_2) < 8:
            return render(request, 'sign-up.html', { 'error': "Passwords are too small" })

        if password_1 != password_2:
            return render(request, 'reset-password.html', {'error': 'Passwords do not match'})
        
        try:
            user = CustomUser.objects.get(id = reset_user_id)
        except CustomUser.DoesNotExist:
            return redirect('forgot-password')

        user.set_password(password_1)
        user.save()

        Verification.objects.get(user = user).delete()
        del request.session['reset_user_id']

        return redirect('sign-in')

    else:
        return render(request, 'reset-password.html')