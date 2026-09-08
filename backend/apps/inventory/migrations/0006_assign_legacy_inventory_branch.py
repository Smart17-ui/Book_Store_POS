from django.db import migrations


def assign_legacy_inventory_branch(apps, schema_editor):
    Branch = apps.get_model('accounts', 'Branch')
    Inventory = apps.get_model('inventory', 'Inventory')
    branch = Branch.objects.filter(client__users__role__name='OWNER', is_active=True).order_by('name').first()
    if not branch:
        branch = Branch.objects.filter(is_active=True).order_by('created_at').first()
    if branch:
        Inventory.objects.filter(branch__isnull=True).update(branch=branch)


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0005_assign_legacy_users'),
        ('inventory', '0005_assign_legacy_records'),
    ]

    operations = [
        migrations.RunPython(assign_legacy_inventory_branch, migrations.RunPython.noop),
    ]