from collections import Counter

from django.db import migrations, models


def populate_unit_syllabus_page(apps, schema_editor):
    Unit = apps.get_model('pastpaper', 'Unit')
    Question = apps.get_model('pastpaper', 'Question')

    for unit in Unit.objects.all():
        spages = list(
            Question.objects.filter(unit_id=unit.id)
            .exclude(spage__isnull=True)
            .values_list('spage', flat=True)
        )
        if not spages:
            continue
        counter = Counter(spages)
        unit.syllabus_page = counter.most_common(1)[0][0]
        unit.save(update_fields=['syllabus_page'])


class Migration(migrations.Migration):

    dependencies = [
        ('pastpaper', '0003_alter_usertag_save_rename_save_usertag_saved'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='syllabus_page',
            field=models.IntegerField(default=1, verbose_name='大纲页码'),
        ),
        migrations.RunPython(populate_unit_syllabus_page, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='question',
            name='spage',
        ),
    ]
