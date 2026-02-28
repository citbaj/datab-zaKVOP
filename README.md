# PDRFlow

Systém na ingestovanie a vektorové ukladanie dokumentov. Dokumenty sa rozdeľujú na chunky, každý chunk dostane embedding (384-dimenzionálny vektor) a uloží sa do PostgreSQL s rozšírením pgvector pre neskoršie sémantické vyhľadávanie.

## Architektúra

```
ingest/      – wizard UI pre nahrávanie dokumentov + Celery tasky
knowledge/   – modely KnowledgeObject, RawFile, Chunk
pdrflow/     – Django konfigurácia projektu
```

### Dátový model

```
KnowledgeObject          – hlavný kontajner (typ, názov, metadata)
  └── RawFile            – surový text dokumentu
  └── Chunk              – textový úsek + 384-dim embedding (pgvector)
```

### Processing pipeline

```
POST /wizard/submit/
  → vytvorí KnowledgeObject + RawFile
  → Celery task process_ingest
      → RecursiveCharacterTextSplitter (chunk_size=500, overlap=50)
      → SentenceTransformer all-MiniLM-L6-v2 → 384-dim embeddingy
      → bulk INSERT do tabuľky Chunk
```

## Požiadavky

- Python 3.12
- Docker (PostgreSQL 16 + pgvector, Redis 7)

## Lokálne spustenie

### 1. Infraštruktúra

```bash
docker compose up -d
```

### 2. Prostredie

```bash
cp .env.example .env
# upravte .env podľa potreby
```

### 3. Závislosti

```bash
pip install -r requirements.txt
```

### 4. Migrácie

```bash
python manage.py migrate
```

### 5. Celery worker

```bash
celery -A pdrflow worker -l info
```

### 6. Django server

```bash
python manage.py runserver
```

Aplikácia je dostupná na `http://localhost:8000/wizard/`.

## Premenné prostredia

| Premenná | Popis | Predvolená hodnota |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | – |
| `REDIS_URL` | Redis URL pre Celery | `redis://localhost:6379/0` |
| `DJANGO_SECRET_KEY` | Django secret key | insecure default |
| `DJANGO_DEBUG` | Debug režim (`1`/`0`) | `1` |
| `DJANGO_ALLOWED_HOSTS` | Povolené hosty (čiarkou) | `127.0.0.1,localhost` |
| `DJANGO_TIME_ZONE` | Časová zóna | `Europe/Bratislava` |

## Testy

```bash
python manage.py test ingest
```

Testová sada (8 testov) overuje wizard views, spracovanie súborov, chunkovanie, rozmery embeddingov a edge cases.

## Typy dokumentov

| Hodnota | Popis |
|---|---|
| `podnet` | Podnet |
| `vyrocna` | Výročná správa |
| `list` | List |
| `tema` | Tématický súhrn |
