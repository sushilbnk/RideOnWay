# Generated by Django 5.0.3 on 2024-03-23 14:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RideOnWay', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RideSourceDestinationDetails',
            fields=[
                ('source', models.CharField(max_length=200)),
                ('destination', models.CharField(max_length=200)),
                ('sourceDestinationId', models.AutoField(primary_key=True, serialize=False)),
                ('isRideAvailable', models.BooleanField()),
                ('ride', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='RideOnWay.ridedetails')),
            ],
        ),
    ]