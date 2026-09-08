from django.db import migrations


def create_default_branches(apps, schema_editor):
    Client = apps.get_model('accounts', 'Client')
    Branch = apps.get_model('accounts', 'Branch')
    for client in Client.objects.all():
        Branch.objects.get_or_create(
            client=client,
            code='MAIN',
            defaults={'name': 'Main branch', 'address': ''},
        )


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0005_assign_legacy_users'),
    ]

    operations = [
        migrations.RunPython(create_default_branches, migrations.RunPython.noop),
    ]