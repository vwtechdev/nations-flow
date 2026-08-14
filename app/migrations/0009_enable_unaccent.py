from django.db import migrations


def enable_unaccent(apps, schema_editor):
    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.execute('CREATE EXTENSION IF NOT EXISTS unaccent')


def disable_unaccent(apps, schema_editor):
    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.execute('DROP EXTENSION IF EXISTS unaccent')


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_user_is_owner'),
    ]

    operations = [
        migrations.RunPython(enable_unaccent, disable_unaccent),
    ]
