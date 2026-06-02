# Generated migration for adding validators to data_limit_mb field

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='simcard',
            name='data_limit_mb',
            field=models.IntegerField(
                blank=True,
                help_text='Monthly data limit in MB (maximum 100,000 MB)',
                null=True,
                validators=[MinValueValidator(1), MaxValueValidator(100000)]
            ),
        ),
    ]
