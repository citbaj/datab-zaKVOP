from celery import shared_task

@shared_task
def process_ingest(job_id: str):
    # TODO: extrakcia -> LLM normalizácia -> chunking -> embedding/index
    # Zatiaľ len log placeholder:
    print(f"[process_ingest] job_id={job_id}")
