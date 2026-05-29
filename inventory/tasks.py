"""
Celery tasks for the inventory app.
Background tasks for SIM card and APN management.
"""

from celery import shared_task
from django.db.models import Count, Q
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def bulk_import_sim_cards(self, sim_data_list, organization_id):
    """
    Bulk import SIM cards from a list of data.
    
    Args:
        sim_data_list: List of dictionaries containing SIM card data
        organization_id: The organization to assign the SIM cards to
    """
    try:
        from inventory.models import SIMCard
        from users.models import Organization
        
        organization = Organization.objects.get(org_id=organization_id)
        created_count = 0
        failed_count = 0
        
        for sim_data in sim_data_list:
            try:
                SIMCard.objects.create(
                    iccid=sim_data['iccid'],
                    phone_number=sim_data.get('phone_number'),
                    carrier=sim_data.get('carrier', 'Unknown'),
                    network_type=sim_data.get('network_type', '4G'),
                    status=sim_data.get('status', 'available'),
                    data_limit_mb=sim_data.get('data_limit_mb', 1000),
                    organization=organization
                )
                created_count += 1
            except Exception as e:
                logger.error(f"Failed to import SIM {sim_data.get('iccid')}: {str(e)}")
                failed_count += 1
        
        logger.info(f"Bulk import completed: {created_count} created, {failed_count} failed")
        return {
            'status': 'success',
            'created': created_count,
            'failed': failed_count
        }
        
    except Exception as exc:
        logger.error(f"Error in bulk import: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def check_sim_inventory_levels():
    """
    Periodic task to check SIM inventory levels and send alerts.
    Run this task daily to notify admins of low inventory.
    """
    from inventory.models import SIMCard
    from users.models import Organization, User
    
    for org in Organization.objects.all():
        available_sims = SIMCard.objects.filter(
            organization=org,
            status='available'
        ).count()
        
        total_sims = SIMCard.objects.filter(organization=org).count()
        
        # Alert if less than 10% available
        if total_sims > 0 and (available_sims / total_sims) < 0.1:
            # Get network admins for this organization
            admins = User.objects.filter(
                organization=org,
                role='network_admin',
                is_active=True
            )
            
            for admin in admins:
                send_mail(
                    subject='Low SIM Inventory Alert',
                    message=f"""
                    Hello {admin.first_name or admin.username},
                    
                    Your organization ({org.name}) has low SIM inventory:
                    - Available SIMs: {available_sims}
                    - Total SIMs: {total_sims}
                    
                    Please consider ordering more SIM cards.
                    
                    Best regards,
                    APN & SIM Management System
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[admin.email],
                    fail_silently=True,
                )
            
            logger.warning(f"Low inventory alert sent for {org.name}")
    
    return {'status': 'success'}


@shared_task(bind=True, max_retries=3)
def sync_sim_status_with_carrier(self, iccid):
    """
    Sync SIM card status with carrier's API.
    This is a placeholder for future carrier API integration.
    
    Args:
        iccid: The ICCID of the SIM card to sync
    """
    try:
        from inventory.models import SIMCard
        
        sim = SIMCard.objects.get(iccid=iccid)
        
        # TODO: Implement actual carrier API integration
        # For now, just log the sync attempt
        logger.info(f"Syncing SIM {iccid} status with carrier {sim.carrier}")
        
        return {
            'status': 'success',
            'iccid': iccid,
            'message': 'Carrier sync not yet implemented'
        }
        
    except Exception as exc:
        logger.error(f"Error syncing SIM {iccid}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def generate_inventory_report():
    """
    Periodic task to generate inventory reports.
    Run this task weekly to generate summary reports.
    """
    from inventory.models import SIMCard
    from users.models import Organization
    
    report_data = []
    
    for org in Organization.objects.all():
        stats = SIMCard.objects.filter(organization=org).aggregate(
            total=Count('iccid'),
            active=Count('iccid', filter=Q(status='assigned')),
            suspended=Count('iccid', filter=Q(status='suspended')),
            available=Count('iccid', filter=Q(status='available')),
            deactivated=Count('iccid', filter=Q(status='deactivated'))
        )
        
        report_data.append({
            'organization': org.name,
            'stats': stats
        })
    
    logger.info(f"Generated inventory report for {len(report_data)} organizations")
    return {'status': 'success', 'report': report_data}
