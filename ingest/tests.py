import io
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from knowledge.models import KnowledgeObject, RawFile, Chunk
from ingest.tasks import process_ingest


SAMPLE_TEXT = (
    "Toto je testovací dokument. " * 30  # dostatočne dlhý text na viac chunkov
)


class WizardViewTest(TestCase):

    def test_wizard_get(self):
        """Wizard stránka sa načíta."""
        response = self.client.get("/wizard/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ko_type")

    def test_wizard_submit_text(self):
        """POST s textom vytvorí KO, RawFile a presmeruje."""
        response = self.client.post("/wizard/submit/", {
            "ko_type": "podnet",
            "title": "Testovací podnet",
            "text": SAMPLE_TEXT,
        })
        self.assertRedirects(response, "/wizard/", fetch_redirect_response=False)
        ko = KnowledgeObject.objects.get(ko_type="podnet", title="Testovací podnet")
        self.assertEqual(ko.raw_files.count(), 1)
        rf = ko.raw_files.first()
        self.assertEqual(rf.text, SAMPLE_TEXT.strip())
        self.assertEqual(rf.filename, "manual_input.txt")

    def test_wizard_submit_file_upload(self):
        """POST so súborom uloží text zo súboru do RawFile."""
        content = ("Obsah nahratého súboru. " * 20).encode("utf-8")
        response = self.client.post("/wizard/submit/", {
            "ko_type": "list",
            "title": "",
            "file": io.BytesIO(content),
        }, format="multipart")
        # Skontrolujeme že KO vznikol
        ko = KnowledgeObject.objects.filter(ko_type="list").first()
        self.assertIsNotNone(ko)
        rf = ko.raw_files.first()
        self.assertIsNotNone(rf)
        self.assertIn("Obsah nahratého súboru", rf.text)

    def test_wizard_submit_no_text_no_file(self):
        """POST bez textu nevytvorí RawFile ani nespustí task."""
        response = self.client.post("/wizard/submit/", {
            "ko_type": "tema",
            "title": "Bez obsahu",
        })
        ko = KnowledgeObject.objects.get(ko_type="tema", title="Bez obsahu")
        self.assertEqual(ko.raw_files.count(), 0)
        self.assertEqual(ko.chunks.count(), 0)


class ProcessIngestTaskTest(TestCase):

    def test_real_chunking_and_embedding(self):
        """process_ingest rozdeľuje text a generuje reálne embeddingy."""
        ko = KnowledgeObject.objects.create(ko_type="podnet", title="Test ingest")
        RawFile.objects.create(
            ko=ko,
            filename="test.txt",
            content_type="text/plain",
            text=SAMPLE_TEXT,
        )

        # Spustíme task priamo (synchronne, nie cez Celery)
        process_ingest(str(ko.id))

        chunks = list(Chunk.objects.filter(ko=ko).order_by("ordinal"))
        self.assertGreater(len(chunks), 1, "Očakávame viac ako 1 chunk")

        for i, chunk in enumerate(chunks):
            self.assertIsNotNone(chunk.embedding, f"Chunk {i} nemá embedding")
            self.assertEqual(len(chunk.embedding), 384, f"Chunk {i} má zlý rozmer embeddingu")
            self.assertTrue(chunk.text.strip(), f"Chunk {i} má prázdny text")
            self.assertEqual(chunk.ordinal, i + 1)
            self.assertEqual(chunk.meta["source"], "test.txt")

    def test_no_raw_file_creates_no_chunks(self):
        """Ak neexistuje RawFile, task nič nevytvorí."""
        ko = KnowledgeObject.objects.create(ko_type="list", title="Prázdny KO")
        process_ingest(str(ko.id))
        self.assertEqual(ko.chunks.count(), 0)

    def test_empty_text_creates_no_chunks(self):
        """RawFile s prázdnym textom neprodukuje žiadne chunky."""
        ko = KnowledgeObject.objects.create(ko_type="vyrocna", title="Prázdny text")
        RawFile.objects.create(ko=ko, filename="empty.txt", text="")
        process_ingest(str(ko.id))
        self.assertEqual(ko.chunks.count(), 0)

    def test_chunk_ordinals_are_sequential(self):
        """Chunky majú sekvenčné ordinal hodnoty od 1."""
        ko = KnowledgeObject.objects.create(ko_type="tema", title="Sekvenčný test")
        RawFile.objects.create(ko=ko, filename="seq.txt", text=SAMPLE_TEXT)
        process_ingest(str(ko.id))
        chunks = Chunk.objects.filter(ko=ko).order_by("ordinal")
        ordinals = [c.ordinal for c in chunks]
        self.assertEqual(ordinals, list(range(1, len(ordinals) + 1)))
