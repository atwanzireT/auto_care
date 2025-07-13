from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")  # replace with your desired redirect
        else:
            messages.error(request, "Invalid credentials")
    return render(request, "accounts/login.html")

def logout_view(request):
    logout(request)
    return redirect("login")  # redirect to login page

def register_view(request):
    if request.method == "POST":
        # You can add full user creation logic here or use a Django form
        pass
    return render(request, "accounts/register.html")


