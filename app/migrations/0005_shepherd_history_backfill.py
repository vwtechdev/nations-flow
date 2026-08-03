from django.db import migrations
from datetime import date


def create_initial_shepherd_history(apps, schema_editor):
    Church = apps.get_model("app", "Church")
    ShepherdHistory = apps.get_model("app", "ShepherdHistory")
    for church in Church.objects.select_related("shepherd").all():
        if church.shepherd and not ShepherdHistory.objects.filter(church=church).exists():
            ShepherdHistory.objects.create(
                church=church,
                shepherd=church.shepherd,
                start_date=church.created_at.date() if church.created_at else date.today(),
                end_date=None,
            )


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0004_contract_shepherdhistory"),
    ]

    operations = [
        migrations.RunPython(
            create_initial_shepherd_history,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
