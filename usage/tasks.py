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
        from inventory.models import SimCard
        from usage.models import UsageLog
        
        # Get the SIM card
        sim = SimCard.objects.select_for_update().get(iccid=iccid)
        
        # Calculate total usage for current billing cycle
        total_usage = UsageLog.objects.filter(
            iccid=sim
        ).aggregate(
            total=Sum('data_consumed_mb')
        )['total'] or Decimal('0')
        
        logger.info(f"SIM {iccid}: Total usage = {total_usage} MB, Limit = {sim.data_limit_mb} MB")
        
        # Check if limit exceeded
        if total_usage > sim.data_limit_mb and sim.status == 'Active':
            sim.status = 'Suspended'
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
        