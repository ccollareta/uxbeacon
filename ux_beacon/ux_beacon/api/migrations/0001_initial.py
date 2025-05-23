# Generated by Django 4.2.19 on 2025-03-04 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WCAGReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=20)),
                ('website_url', models.URLField()),
                ('readability_score', models.CharField(blank=True, max_length=50, null=True)),
                ('missing_alt_text', models.IntegerField(default=0)),
                ('heading_structure', models.JSONField(default=dict)),
                ('contrast_issues', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('pdf_report_path', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
    ]
