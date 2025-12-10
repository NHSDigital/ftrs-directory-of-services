# FTRS-1891: Instrukcje Testów Manualnych - Queue Populator

## Przegląd
Ten dokument zawiera szczegółowe instrukcje krok po kroku do wykonania testów manualnych dla FTRS-1891.

## Przygotowanie Środowiska

### Krok 1: Weryfikacja dostępu do AWS
1. Zaloguj się do AWS Console
2. Upewnij się, że jesteś w regionie **eu-west-2** (London)
3. Zweryfikuj dostęp do:
   - AWS Lambda
   - Amazon SQS
   - CloudWatch Logs
   - RDS (dostęp do bazy danych)

### Krok 2: Identyfikacja zasobów
1. **Lambda Function**:
   - Nazwa: `ftrs-dos-dev-data-migration-queue-populator-lambda-ftrs-1898`
   - Znajdź tę funkcję w AWS Lambda Console

2. **SQS Queue**:
   - Otwórz Lambda function w konsoli
   - Przejdź do zakładki "Configuration" → "Environment variables"
   - Znajdź zmienną `SQS_QUEUE_URL` i zapisz jej wartość

3. **Database**:
   - Database: `ftrs-dos-dev`
   - Schema: `pathwaysdos`
   - Table: `services`

### Krok 3: Przygotowanie danych testowych
1. Połącz się z bazą danych `ftrs-dos-dev`
2. Wykonaj zapytanie, aby znaleźć istniejące service IDs:

```sql
-- Znajdź aktywny serwis do testów
SELECT id, name, typeid, statusid
FROM pathwaysdos.services
WHERE statusid = 1
LIMIT 10;
```

3. Zapisz kilka service IDs do testów (np. 12345, 12346, 12347)

---

## Test 1: Single Service Event - Prawidłowy Service ID

### Cel
Sprawdzenie, czy queue populator poprawnie przetwarza pojedynczy serwis.

### Krok po kroku

#### 1.1 Przygotowanie
```sql
-- Sprawdź, czy serwis istnieje w bazie
SELECT id, name, typeid, statusid
FROM pathwaysdos.services
WHERE id = 12345;  -- Użyj prawdziwego ID z Kroku 3
```

#### 1.2 Wyczyść kolejkę SQS (opcjonalne, ale zalecane)
1. Otwórz SQS Queue w AWS Console
2. Zanotuj aktualną liczbę wiadomości w kolejce
3. Jeśli chcesz zacząć od czystej kolejki:
   - Kliknij "Send and receive messages"
   - Przejdź do zakładki "Poll for messages"
   - Kliknij "Start polling"
   - Usuń wszystkie testowe wiadomości (jeśli są)

#### 1.3 Wywołaj Lambda function
1. Otwórz Lambda function: `ftrs-dos-dev-data-migration-queue-populator-lambda-ftrs-1898`
2. Kliknij zakładkę "Test"
3. Kliknij "Create new event" lub wybierz istniejący event
4. Wpisz nazwę event: `Test1-SingleService-Valid`
5. Wklej poniższy JSON (zamień 12345 na prawdziwy service ID):

```json
{
  "table_name": "services",
  "service_id": 12345,
  "record_id": 12345,
  "full_sync": false,
  "type_ids": null,
  "status_ids": null
}
```

6. Kliknij "Save"
7. Kliknij "Test"

#### 1.4 Weryfikacja wykonania Lambda
1. Poczekaj na zakończenie wykonania (kilka sekund)
2. Sprawdź status wykonania:
   - **Expected**: "Execution result: succeeded" (zielony banner)
   - **Execution duration**: kilka sekund
   - **Memory used**: sprawdź czy nie ma problemów z pamięcią

3. Kliknij "View CloudWatch logs"

#### 1.5 Weryfikacja logów CloudWatch
Sprawdź, czy w logach znajdują się następujące wpisy:

