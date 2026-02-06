# Generated manually to fix datetime field issues

from django.db import migrations
from django.utils import timezone
from datetime import timedelta


def fix_datetime_fields(apps, schema_editor):
    """Fix any records with None datetime values"""
    KotakNeoUserToken = apps.get_model('KOTAK_NEO_API', 'KotakNeoUserToken')
    
    # Fix tokens with None expires_at
    tokens_without_expiry = KotakNeoUserToken.objects.filter(expires_at__isnull=True)
    for token in tokens_without_expiry:
        token.expires_at = timezone.now() + timedelta(hours=24)
        token.save()


def reverse_fix_datetime_fields(apps, schema_editor):
    """Reverse migration - no action needed"""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('KOTAK_NEO_API', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(fix_datetime_fields, reverse_fix_datetime_fields),
    ] 