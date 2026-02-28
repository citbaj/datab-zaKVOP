from celery import shared_task
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from knowledge.models import KnowledgeObject, Chunk

_model = None

def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

@shared_task
def process_ingest(job_id: str):
    ko = KnowledgeObject.objects.get(id=job_id)
    raw_files = ko.raw_files.all()
    if not raw_files.exists():
        print(f"[process_ingest] job_id={job_id} -> žiadne raw súbory, preskakujem")
        return

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    model = _get_model()

    chunks_to_create = []
    ordinal = 1
    for raw_file in raw_files:
        if not raw_file.text:
            continue
        texts = splitter.split_text(raw_file.text)
        embeddings = model.encode(texts, show_progress_bar=False)
        for text, embedding in zip(texts, embeddings):
            chunks_to_create.append(Chunk(
                ko=ko,
                ordinal=ordinal,
                text=text,
                embedding=embedding.tolist(),
                meta={"source": raw_file.filename},
            ))
            ordinal += 1

    Chunk.objects.bulk_create(chunks_to_create)
    print(f"[process_ingest] job_id={job_id} -> {len(chunks_to_create)} chunkov vytvorených")
