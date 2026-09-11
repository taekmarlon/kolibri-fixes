import kolibri.core.fields
import kolibri.utils.time_utils
import morango.models.fields.uuids
from django.db import migrations
from django.db import models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("kolibriauth", "0036_facilitydataset_theme_field"),
        ("coursework", "0004_add_learner_intervention"),
    ]

    operations = [
        migrations.CreateModel(
            name="Announcement",
            fields=[
                (
                    "id",
                    morango.models.fields.uuids.UUIDField(
                        editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "_morango_dirty_bit",
                    models.BooleanField(default=True, editable=False),
                ),
                ("_morango_source_id", models.CharField(editable=False, max_length=96)),
                (
                    "_morango_partition",
                    models.CharField(editable=False, max_length=128),
                ),
                ("title", models.CharField(max_length=200)),
                ("body", models.TextField()),
                (
                    "announcement_type",
                    models.CharField(
                        choices=[
                            ("general", "General Notice"),
                            ("event", "School Event"),
                            ("deped_memo", "DepEd Memorandum"),
                            ("urgent", "Urgent Bulletin"),
                        ],
                        default="general",
                        max_length=20,
                    ),
                ),
                (
                    "scope",
                    models.CharField(
                        choices=[
                            ("facility", "Facility-Wide"),
                            ("class", "Class-Level"),
                        ],
                        default="class",
                        max_length=10,
                    ),
                ),
                ("is_pinned", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "event_date",
                    kolibri.core.fields.DateTimeTzField(blank=True, null=True),
                ),
                (
                    "expiry_date",
                    kolibri.core.fields.DateTimeTzField(blank=True, null=True),
                ),
                ("link_url", models.URLField(blank=True, default="", max_length=500)),
                (
                    "date_created",
                    kolibri.core.fields.DateTimeTzField(
                        default=kolibri.utils.time_utils.local_now, editable=False
                    ),
                ),
                (
                    "date_modified",
                    kolibri.core.fields.DateTimeTzField(
                        default=kolibri.utils.time_utils.local_now
                    ),
                ),
                (
                    "collection",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="announcements",
                        to="kolibriauth.collection",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="announcements_created",
                        to="kolibriauth.facilityuser",
                    ),
                ),
                (
                    "dataset",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="kolibriauth.facilitydataset",
                    ),
                ),
            ],
            options={
                "ordering": ["-is_pinned", "-date_created"],
            },
        ),
    ]
