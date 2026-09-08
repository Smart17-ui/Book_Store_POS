from django.db import migrations


def assign_legacy_records(apps, schema_editor):
    Client = apps.get_model('accounts', 'Client')
    Category = apps.get_model('inventory', 'Category')
    Product = apps.get_model('inventory', 'Product')
    client = Client.objects.filter(users__role__name='OWNER').first() or Client.objects.order_by('created_at').first()
    if client:
        Category.objects.filter(client__isnull=True).update(client=client)
        Product.objects.filter(client__isnull=True).update(client=client)


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0005_assign_legacy_users'),
        ('inventory', '0004_category_client_product_client'),
    ]

    operations = [
        migrations.RunPython(assign_legacy_records, migrations.RunPython.noop),
    ]