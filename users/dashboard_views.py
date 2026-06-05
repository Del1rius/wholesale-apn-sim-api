from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta

from inventory.models import SIMCard
from usage.models import DataUsageRecord, BillingCycle


def login_view(request):
    # Handle user login
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # Validate that both fields are provided
        if not username or not password:
            messages.error(request, 'Please enter both username and password')
            return render(request, 'login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')


def logout_view(request):
    # Handle user logout
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    # Main dashboard view with real data from database
    user = request.user

    # Get organization
    organization = user.organization if hasattr(user, 'organization') else None

    # Filter SIM cards based on user role
    if user.is_superuser:
        # Superuser sees everything
        sim_cards = SIMCard.objects.all()
    elif organization:
        # All other users (including network_admin) see only their organization's SIM cards
        sim_cards = SIMCard.objects.filter(organization=organization)
    else:
        # User has no organization - show nothing
        sim_cards = SIMCard.objects.none()

    # Get current billing cycle for the user's organization
    current_date = timezone.now().date()
    if organization:
        current_cycle = BillingCycle.objects.filter(
            organization=organization,
            start_date__lte=current_date,
            end_date__gte=current_date,
            is_active=True
        ).first()
    else:
        current_cycle = None

    # Calculate statistics
    total_sims = sim_cards.count()
    active_sims = sim_cards.filter(status='assigned').count()
    available_sims = sim_cards.filter(status='available').count()
    suspended_sims_queryset = sim_cards.filter(status='suspended')
    suspended_count = suspended_sims_queryset.count()

    # Calculate usage for each SIM card
    sims_with_usage = []
    total_usage_mb = 0

    # Define status priority for sorting (lower number = higher priority)
    status_priority = {
        'suspended': 1,    # Highest priority - needs attention!
        'assigned': 2,     # Active SIMs
        'available': 3,    # Ready to allocate
        'deactivated': 4,  # Lowest priority
        'lost': 5
    }

    for sim in sim_cards:
        # Get usage records for current billing cycle or last 30 days
        if current_cycle:
            usage_records = DataUsageRecord.objects.filter(
                sim_card=sim,
                billing_cycle=current_cycle
            )
        else:
            thirty_days_ago = timezone.now() - timedelta(days=30)
            usage_records = DataUsageRecord.objects.filter(
                sim_card=sim,
                recorded_at__gte=thirty_days_ago
            )

        # Calculate total usage for this SIM
        sim_total_usage = usage_records.aggregate(
            total=Sum('data_consumed_mb')
        )['total'] or 0

        # Auto-update status based on usage vs limit
        if sim.data_limit_mb and sim.data_limit_mb > 0:
            if float(sim_total_usage) >= sim.data_limit_mb:
                # Usage exceeds limit - should be suspended
                if sim.status == 'assigned':
                    sim.status = 'suspended'
                    sim.save()
            else:
                # Usage is below limit - should be active if currently suspended
                if sim.status == 'suspended':
                    sim.status = 'assigned'
                    sim.save()

        total_usage_mb += float(sim_total_usage)

        # Calculate usage percentage
        usage_percentage = 0
        if sim.data_limit_mb and sim.data_limit_mb > 0:
            usage_percentage = (float(sim_total_usage) /
                                sim.data_limit_mb) * 100

        # Add SIM with usage data
        sims_with_usage.append({
            'ICCID': sim.iccid,
            'MSISDN': sim.phone_number or 'N/A',
            'Status': sim.get_status_display(),
            'DataLimit_MB': sim.data_limit_mb or 0,
            'total_consumed': float(sim_total_usage),
            'usage_percentage': round(usage_percentage, 2),
            'DateAllocated': sim.activation_date or sim.date_created.date(),
            # For sorting
            '_status_priority': status_priority.get(sim.status, 99)
        })

    # Sort by status priority first (suspended=1, active=2, etc.),
    # then by usage percentage (highest to lowest within each status group)
    sims_with_usage.sort(
        key=lambda x: (x['_status_priority'], -x['usage_percentage']))

    # Convert total usage to GB
    total_usage_gb = round(total_usage_mb / 1024, 2)

    # Get recent usage logs (last 50)
    if user.is_superuser:
        # Superuser sees all usage logs
        usage_logs = DataUsageRecord.objects.all()
    elif organization:
        # All other users see only their organization's usage logs
        usage_logs = DataUsageRecord.objects.filter(
            sim_card__organization=organization
        )
    else:
        # User has no organization - show nothing
        usage_logs = DataUsageRecord.objects.none()

    usage_logs = usage_logs.select_related(
        'sim_card').order_by('-recorded_at')[:50]

    # Format usage logs for template
    formatted_logs = []
    for log in usage_logs:
        formatted_logs.append({
            'LogID': str(log.record_id)[:8],  # Short ID for display
            'ICCID': log.sim_card.iccid,
            'DataConsumed_MB': float(log.data_consumed_mb),
            'Timestamp': log.recorded_at
        })

    # Get suspended SIMs list
    suspended_sims_list = []
    for sim in suspended_sims_queryset:
        suspended_sims_list.append({
            'iccid': sim.iccid,
            'phone_number': sim.phone_number or 'N/A',
            'carrier': sim.carrier
        })

    context = {
        'organization': organization,
        'total_sims': total_sims,
        'active_sims': active_sims,
        'suspended_sims': suspended_sims_list,
        'suspended_count': suspended_count,
        'available_sims': available_sims,
        'total_usage_gb': total_usage_gb,
        'sims': sims_with_usage,
        'usage_logs': formatted_logs,
    }

    return render(request, 'dashboard.html', context)