```
✅ DM_QP_000: "Starting Data Migration Queue Populator"
   - Powinien zawierać: "type_ids": null, "status_ids": null

✅ DM_QP_001: [liczba znalezionych rekordów]
   - Expected: "count": 1
   - Expected: queue_url zawiera URL kolejki SQS

✅ DM_QP_999: "Data Migration Queue Populator completed"
```

#### 1.6 Weryfikacja kolejki SQS
1. Wróć do SQS Queue w AWS Console
2. Odśwież stronę
3. Sprawdź:
   - **Messages Available**: powinno wzrosnąć o 1
   - Kliknij "Send and receive messages"
   - Kliknij "Poll for messages"
   - Powinieneś zobaczyć 1 nową wiadomość

#### 1.7 Weryfikacja zawartości wiadomości SQS
1. Kliknij na wiadomość, aby ją otworzyć
2. Sprawdź "Body" wiadomości
3. Zweryfikuj strukturę JSON:

```json
{
  "type": "dms_event",
  "record_id": 12345,      // Twoje service ID
  "service_id": 12345,     // Twoje service ID
  "table_name": "services",
  "method": "insert"
}
```

4. **Nie usuwaj** tej wiadomości jeszcze - będzie potrzebna do weryfikacji

### Wynik Test 1
- [ ] Lambda wykonała się bez błędów
- [ ] CloudWatch Logs zawierają DM_QP_000, DM_QP_001 (count=1), DM_QP_999
- [ ] SQS queue zawiera dokładnie 1 nową wiadomość
- [ ] Wiadomość SQS ma poprawną strukturę DMSEvent
- [ ] service_id i record_id w wiadomości są prawidłowe

**Status**: ✅ PASS / ❌ FAIL
**Notatki**: _____________________

---

## Test 2: Single Service Event - Nieistniejący Service ID

### Cel
Sprawdzenie, czy Lambda poprawnie obsługuje nieistniejący service ID (brak błędów, 0 wiadomości w kolejce).

### Krok po kroku

#### 2.1 Weryfikacja, że service ID nie istnieje
```sql
-- Sprawdź, że ten service ID NIE istnieje
SELECT id FROM pathwaysdos.services WHERE id = 999999999;
-- Powinno zwrócić 0 rows
```

#### 2.2 Zanotuj stan kolejki SQS
1. Otwórz SQS Queue
2. Zapisz aktualną liczbę wiadomości: **______**

#### 2.3 Wywołaj Lambda function
1. Otwórz Lambda function
2. Zakładka "Test"
3. Kliknij "Edit" przy event lub "Create new event"
4. Nazwa: `Test2-SingleService-NotFound`
5. Event JSON:

```json
{
  "table_name": "services",
  "service_id": 999999999,
  "record_id": 999999999,
  "full_sync": false,
  "type_ids": null,
  "status_ids": null
}
```

6. Save i Test

#### 2.4 Weryfikacja wykonania
1. Lambda powinna zakończyć się sukcesem (status: succeeded)
2. Sprawdź CloudWatch Logs:
   - DM_QP_000: "Starting..."
   - DM_QP_001: **"count": 0** ← To jest kluczowe!
   - DM_QP_999: "...completed"
3. NIE powinno być żadnych błędów ani exception

#### 2.5 Weryfikacja kolejki SQS
1. Odśwież SQS Queue
2. Liczba wiadomości powinna pozostać **bez zmian** (żadne nowe wiadomości)

### Wynik Test 2
- [ ] Lambda wykonała się bez błędów
- [ ] CloudWatch Logs pokazują count=0
- [ ] SQS queue nie zawiera nowych wiadomości
- [ ] Brak błędów w logach

**Status**: ✅ PASS / ❌ FAIL
**Notatki**: _____________________

---

## Test 3: Single Service Event - Brakujące Parametry

### Cel
Sprawdzenie walidacji wymaganych parametrów.

### Test 3a: Brakujące service_id

