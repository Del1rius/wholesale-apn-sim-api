from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')


def logout_view(request):
    """Handle user logout"""
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    """Main dashboard view"""
    # TODO: Add real SIM card statistics from database
    context = {
        'organization': request.user.organization if hasattr(request.user, 'organization') else None,
        'total_sims': 0,
        'active_sims': 0,
        'suspended_sims': [],
        'suspended_count': 0,
        'available_sims': 0,
        'total_usage_gb': 0.0,
        'sims': [],
        'usage_logs': [],
    }
    return render(request, 'dashboard.html', context)


@login_required
def sim_list_view(request):
    """SIM card list view"""
    # TODO: Add real SIM card list from database
    context = {
        'sims': [],
    }
    return render(request, 'sim_list.html', context)


@login_required
def sim_detail_view(request, iccid):
    """SIM card detail view"""
    # TODO: Get real SIM card from database
    context = {
        'sim': None,
        'iccid': iccid,
    }
    return render(request, 'sim_detail.html', context)
