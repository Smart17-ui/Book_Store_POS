from django.db import migrations


def assign_legacy_customers(apps, schema_editor):
    Client = apps.get_model('accounts', 'Client')
    Customer = apps.get_model('sales', 'Customer')
    client = Client.objects.filter(users__role__name='OWNER').first() or Client.objects.order_by('created_at').first()
    if client:
        Customer.objects.filter(client__isnull=True).update(client=client)


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0005_assign_legacy_users'),
        ('sales', '0002_customer_client'),
    ]

    operations = [
        migrations.RunPython(assign_legacy_customers, migrations.RunPython.noop),
    ]