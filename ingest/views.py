from django.shortcuts import render, redirect
from django.http import HttpRequest
from knowledge.models import KnowledgeObject, RawFile
from .parsers import extract_text
from .tasks import process_ingest


def wizard(request: HttpRequest):
    return render(request, "ingest/wizard.html", {})


def wizard_submit(request: HttpRequest):
    ko_type = request.POST.get("ko_type", "podnet")
    ko = KnowledgeObject.objects.create(ko_type=ko_type, title=request.POST.get("title", ""))

    uploaded_file = request.FILES.get("file")
    if uploaded_file:
        file_bytes = uploaded_file.read()
        filename = uploaded_file.name
        content_type = uploaded_file.content_type or "text/plain"
        text = extract_text(file_bytes, filename, content_type)
    else:
        text = request.POST.get("text", "").strip()
        filename = "manual_input.txt"
        content_type = "text/plain"

    if text:
        RawFile.objects.create(ko=ko, filename=filename, content_type=content_type, text=text)
        process_ingest.delay(str(ko.id))

    return redirect("wizard")
