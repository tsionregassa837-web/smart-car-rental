from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0025_booking_pickup_fuel_level_booking_pickup_mileage_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="return_fuel_level",
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name="booking",
            name="return_mileage",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="booking",
            name="return_notes",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="ExtraCharge",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("charge_type", models.CharField(choices=[("Damage", "Damage"), ("Fuel", "Fuel"), ("Late Return", "Late Return"), ("Cleaning", "Cleaning"), ("Other", "Other")], max_length=30)),
                ("description", models.CharField(max_length=255)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("booking", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="extra_charges", to="core.booking")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="rental_extra_charges", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="RentalInspection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("inspection_type", models.CharField(choices=[("Pickup", "Pickup"), ("Return", "Return")], max_length=10)),
                ("mileage", models.PositiveIntegerField()),
                ("fuel_level", models.CharField(choices=[("Empty", "Empty"), ("1/4", "1/4"), ("1/2", "1/2"), ("3/4", "3/4"), ("Full", "Full")], max_length=10)),
                ("notes", models.TextField(blank=True)),
                ("damage_found", models.BooleanField(default=False)),
                ("damage_description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("booking", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="inspections", to="core.booking")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="rental_inspections", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["inspection_type", "-created_at"]},
        ),
        migrations.AddConstraint(
            model_name="rentalinspection",
            constraint=models.UniqueConstraint(fields=("booking", "inspection_type"), name="unique_booking_inspection_type"),
        ),
    ]
