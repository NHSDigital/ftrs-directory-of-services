# FTRS-1891: Analiza i Rekomendacje - Queue Populator Single Service Testing

## Executive Summary

### Cel ticketu
Umożliwienie testowania pojedynczych serwisów przez Queue Populator Lambda bez konieczności uruchamiania pełnej synchronizacji (full sync). Dzięki temu możliwe będzie izolowane testowanie migracji konkretnych serwisów.

### Główne zmiany
Lambda `queue-populator` została rozszerzona o obsługę nowego typu eventu pozwalającego na uruchomienie migracji dla jednego konkretnego service ID.

---

## Analiza techniczna

### Architektura obecnego rozwiązania

#### Queue Populator Lambda
- **Nazwa**: `ftrs-dos-dev-data-migration-queue-populator-lambda-ftrs-1898`
- **Lokalizacja kodu**: `services/data-migration/src/queue_populator/lambda_handler.py`
- **Główne funkcje**:
  - `get_record_ids()` - pobiera IDs serwisów z bazy danych
  - `get_dms_event_batches()` - generuje batche DMSEvent messages
  - `send_message_batch()` - wysyła batche do SQS
  - `populate_sqs_queue()` - orkiestruje proces populacji kolejki
  - `lambda_handler()` - entry point Lambda

#### Przepływ danych
```
Database (pathwaysdos.services)
    ↓
Queue Populator Lambda
    ↓
SQS Queue (DMS Events)
    ↓
Processor Lambda (data migration)
    ↓
DynamoDB (transformed services)
```

### Implementacja FTRS-1891

#### Nowe typy eventów

**1. Single Service Event (NOWY)**
```python
class QueuePopulatorEvent(BaseModel):
    table_name: str
    service_id: int
    record_id: int
    full_sync: bool = False
    type_ids: list[int] | None = None
    status_ids: list[int] | None = None
```

**2. Full Sync Event (ISTNIEJĄCY)**
```python
class QueuePopulatorEvent(BaseModel):
    type_ids: list[int] | None = None
    status_ids: list[int] | None = None
    full_sync: bool = True
    service_id: int | None = None
    record_id: int | None = None
    table_name: str | None = None
```

#### Logika warunkowa
```python
# W get_record_ids():
if full_sync:
    # Stara logika: SELECT id FROM services WHERE type_id IN (...) AND status_id IN (...)
    stmt = select(Service.id)
    if config.type_ids:
        stmt = stmt.where(Service.typeid.in_(config.type_ids))
    if config.status_ids:
        stmt = stmt.where(Service.statusid.in_(config.status_ids))
else:
    # Nowa logika: SELECT id FROM services WHERE id = service_id
    stmt = select(Service.id).where(Service.id == config.service_id)
```

### Generowanie DMSEvent

Każdy rekord (niezależnie od typu synchronizacji) generuje DMSEvent:
```python
DMSEvent(
    type="dms_event",
    record_id=record_id,
    service_id=record_id,  # service_id = record_id dla tabeli services
    table_name="services",
    method="insert"         # zawsze "insert" dla queue populator
)
```

**Ważne**: Queue Populator **nie wykonuje** migracji - tylko wypełnia kolejkę eventami. Faktyczna migracja jest wykonywana przez Processor Lambda, który konsumuje wiadomości z SQS.

---

## Ryzyko i potencjalne problemy

### 1. Walidacja parametrów
**Ryzyko**: Brak service_id dla full_sync=false
**Mitygacja**: Pydantic BaseModel powinien walidować wymagane pola

### 2. Nieistniejący service ID
**Zachowanie**: Lambda zakończy się sukcesem, ale wyśle 0 wiadomości do SQS
**Czy OK?**: Tak, to akceptowalne zachowanie

### 3. Backward compatibility
**Ryzyko**: Zmiana może zepsuć istniejącą funkcjonalność full sync
**Mitygacja**: Test 4 weryfikuje backward compatibility

### 4. Concurrent executions
**Ryzyko**: Równoczesne uruchomienia dla tego samego service_id mogą powodować duplikaty
**Mitygacja**: SQS at-least-once delivery i idempotentność processora

### 5. EventBridge trigger
**Obserwacja**: EventBridge automatycznie wywołuje queue populator po zakończeniu DMS replication task
**Event structure**: Trzeba sprawdzić, czy EventBridge event jest zgodny z nową strukturą

---

## Zakres testowania