#### 3a.1 Wywołaj Lambda z niepełnym eventem
1. Nazwa event: `Test3a-Missing-ServiceId`
2. Event JSON:

```json
{
  "table_name": "services",
  "record_id": 12345,
  "full_sync": false,
  "type_ids": null,
  "status_ids": null
}
```

3. Kliknij Test

#### 3a.2 Weryfikacja
1. Lambda powinna zwrócić **błąd walidacji**
2. Sprawdź Response/Error:
   - Powinien zawierać informację o brakującym polu
3. CloudWatch Logs:
   - Sprawdź błąd walidacji
4. SQS Queue:
   - Nie powinno być nowych wiadomości

### Test 3b: Brakujące record_id

#### 3b.1 Wywołaj Lambda
1. Nazwa: `Test3b-Missing-RecordId`
2. Event JSON:

```json
{
  "table_name": "services",
  "service_id": 12345,
  "full_sync": false,
  "type_ids": null,
  "status_ids": null
}
```

3. Test

#### 3b.2 Weryfikacja
Analogicznie jak w 3a.2 - spodziewany błąd walidacji.

### Test 3c: Brakujące table_name

#### 3c.1 Wywołaj Lambda
1. Nazwa: `Test3c-Missing-TableName`
2. Event JSON:

```json
{
  "service_id": 12345,
  "record_id": 12345,
  "full_sync": false,
  "type_ids": null,
  "status_ids": null
}
```

3. Test

#### 3c.2 Weryfikacja
Analogicznie - spodziewany błąd walidacji.

### Wynik Test 3
- [ ] Test 3a: Lambda zwróciła błąd walidacji dla brakującego service_id
- [ ] Test 3b: Lambda zwróciła błąd walidacji dla brakującego record_id
- [ ] Test 3c: Lambda zwróciła błąd walidacji dla brakującego table_name
- [ ] Żadne wiadomości nie trafiły do SQS queue

**Status**: ✅ PASS / ❌ FAIL
**Notatki**: _____________________

---

## Test 4: Full Sync Event - Kompatybilność wsteczna

### Cel
Sprawdzenie, że istniejąca funkcjonalność full sync nadal działa poprawnie.

### Krok po kroku

#### 4.1 Znajdź serwisy do full sync
```sql
-- Policz serwisy spełniające kryteria
SELECT COUNT(*) as total_count
FROM pathwaysdos.services
WHERE statusid = 1 AND typeid = 100;

-- Zapisz liczbę: __________
```

#### 4.2 Wyczyść kolejkę SQS
1. Usuń wszystkie testowe wiadomości z poprzednich testów
2. Upewnij się, że queue jest pusty (Messages Available = 0)

#### 4.3 Wywołaj Lambda z full sync event
1. Nazwa: `Test4-FullSync-BackwardCompatibility`
2. Event JSON:

```json
{
  "status_ids": [1],
  "type_ids": [100],
  "full_sync": true,
  "record_id": null,
  "service_id": null,
  "table_name": "services"
}
```

3. **UWAGA**: Ten test może trwać dłużej jeśli jest dużo serwisów!
4. Kliknij Test

#### 4.4 Weryfikacja wykonania
1. Lambda powinna zakończyć się sukcesem
2. CloudWatch Logs:
   - DM_QP_000: powinien zawierać "type_ids": [100], "status_ids": [1]
   - DM_QP_001: "count" powinno być równe liczbie z zapytania SQL w kroku 4.1
   - DM_QP_999: "...completed"

#### 4.5 Weryfikacja kolejki SQS
1. Odśwież SQS Queue
2. **Messages Available** powinno być równe liczbie serwisów z kroku 4.1
3. Poll for messages i sprawdź kilka wiadomości:
   - Każda powinna mieć strukturę DMSEvent
   - service_id i record_id powinny być różne w każdej wiadomości
   - Wszystkie powinny mieć table_name="services" i method="insert"

