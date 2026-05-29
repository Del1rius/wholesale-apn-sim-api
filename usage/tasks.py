from celery import shared_task
from django.db.models import Sum
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_usage_and_check_limit(self, iccid):
    """
    Asynchronous task to calculate total usage and suspend SIM if limit exceeded.
    """
    try:
        from inventory.models import SIMCard
        from usage.models import DataUsageRecord
        
        # Get the SIM card
        sim = SIMCard.objects.select_for_update().get(iccid=iccid)
        
        # Calculate total usage for current billing cycle
        total_usage = DataUsageRecord.objects.filter(
            sim_card=sim
        ).aggregate(
            total=Sum('data_consumed_mb')
        )['total'] or Decimal('0')
        
        logger.info(f"SIM {iccid}: Total usage = {total_usage} MB, Limit = {sim.data_limit_mb} MB")
        
        # Check if limit exceeded
        if total_usage > sim.data_limit_mb and sim.status == 'assigned':
            sim.status = 'suspended'
            sim.save()
            logger.warning(f"SIM {iccid} automatically suspended due to data limit breach")
            return {
                'status': 'suspended',
                'iccid': iccid,
                'total_usage': float(total_usage),
                'limit': float(sim.data_limit_mb)
            }
        
        return {
            'status': 'ok',
            'iccid': iccid,
            'total_usage': float(total_usage),
            'limit': float(sim.data_limit_mb)
        }
        
    except Exception as exc:
        logger.error(f"Error processing usage for {iccid}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)
        


@shared_task
def generate_usage_reports():
    """
    Periodic task to generate usage reports for all organizations.
    Run this task daily to generate usage summaries.
    """
    from usage.models import DataUsageRecord, BillingCycle
    from users.models import Organization
    from django.utils import timezone
    
    current_date = timezone.now().date()
    report_data = []
    
    for org in Organization.objects.all():
        # Get current billing cycle
        current_cycle = BillingCycle.objects.filter(
            organization=org,
            start_date__lte=current_date,
            end_date__gte=current_date,
            is_active=True
        ).first()
        
        if current_cycle:
            total_usage = DataUsageRecord.objects.filter(
                billing_cycle=current_cycle
            ).aggregate(
                total=Sum('data_consumed_mb')
            )['total'] or Decimal('0')
            
            report_data.append({
                'organization': org.name,
                'billing_cycle': str(current_cycle),
                'total_usage_mb': float(total_usage)
            })
    
    logger.info(f"Generated usage reports for {len(report_data)} organizations")
    return {'status': 'success', 'reports': report_data}


@shared_task(bind=True, max_retries=3)
def send_usage_alert(self, iccid, usage_percentage):
    """
    Send usage alert email when SIM approaches data limit.
    
    Args:
        iccid: The ICCID of the SIM card
        usage_percentage: Current usage percentage
    """
    try:
        from inventory.models import SIMCard
        from users.models import User
        from django.core.mail import send_mail
        from django.conf import settings
        
        sim = SIMCard.objects.get(iccid=iccid)
        
        if sim.organization:
            # Get network admins for this organization
            admins = User.objects.filter(
                organization=sim.organization,
                role='network_admin',
                is_active=True
            )
            
            for admin in admins:
                send_mail(
                    subject=f'Usage Alert: SIM {iccid}',
                    message=f"""
                    Hello {admin.first_name or admin.username},
                    
                    SIM card {iccid} has reached {usage_percentage}% of its data limit.
                    
                    Current Status: {sim.get_status_display()}
                    Data Limit: {sim.data_limit_mb} MB
                    
                    Please review and take appropriate action.
                    
                    Best regards,
                    APN & SIM Management System
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[admin.email],
                    fail_silently=False,
                )
            
            logger.info(f"Usage alert sent for SIM {iccid} at {usage_percentage}%")
        
        return {'status': 'success', 'iccid': iccid}
        
    except Exception as exc:
        logger.error(f"Error sending usage alert for {iccid}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def cleanup_old_usage_records():
    """
    Periodic task to archive or delete old usage records.
    Run this task monthly to clean up records older than 2 years.
    """
    from usage.models import DataUsageRecord
    from django.utils import timezone
    from datetime import timedelta
    
    two_years_ago = timezone.now() - timedelta(days=730)
    
    old_records = DataUsageRecord.objects.filter(
        recorded_at__lt=two_years_ago
    )
    
    count = old_records.count()
    # In production, you might want to archive instead of delete
    # old_records.delete()
    
    logger.info(f"Found {count} old usage records (older than 2 years)")
    return {'status': 'success', 'old_records_count': count}
