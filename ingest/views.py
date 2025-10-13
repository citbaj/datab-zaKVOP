from django.shortcuts import render, redirect
from django.http import HttpRequest
from knowledge.models import KnowledgeObject
from .tasks import process_ingest

def wizard(request: HttpRequest):
    return render(request, "ingest/wizard.html", {})

def wizard_submit(request: HttpRequest):
    ko_type = request.POST.get("ko_type", "podnet")
    ko = KnowledgeObject.objects.create(ko_type=ko_type, title=request.POST.get("title",""))
    process_ingest.delay(str(ko.id))
    return redirect("wizard")
