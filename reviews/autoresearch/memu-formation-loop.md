# Reduce duplicate/stale memory formation

project: memu
metric: lower redundancy with same or better recall
status: baseline captured against production memU contract
generated_at: 2026-03-13T23:05:36+00:00
base_url: https://api-production-86f5.up.railway.app
run_id: arugula-memu-d5c476baa996

## baseline summary
- health_ok: True
- write_read_recall_ok: True
- recall_rank: 1
- duplicate_ids_written: 2
- duplicate_results_found: 2
- duplicate_formation_detected: True
- total_memories_reported: 6727

## contract probes
- health: ok=True, status=200, latency_ms=197.5, path=/api/v1/memu/health
- recall_upsert: ok=True, status=200, latency_ms=167.9, path=/api/v1/memu/upsert
- recall_search: ok=True, status=200, latency_ms=378.9, path=/api/v1/memu/search
- duplicate_upsert_1: ok=True, status=200, latency_ms=167.7, path=/api/v1/memu/upsert
- duplicate_upsert_2: ok=True, status=200, latency_ms=118.3, path=/api/v1/memu/upsert
- duplicate_search: ok=True, status=200, latency_ms=361.8, path=/api/v1/memu/search

## observations
- Production health endpoint responded with {
  "db": "ok",
  "ok": true,
  "schema": "ok",
  "total_memories": 6727,
  "vector": "ok"
}
- Unique recall probe was written with id=6729; exact query returned 1 result(s).
- Exact write-to-read recall succeeded immediately at rank 1.
- Two identical writes produced ids [6730, 6731]; subsequent search surfaced 2 exact duplicate result(s).
- Duplicate formation is reproducible under the current contract; the store is not deduping exact repeated content on write.

## raw payload snapshots
### health
```json
{
  "db": "ok",
  "ok": true,
  "schema": "ok",
  "total_memories": 6727,
  "vector": "ok"
}
```

### recall_search
```json
{
  "count": 1,
  "memories": [
    {
      "content": "ARUGULA memU recall probe arugula-memu-d5c476baa996",
      "id": 6729,
      "metadata": {
        "agent": "ARUGULA",
        "run_id": "arugula-memu-d5c476baa996",
        "source": "arugula",
        "tags": [
          "arugula",
          "autoresearch",
          "recall-probe",
          "arugula-memu-d5c476baa996"
        ],
        "ts": "2026-03-13T23:05:36+00:00"
      },
      "score": 0.10000000149011612
    }
  ],
  "ok": true,
  "results": [
    {
      "content": "ARUGULA memU recall probe arugula-memu-d5c476baa996",
      "id": 6729,
      "metadata": {
        "agent": "ARUGULA",
        "run_id": "arugula-memu-d5c476baa996",
        "source": "arugula",
        "tags": [
          "arugula",
          "autoresearch",
          "recall-probe",
          "arugula-memu-d5c476baa996"
        ],
        "ts": "2026-03-13T23:05:36+00:00"
      },
      "score": 0.10000000149011612
    }
  ]
}
```

### duplicate_search
```json
{
  "count": 2,
  "memories": [
    {
      "content": "ARUGULA memU duplicate probe arugula-memu-d5c476baa996",
      "id": 6731,
      "metadata": {
        "agent": "ARUGULA",
        "run_id": "arugula-memu-d5c476baa996",
        "source": "arugula",
        "tags": [
          "arugula",
          "autoresearch",
          "duplicate-probe",
          "arugula-memu-d5c476baa996"
        ],
        "ts": "2026-03-13T23:05:36+00:00"
      },
      "score": 0.10000000149011612
    },
    {
      "content": "ARUGULA memU duplicate probe arugula-memu-d5c476baa996",
      "id": 6730,
      "metadata": {
        "agent": "ARUGULA",
        "run_id": "arugula-memu-d5c476baa996",
        "source": "arugula",
        "tags": [
          "arugula",
          "autoresearch",
          "duplicate-probe",
          "arugula-memu-d5c476baa996"
        ],
        "ts": "2026-03-13T23:05:36+00:00"
      },
      "score": 0.10000000149011612
    }
  ],
  "ok": true,
  "results": [
    {
      "content": "ARUGULA memU duplicate probe arugula-memu-d5c476baa996",
      "id": 6731,
      "metadata": {
        "agent": "ARUGULA",
        "run_id": "arugula-memu-d5c476baa996",
        "source": "arugula",
        "tags": [
          "arugula",
          "autoresearch",
          "duplicate-probe",
          "arugula-memu-d5c476baa996"
        ],
        "ts": "2026-03-13T23:05:36+00:00"
      },
      "score": 0.10000000149011612
    },
    {
      "content": "ARUGULA memU duplicate probe arugula-memu-d5c476baa996",
      "id": 6730,
      "metadata": {
        "agent": "ARUGULA",
        "run_id": "arugula-memu-d5c476baa996",
        "source": "arugula",
        "tags": [
          "arugula",
          "autoresearch",
          "duplicate-probe",
          "arugula-memu-d5c476baa996"
        ],
        "ts": "2026-03-13T23:05:36+00:00"
      },
      "score": 0.10000000149011612
    }
  ]
}
```

## next steps
- Formation is currently append-only for identical payloads. Add duplicate suppression or content hashing before promotion.
- Write-to-read recall succeeded immediately. Track this as the minimum production proof gate before shipping retrieval changes.
- Prioritize pre-insert duplicate checks and stale-memory consolidation before touching ranking weights.
- Keep this exact probe packet as the production proof gate for future memU ARUGULA runs.