### Testy jednostkowe (już istnieją)
- ✅ `test_get_record_ids()` - podstawowe pobieranie IDs
- ✅ `test_get_record_ids_with_type_ids()` - filtrowanie po type_ids
- ✅ `test_get_record_ids_with_status_ids()` - filtrowanie po status_ids
- ✅ `test_get_dms_event_batches()` - generowanie batches
- ✅ `test_populate_sqs_queue()` - populacja kolejki
- ✅ `test_lambda_handler()` - integracja

### Testy manualne (do wykonania)
Zobacz: `FTRS-1891_Manual_Testing_Plan.md` i `FTRS-1891_Testing_Instructions_PL.md`

**6 głównych scenariuszy testowych**:
1. ✅ Single service - prawidłowy ID
2. ✅ Single service - nieistniejący ID
3. ✅ Walidacja parametrów (3 podtesty)
4. ✅ Full sync - backward compatibility
5. ✅ Multiple sequential invocations
6. ✅ Full sync - empty result set

---

## Rekomendacje testowe

### Pre-testing setup
1. Zweryfikuj workspace `ftrs-1898` jest aktywny
2. Sprawdź, czy developer już wdrożył kod do dev
3. Przygotuj listę test service IDs z bazy danych
4. Wyczyść SQS queue przed testami

### Sequence testów
1. **Test 2** (non-existent ID) - najprostszy, weryfikuje podstawowe działanie
2. **Test 1** (valid ID) - główna funkcjonalność
3. **Test 3** (validation) - error handling
4. **Test 6** (empty full sync) - edge case dla full sync
5. **Test 4** (full sync) - backward compatibility (może trwać długo!)
6. **Test 5** (sequential) - stress test

### Critical checkpoints
- CloudWatch Logs: DM_QP_000, DM_QP_001, DM_QP_999
- SQS message count MUSI się zgadzać z count w logach
- DMSEvent structure: type, record_id, service_id, table_name, method
- Brak błędów w Dead Letter Queue

---

## Post-testing actions

### Jeśli wszystkie testy PASS
1. Dokumentuj wyniki w Jira ticket FTRS-1891
2. Oznacz ticket jako "Ready for Review"
3. Powiadom developera o ukończonych testach
4. Zapisz screenshot'y z AWS Console (CloudWatch, SQS)

### Jeśli któryś test FAIL
1. Dokumentuj szczegóły błędu (screenshots, logs, error messages)
2. Sprawdź CloudWatch Logs dla dokładnego stack trace
3. Stwórz bug ticket (jeśli potrzebny) w stylu FTRS-1702
4. Przypisz z powrotem do developera z dokładnym opisem

---

## Kolejne kroki

### 1. Automated tests (przyszłość)
Po zakończeniu testów manualnych, rozważ:
- Stworzenie BDD feature file dla queue populator
- Użycie localstack do emulacji SQS w testach
- Integracja z istniejącymi pytest fixtures

### 2. Monitoring
- CloudWatch Alarms dla Lambda errors
- CloudWatch Metrics dla SQS queue depth
- X-Ray tracing dla end-to-end visibility

### 3. Documentation
- Zaktualizuj README z przykładami użycia single-service testing
- Dodaj runbook dla troubleshooting queue populator issues

---

## Przydatne informacje

### AWS Resources
- **Lambda**: ftrs-dos-dev-data-migration-queue-populator-lambda-ftrs-1898
- **Region**: eu-west-2
- **Workspace**: ftrs-1898
- **Database**: ftrs-dos-dev.pathwaysdos

### Code locations
```
services/data-migration/
├── src/
│   ├── queue_populator/
│   │   ├── lambda_handler.py          # Main logic
│   │   └── config.py                  # Configuration
│   └── common/
│       └── events.py                  # DMSEvent definition
└── tests/
    └── unit/
        └── queue_populator/
            └── test_queue_populator_lambda_handler.py  # Unit tests
```

### Related tickets
- FTRS-1898: Parent workspace ticket
- FTRS-1369: ServiceEndpoints trigger testing (poprzedni ticket)
- FTRS-1702: Bug discovered during FTRS-1369 testing

---

## Podsumowanie

FTRS-1891 dodaje istotną funkcjonalność umożliwiającą targeted testing pojedynczych serwisów bez konieczności uruchamiania full sync. Implementacja jest straightforward - rozszerzenie istniejącej logiki o obsługę warunku `full_sync=false` i pojedynczego `service_id`.

**Klucz do sukcesu testów**: Dokładna weryfikacja liczby wiadomości w SQS i struktura DMSEvent w każdym scenariuszu testowym.

**Szacowany czas testowania**: 1-2 godziny (w zależności od rozmiaru full sync w Test 4)

---

**Dokument utworzony**: 2025-01-10
**Branch**: task/FTRS-1891_single-service-queue-populator-testing
**Commit**: 1a5506a6

