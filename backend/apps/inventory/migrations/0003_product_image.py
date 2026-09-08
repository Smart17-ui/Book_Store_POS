from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('inventory', '0002_create_missing_inventory'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='products/'),
        ),
    ]