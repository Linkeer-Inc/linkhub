from django.db import migrations, models
import uuid
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = False

    dependencies = [
        ('links', '0007_link_emphasis_alter_link_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='LinkClick',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('payload', models.JSONField(null=True, blank=True)),
                ('referrer', models.URLField(max_length=2000, null=True, blank=True)),
                ('user_agent', models.TextField(null=True, blank=True)),
                ('client_x', models.IntegerField(null=True, blank=True)),
                ('client_y', models.IntegerField(null=True, blank=True)),
                ('viewport_width', models.IntegerField(null=True, blank=True)),
                ('viewport_height', models.IntegerField(null=True, blank=True)),
                ('ip_address', models.GenericIPAddressField(null=True, blank=True)),
                ('link', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clicks', to='links.link')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]