@login_required
def sim_list_view(request):
    # SIM card list view with real data
    user = request.user

    # Get organization
    organization = user.organization if hasattr(user, 'organization') else None

    # Get current billing cycle for the user's organization
    current_date = timezone.now().date()
    if organization:
        current_cycle = BillingCycle.objects.filter(
            organization=organization,
            start_date__lte=current_date,
            end_date__gte=current_date,
            is_active=True
        ).first()
    else:
        current_cycle = None

    # Filter SIM cards based on user role
    if user.is_superuser:
        # Superuser sees everything
        sim_cards = SIMCard.objects.all()
    elif organization:
        # All other users (including network_admin) see only their organization's SIM cards
        sim_cards = SIMCard.objects.filter(organization=organization)
    else:
        # User has no organization - show nothing
        sim_cards = SIMCard.objects.none()

    # Apply filters from query parameters
    status_filter = request.GET.get('status', None)
    if status_filter and status_filter != 'all':
        # Map display status to model status
        status_map = {
            'Active': 'assigned',
            'Suspended': 'suspended',
            'Deactivated': 'deactivated',
            'Unallocated': 'available'
        }
        model_status = status_map.get(status_filter, status_filter.lower())
        sim_cards = sim_cards.filter(status=model_status)

    search_query = request.GET.get('q', None)
    if search_query:
        sim_cards = sim_cards.filter(
            Q(iccid__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )

    # Format SIM cards for template (match expected field names)
    sims_formatted = []

    # Define status priority for sorting (lower number = higher priority)
    status_priority = {
        'suspended': 1,    # Highest priority - needs attention!
        'assigned': 2,     # Active SIMs
        'available': 3,    # Ready to allocate
        'deactivated': 4,  # Lowest priority
        'lost': 5
    }

    for sim in sim_cards:
        # Get usage for this SIM
        if current_cycle:
            usage_records = DataUsageRecord.objects.filter(
                sim_card=sim,
                billing_cycle=current_cycle
            )
        else:
            thirty_days_ago = timezone.now() - timedelta(days=30)
            usage_records = DataUsageRecord.objects.filter(
                sim_card=sim,
                recorded_at__gte=thirty_days_ago
            )

        total_usage = usage_records.aggregate(
            total=Sum('data_consumed_mb')
        )['total'] or 0

        # Auto-update status based on usage vs limit
        if sim.data_limit_mb and sim.data_limit_mb > 0:
            if float(total_usage) >= sim.data_limit_mb:
                # Usage exceeds limit - should be suspended
                if sim.status == 'assigned':
                    sim.status = 'suspended'
                    sim.save()
            else:
                # Usage is below limit - should be active if currently suspended
                if sim.status == 'suspended':
                    sim.status = 'assigned'
                    sim.save()

        usage_percentage = 0
        if sim.data_limit_mb and sim.data_limit_mb > 0:
            usage_percentage = (float(total_usage) / sim.data_limit_mb) * 100

        # Map status to display format
        status_display_map = {
            'assigned': 'assigned',  # Keep as 'assigned' for template
            'suspended': 'suspended',
            'deactivated': 'deactivated',
            'available': 'available',
            'lost': 'lost'
        }

        sims_formatted.append({
            'ICCID': sim.iccid,
            'MSISDN': sim.phone_number or 'N/A',
            # Use lowercase status
            'status': status_display_map.get(sim.status, sim.status),
            'DataLimit_MB': sim.data_limit_mb or 0,
            'total_consumed': float(total_usage),
            'usage_percentage': round(usage_percentage, 2),
            'DateAllocated': sim.activation_date or sim.date_created.date(),
            # For sorting
            '_status_priority': status_priority.get(sim.status, 99)
        })

        # Debug: Print what we're sending to template
        print(
            f"DEBUG: SIM {sim.iccid} - Status: {sim.status} -> {status_display_map.get(sim.status, sim.status)}")

    # Sort by status priority first (suspended=1, active=2, etc.),
    # then by usage percentage (highest to lowest within each status group)
    sims_formatted.sort(
        key=lambda x: (x['_status_priority'], -x['usage_percentage']))

    # Get suspended SIMs for alert banner (before applying filters)
    if user.is_superuser:
        all_sim_cards = SIMCard.objects.all()
    elif organization:
        all_sim_cards = SIMCard.objects.filter(organization=organization)
    else:
        all_sim_cards = SIMCard.objects.none()

    suspended_sims_queryset = all_sim_cards.filter(status='suspended')
    suspended_sims_list = []
    for sim in suspended_sims_queryset:
        suspended_sims_list.append({
            'iccid': sim.iccid,
            'phone_number': sim.phone_number or 'N/A',
            'carrier': sim.carrier
        })

    context = {
        'sims': sims_formatted,
        'status_filter': status_filter,
        'search_query': search_query,
        'suspended_sims': suspended_sims_list,
        'suspended_count': len(suspended_sims_list)
    }

    return render(request, 'sim_list.html', context)


@login_required
def sim_detail_view(request, iccid):
    """SIM card detail view with usage history"""
    user = request.user

    # Get SIM card
    sim_obj = get_object_or_404(SIMCard, iccid=iccid)

    # Check permission
    if not (user.is_superuser or user.role == 'network_admin'):
        if sim_obj.organization != user.organization:
            messages.error(
                request, 'You do not have permission to view this SIM card')
            return redirect('dashboard')

    # Get usage records for this SIM (before handling POST to have accurate data)
    usage_records = DataUsageRecord.objects.filter(
        sim_card=sim_obj
    ).order_by('-recorded_at')[:100]  # Last 100 records

    # Calculate total usage
    total_usage = usage_records.aggregate(
        total=Sum('data_consumed_mb')
    )['total'] or 0

    # Auto-update status based on current usage vs limit
    if sim_obj.data_limit_mb and sim_obj.data_limit_mb > 0:
        if float(total_usage) >= sim_obj.data_limit_mb:
            # Usage exceeds limit - should be suspended
            if sim_obj.status == 'assigned':
                sim_obj.status = 'suspended'
                sim_obj.save()
        else:
            # Usage is below limit - should be active if currently suspended
            if sim_obj.status == 'suspended':
                sim_obj.status = 'assigned'
                sim_obj.save()

    # Handle POST request for updating data limit
    if request.method == 'POST':
        new_limit = request.POST.get('data_limit_mb')
        try:
            new_limit = int(new_limit)
            if new_limit <= 0:
                messages.error(request, 'Data limit must be greater than 0')
            elif new_limit > 100000:
                messages.error(request, 'Data limit cannot exceed 100,000 MB')
            else:
                # Update the data limit
                sim_obj.data_limit_mb = new_limit

                # Check if status needs to be updated based on usage
                if float(total_usage) >= new_limit:
                    # Usage exceeds new limit - suspend the SIM
                    if sim_obj.status != 'suspended':
                        sim_obj.status = 'suspended'
                        messages.warning(
                            request,
                            f'Data limit updated to {new_limit} MB. '
                            f'SIM has been suspended due to exceeding the limit.'
                        )
                    else:
                        messages.success(
                            request,
                            f'Data limit updated to {new_limit} MB successfully!'
                        )
                else:
                    # Usage is below new limit - ensure SIM is active if it was suspended
                    if sim_obj.status == 'suspended':
                        sim_obj.status = 'assigned'
                        messages.success(
                            request, f'Data limit updated to {new_limit} MB. SIM has been reactivated.')
                    else:
                        messages.success(
                            request, f'Data limit updated to {new_limit} MB successfully!')

                sim_obj.save()
                return redirect('sim_detail', iccid=iccid)
        except (ValueError, TypeError):
            messages.error(request, 'Invalid data limit value')

    # Calculate usage percentage
    usage_percentage = 0
    if sim_obj.data_limit_mb and sim_obj.data_limit_mb > 0:
        usage_percentage = (float(total_usage) / sim_obj.data_limit_mb) * 100

    # Calculate remaining
    remaining_mb = (sim_obj.data_limit_mb or 0) - float(total_usage)

    # Create a formatted sim object for the template
    class FormattedSIM:
        def __init__(self, sim_obj, total_usage, usage_percentage, remaining_mb):
            self.ICCID = sim_obj.iccid
            self.MSISDN = sim_obj.phone_number or 'N/A'
            self.status = sim_obj.status
            self.DataLimit_MB = sim_obj.data_limit_mb or 0
            self.DateAllocated = sim_obj.activation_date or sim_obj.date_created
            self.OrgID = type('obj', (object,), {
                              'Name': sim_obj.organization.name if sim_obj.organization else 'N/A'})()
            self.total_consumed = float(total_usage)
            self.usage_percentage = round(usage_percentage, 2)
            self.remaining_mb = remaining_mb
            self.carrier = sim_obj.carrier
            self.network_type = sim_obj.network_type
            self.get_status_display = sim_obj.get_status_display

    sim = FormattedSIM(sim_obj, total_usage, usage_percentage, remaining_mb)

    # Format usage logs for template (match expected field names)
    formatted_usage_logs = []
    for record in usage_records:
        formatted_usage_logs.append({
            'LogID': str(record.record_id)[:8],  # Short ID for display
            'Timestamp': record.recorded_at,
            'DataConsumed_MB': float(record.data_consumed_mb)
        })

    context = {
        'sim': sim,
        'iccid': iccid,
        'usage_logs': formatted_usage_logs,  # Changed from usage_records to usage_logs
        'total_usage_mb': float(total_usage),
        'usage_percentage': round(usage_percentage, 2)
    }

    return render(request, 'sim_detail.html', context)
