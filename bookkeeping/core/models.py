from django.db import models

class SourceDocument(models.Model):
    document_type = models.CharField(max_length=50)
    reference_number = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    journal_entry = models.ForeignKey(
        "django_ledger.JournalEntryModel",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="source_documents",
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("DRAFT", "Draft"),
            ("POSTED", "Posted"),
            ("PAID", "Paid"),
        ],
        default="DRAFT",
    )
