from django.test import TestCase
from knowledge.models import KnowledgeObject, RawFile, Chunk
from knowledge.embeddings import encode
from ingest.tasks import process_ingest


DOGS_TEXT = "Pes je domestikované zviera. Psy sú verní spoločníci človeka. " * 20
CATS_TEXT = "Mačka je nezávislé zviera. Mačky radi spia a loví myši. " * 20


class SearchViewTest(TestCase):

    def test_search_get_empty(self):
        """GET /search/ bez dotazu vráti 200 a prázdne výsledky."""
        response = self.client.get("/search/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<ol>")

    def test_search_no_results(self):
        """Dotaz keď DB je prázdna vráti prázdne výsledky."""
        response = self.client.get("/search/", {"q": "kvantová fyzika"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Žiadne výsledky")

    def test_search_returns_results(self):
        """Dotaz vráti chunky zoradené podľa sémantickej podobnosti."""
        ko = KnowledgeObject.objects.create(ko_type="podnet", title="Psy")
        RawFile.objects.create(ko=ko, filename="psy.txt", text=DOGS_TEXT)
        process_ingest(str(ko.id))

        response = self.client.get("/search/", {"q": "verný spoločník človeka"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pes")

    def test_search_closest_chunk_first(self):
        """Najrelevantnejší dokument je na prvom mieste."""
        ko_dogs = KnowledgeObject.objects.create(ko_type="podnet", title="Psy")
        RawFile.objects.create(ko=ko_dogs, filename="psy.txt", text=DOGS_TEXT)
        process_ingest(str(ko_dogs.id))

        ko_cats = KnowledgeObject.objects.create(ko_type="podnet", title="Mačky")
        RawFile.objects.create(ko=ko_cats, filename="macky.txt", text=CATS_TEXT)
        process_ingest(str(ko_cats.id))

        response = self.client.get("/search/", {"q": "mačka loví myši"})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        # Mačky musia byť skôr ako Psy
        self.assertLess(content.index("Mačky"), content.index("Psy"))


class EncodeTest(TestCase):

    def test_encode_returns_384_dims(self):
        """encode() vráti vektor s 384 dimenziami."""
        vec = encode("testovací text")
        self.assertEqual(len(vec), 384)

    def test_encode_returns_floats(self):
        """encode() vráti zoznam floatov."""
        vec = encode("ďalší text")
        self.assertTrue(all(isinstance(v, float) for v in vec))
