from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Booking",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=200)),
                ("reservation_date", models.DateField()),
                ("reservation_slot", models.PositiveSmallIntegerField()),
            ],
            options={
                "ordering": ["reservation_date", "reservation_slot"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("reservation_date", "reservation_slot"),
                        name="unique_reservation_date_and_slot",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="Menu",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("price", models.DecimalField(decimal_places=2, max_digits=6)),
                (
                    "menu_item_description",
                    models.TextField(default="", max_length=1000),
                ),
            ],
        ),
    ]
