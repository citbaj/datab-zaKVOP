from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpRequest
from pgvector.django import CosineDistance
from .models import Chunk
from .embeddings import encode

TOP_K = 10


@login_required
def search(request: HttpRequest):
    query = request.GET.get("q", "").strip()
    results = []
    if query:
        embedding = encode(query)
        results = (
            Chunk.objects
            .annotate(distance=CosineDistance("embedding", embedding))
            .order_by("distance")
            .select_related("ko")[:TOP_K]
        )
    return render(request, "knowledge/search.html", {"query": query, "results": results})
