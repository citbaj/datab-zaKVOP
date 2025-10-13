from django.db import models
from pgvector.django import VectorField

class KnowledgeObject(models.Model):
    KO_TYPES = [
        ('podnet', 'Podnet'),
        ('vyrocna', 'Výročná správa'),
        ('list', 'List'),
        ('tema', 'Tématický súhrn'),
    ]
    ko_type = models.CharField(max_length=20, choices=KO_TYPES)
    title = models.CharField(max_length=300, blank=True, default="")
    confidence = models.FloatField(default=0.0)
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class RawFile(models.Model):
    ko = models.ForeignKey(KnowledgeObject, on_delete=models.CASCADE, related_name='raw_files')
    filename = models.CharField(max_length=300)
    content_type = models.CharField(max_length=100, blank=True, default="")
    text = models.TextField(blank=True, default="")
    payload = models.JSONField(default=dict, blank=True)  # audit/extrakt raw
    created_at = models.DateTimeField(auto_now_add=True)

class Chunk(models.Model):
    ko = models.ForeignKey(KnowledgeObject, on_delete=models.CASCADE, related_name='chunks')
    ordinal = models.IntegerField()
    text = models.TextField()
    embedding = VectorField(dimensions=384, null=True)  # MiniLM-L6-v2 = 384
    meta = models.JSONField(default=dict, blank=True)
    class Meta:
        indexes = [models.Index(fields=['ko', 'ordinal'])]
