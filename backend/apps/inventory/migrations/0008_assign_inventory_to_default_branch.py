from django.db import migrations


def assign_inventory(apps, schema_editor):
    Branch = apps.get_model('accounts', 'Branch')
    Inventory = apps.get_model('inventory', 'Inventory')
    for branch in Branch.objects.all():
        Inventory.objects.filter(branch__isnull=True, product__client_id=branch.client_id).update(branch=branch)


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0006_create_default_branches'),
        ('inventory', '0007_inventory_branch'),
    ]

    operations = [
        migrations.RunPython(assign_inventory, migrations.RunPython.noop),
    ]