### Wynik Test 4
- [ ] Lambda wykonała się bez błędów
- [ ] Liczba wiadomości w SQS = liczba serwisów z zapytania SQL
- [ ] CloudWatch Logs pokazują poprawną liczbę w DM_QP_001
- [ ] Przykładowe wiadomości SQS mają poprawną strukturę
- [ ] Full sync nadal działa jak poprzednio

**Status**: ✅ PASS / ❌ FAIL
**Liczba wiadomości expected**: __________
**Liczba wiadomości actual**: __________
**Notatki**: _____________________

---

## Test 5: Multiple Sequential Invocations

### Cel
Sprawdzenie, czy Lambda poprawnie obsługuje wiele kolejnych wywołań dla różnych service IDs.

### Krok po kroku

#### 5.1 Przygotowanie
```sql
-- Znajdź 3 różne service IDs
SELECT id FROM pathwaysdos.services WHERE statusid = 1 LIMIT 3;
-- Zapisz IDs:
-- ID1: __________
-- ID2: __________
-- ID3: __________
```

#### 5.2 Wyczyść kolejkę SQS
Usuń wszystkie wiadomości, zacznij od Messages Available = 0

#### 5.3 Wywołanie #1
1. Nazwa: `Test5-Sequential-Service1`
2. Event JSON (użyj ID1):

```json
{
  "table_name": "services",
  "service_id": [ID1],
  "record_id": [ID1],
  "full_sync": false,
  "type_ids": null,
  "status_ids": null
}
```

3. Kliknij Test
4. Poczekaj na zakończenie (succeeded)
5. Sprawdź SQS: Messages Available = 1

#### 5.4 Wywołanie #2
1. Zmień event na `Test5-Sequential-Service2`
2. Użyj ID2 w event JSON
3. Kliknij Test
4. Poczekaj na zakończenie
5. Sprawdź SQS: Messages Available = 2

#### 5.5 Wywołanie #3
1. Zmień event na `Test5-Sequential-Service3`
2. Użyj ID3 w event JSON
3. Kliknij Test
4. Poczekaj na zakończenie
5. Sprawdź SQS: Messages Available = 3

#### 5.6 Weryfikacja
1. CloudWatch Logs powinny pokazywać 3 oddzielne wykonania
   - Każde z count=1
2. Poll messages z SQS i sprawdź wszystkie 3 wiadomości:
   - Wiadomość 1: service_id = ID1
   - Wiadomość 2: service_id = ID2
   - Wiadomość 3: service_id = ID3
3. Brak interferencji między wywołaniami

### Wynik Test 5
- [ ] Wszystkie 3 wywołania zakończyły się sukcesem
- [ ] SQS zawiera dokładnie 3 wiadomości
- [ ] Każda wiadomość ma poprawny service_id (ID1, ID2, ID3)
- [ ] CloudWatch Logs pokazują 3 oddzielne wykonania
- [ ] Brak błędów lub interferencji

**Status**: ✅ PASS / ❌ FAIL
**Notatki**: _____________________

---

## Test 6: Full Sync with Empty Result Set

### Cel
Sprawdzenie, czy Lambda poprawnie obsługuje full sync gdy żadne serwisy nie spełniają kryteriów.

### Krok po kroku

#### 6.1 Weryfikacja pustego result set
```sql
-- Sprawdź, że żadne serwisy nie mają tych type_id/status_id
SELECT COUNT(*) FROM pathwaysdos.services
WHERE statusid = 999 AND typeid = 999;
-- Powinno zwrócić: 0
```

#### 6.2 Wyczyść kolejkę
Zapisz aktualną liczbę wiadomości: __________

#### 6.3 Wywołaj Lambda
1. Nazwa: `Test6-FullSync-EmptyResult`
2. Event JSON:

```json
{
  "status_ids": [999],
  "type_ids": [999],
  "full_sync": true,
  "record_id": null,
  "service_id": null,
  "table_name": "services"
}
```

