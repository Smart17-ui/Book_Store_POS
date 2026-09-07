from django.db import migrations


def create_missing_inventory(apps, schema_editor):
    Product = apps.get_model('inventory', 'Product')
    Inventory = apps.get_model('inventory', 'Inventory')
    for product in Product.objects.all():
        Inventory.objects.get_or_create(product=product)


class Migration(migrations.Migration):
    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_missing_inventory, migrations.RunPython.noop),
    ]
