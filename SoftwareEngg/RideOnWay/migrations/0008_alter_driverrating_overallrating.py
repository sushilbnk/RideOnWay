# Generated by Django 5.0.3 on 2024-03-31 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RideOnWay', '0007_alter_ridedetails_relatedrideid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driverrating',
            name='overallRating',
            field=models.IntegerField(default=0),
        ),
    ]
