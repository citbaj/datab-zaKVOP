from celery import shared_task
from knowledge.models import KnowledgeObject, Chunk

@shared_task
def process_ingest(job_id: str):
    ko = KnowledgeObject.objects.get(id=job_id)
    text = f"KO {ko.id} ({ko.ko_type}) – dummy chunk pre E2E test."
    Chunk.objects.create(ko=ko, ordinal=1, text=text, embedding=None, meta={"source":"dummy"})
    print(f"[process_ingest] job_id={job_id} -> chunk created")