3. Test

#### 6.4 Weryfikacja
1. Lambda: succeeded (bez błędów)
2. CloudWatch Logs:
   - DM_QP_000: z type_ids: [999], status_ids: [999]
   - DM_QP_001: **count=0**
   - DM_QP_999: completed
3. SQS Queue: brak nowych wiadomości

### Wynik Test 6
- [ ] Lambda zakończyła się sukcesem
- [ ] CloudWatch Logs pokazują count=0
- [ ] SQS queue nie zawiera nowych wiadomości
- [ ] Brak błędów

**Status**: ✅ PASS / ❌ FAIL
**Notatki**: _____________________

---

## Podsumowanie Testów

### Checklist wszystkich testów

| Test | Opis | Status | Notatki |
|------|------|--------|---------|
| Test 1 | Single service - prawidłowy ID | ⬜ PASS / ⬜ FAIL | |
| Test 2 | Single service - nieistniejący ID | ⬜ PASS / ⬜ FAIL | |
| Test 3a | Brakujące service_id | ⬜ PASS / ⬜ FAIL | |
| Test 3b | Brakujące record_id | ⬜ PASS / ⬜ FAIL | |
| Test 3c | Brakujące table_name | ⬜ PASS / ⬜ FAIL | |
| Test 4 | Full sync - backward compatibility | ⬜ PASS / ⬜ FAIL | |
| Test 5 | Multiple sequential invocations | ⬜ PASS / ⬜ FAIL | |
| Test 6 | Full sync - empty result | ⬜ PASS / ⬜ FAIL | |

### Kryteria sukcesu
- [ ] Wszystkie 8 testów przeszły pomyślnie (PASS)
- [ ] Nowa funkcjonalność single-service działa poprawnie
- [ ] Istniejąca funkcjonalność full sync działa bez zmian
- [ ] Walidacja parametrów działa poprawnie
- [ ] Brak błędów w CloudWatch Logs
- [ ] Brak wiadomości w Dead Letter Queue

### Znalezione problemy
_Opisz tutaj wszystkie znalezione problemy lub niespodziewane zachowania:_

1. _____________________
2. _____________________
3. _____________________

### Wnioski
_Twoje uwagi i obserwacje:_

_____________________
_____________________
_____________________

---

## Dodatkowe informacje

### Przydatne linki AWS Console
- Lambda: [Wklej URL do Lambda function]
- SQS Queue: [Wklej URL do SQS queue]
- CloudWatch Logs: [Wklej URL do log group]

### SQL Queries - Przydatne zapytania

```sql
-- Znajdź aktywne serwisy
SELECT id, name, typeid, statusid
FROM pathwaysdos.services
WHERE statusid = 1
LIMIT 10;

-- Policz serwisy według typu i statusu
SELECT typeid, statusid, COUNT(*) as count
FROM pathwaysdos.services
GROUP BY typeid, statusid
ORDER BY count DESC;

-- Sprawdź konkretny serwis
SELECT * FROM pathwaysdos.services WHERE id = 12345;
```

### Troubleshooting

**Problem**: Lambda timeout
**Rozwiązanie**: Użyj mniejszego zakresu type_ids/status_ids dla full sync

**Problem**: Nie widzę wiadomości w SQS
**Rozwiązanie**: Odśwież stronę, sprawdź czy filtrujesz po "All messages"

**Problem**: CloudWatch Logs nie pokazują logów
**Rozwiązanie**: Poczekaj 30-60 sekund, odśwież. Sprawdź czy jesteś w odpowiednim regionie (eu-west-2)

**Problem**: Lambda nie ma dostępu do bazy danych
**Rozwiązanie**: Sprawdź security groups i VPC configuration w Lambda Configuration

---

**Data testów**: _____________________
**Tester**: _____________________
**Środowisko**: dev / ftrs-1898
**Workspace**: ftrs-1898

