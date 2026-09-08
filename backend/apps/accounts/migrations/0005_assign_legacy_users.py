from django.db import migrations


def assign_legacy_users(apps, schema_editor):
    Client = apps.get_model('accounts', 'Client')
    User = apps.get_model('accounts', 'User')
    client = Client.objects.filter(users__role__name='OWNER').first() or Client.objects.order_by('created_at').first()
    if client:
        User.objects.filter(client__isnull=True).update(client=client)


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0004_sessiontoken'),
    ]

    operations = [
        migrations.RunPython(assign_legacy_users, migrations.RunPython.noop),
    ]