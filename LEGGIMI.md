# Nios4 Sync (MySQL)

Toolkit Python per inizializzare un database MySQL compatibile con **Nios4**, gestire la sincronizzazione bidirezionale con il servizio remoto e utilizzare utilità comuni (TID/UUID, valutazione di espressioni, ecc).  
Il progetto espone tre classi principali:

- `database_nios4.py` — creazione/verifica schema, DDL/DDL helper, query semplici.
- `utility_nios4.py` — helper generici (TID/UUID, conversioni, valutatore di espressioni).
- `sync_nios4.py` — orchestratore di sincronizzazione, invio/ricezione pacchetti, notifiche, invio email, upload file.

> Le classi includono **type hints** e **docstring NumPy-style in inglese** per un’integrazione più agevole con IDE e linters.

---

## Indice

- [Caratteristiche](#caratteristiche)
- [Struttura repository](#struttura-repository)
- [Prerequisiti](#prerequisiti)
- [Installazione](#installazione)
- [Configurazione MySQL](#configurazione-mysql)
- [Quickstart](#quickstart)
- [Uso comune](#uso-comune)
  - [Notifiche applicative](#notifiche-applicative)
  - [Invio email](#invio-email)
  - [Upload file e binding al record](#upload-file-e-binding-al-record)
  - [Sync selettivo per tabelle](#sync-selettivo-per-tabelle)
- [Gestione errori](#gestione-errori)
- [Sicurezza & note operative](#sicurezza--note-operative)
- [Troubleshooting](#troubleshooting)
- [Sviluppo](#sviluppo)
- [Test](#test)
- [Licenza](#licenza)

---

## Caratteristiche

- **Bootstrap DB**: crea automaticamente le tabelle core (`so_tables`, `so_fields`, `so_users`, `lo_setting`, `lo_cleanbox`, `lo_syncbox`) se mancanti.
- **Sincronizzazione**:
  - invio struttura (tabelle/campi/utenti) e delta dati in pacchetti,
  - gestione `cleanbox` (delete) e `syncbox` (insert/update mirati),
  - scarico progressivo (partial) con applicazione locale.
- **Utility**:
  - `tid()` UTC in formato `YYYYMMDDHHMMSS` (intero),
  - `gguid()` UUID4 string,
  - `calc_expression()` valutazione sicura di espressioni numeriche Python-like,
  - conversioni e escaping per SQL.
- **Email/Notifiche**: invio email via endpoint remoto, creazione notifiche in `so_notifications`.
- **Upload file**: invio a storage remoto e salvataggio metadati nella tabella applicativa.

---

## Struttura repository

```
.
├── database_nios4.py
├── utility_nios4.py
├── sync_nios4.py
├── requirements.txt        # suggerito (vedi sotto)
├── .env.example            # esempio variabili ambiente (opzionale)
└── README.md               # questo file
```

---

## Prerequisiti

- **Python** 3.9+ (consigliato 3.11/3.12)
- **MySQL** 5.7+ / 8.0+
- Dipendenze Python:
  - `mysql-connector-python`
  - `requests`

Esempio `requirements.txt`:

```txt
mysql-connector-python>=9.0.0
requests>=2.31.0
python-dotenv>=1.0.1  # opzionale, per caricare .env
```

---

## Installazione

```bash
git clone https://github.com/<org>/<repo>.git
cd <repo>
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Opzionale: crea un `.env` a partire da `.env.example`.

---

## Configurazione MySQL

L’utente MySQL configurato deve avere permessi per:

- `CREATE DATABASE`, `CREATE`, `ALTER`, `DROP` sulle tabelle di lavoro,
- `SELECT`, `INSERT`, `UPDATE`, `DELETE`.

Esempio rapido:

```sql
CREATE DATABASE nios4 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'nios4'@'%' IDENTIFIED BY '********';
GRANT ALL PRIVILEGES ON nios4.* TO 'nios4'@'%';
FLUSH PRIVILEGES;
```

> Se il database non esiste, `database_nios4` lo crea automaticamente (con charset/collation standard) usando le credenziali server.

---

## Quickstart

Esempio minimale che inizializza il DB e avvia una sincronizzazione completa:

```python
from sync_nios4 import sync_nios4

SYNC = sync_nios4(
    username="user@example.com",         # credenziali servizio remoto
    password="password",
    token="",                            # se vuoto, viene eseguito login()
    dbname="nios4",
    hostdb="127.0.0.1",
    usernamedb="nios4",
    passworddb="********"
)

# Opzionale: limita le tabelle coinvolte
# SYNC.enabled_getdata_tables = ["my_table"]
# SYNC.enabled_setdata_tables = ["my_table"]

ok = SYNC.syncro(dbname="nios4_remote_key")  # 'db' per l'endpoint remoto
print("SYNC OK:", ok)
```

---

## Uso comune

### Notifiche applicative

```python
SYNC.send_notificationrecord(
    uta="target.user", 
    title="Promemoria attività", 
    description="Controlla la scheda #1234",
    tablename="orders",
    gguidrif="2a89c7bc-2c57-4d5e-ae9f-3c61a2d1c001"
)
```

### Invio email

```python
SYNC.send_emailv2(
    dbname="nios4_remote_key",
    sendfrom="noreply@example.com",
    sendfromname="Nios4 Bot",
    sendto="destinatario@example.com",
    subject="Conferma ordine",
    replyto="support@example.com",
    body="Grazie per il tuo ordine!",
    bodyhtml="<p><b>Grazie</b> per il tuo ordine!</p>",
    listcc=[],
    listbcc=[],
    listdocument=[]  # gestione allegati da implementare se necessario
)
```

Oppure via template:

```python
SYNC.send_templatemail(
    mail="destinatario@example.com",
    idtemplate=42,
    payload={"nome": "Davide", "ordine": "A-1002"}
)
```

### Upload file e binding al record

```python
resp = SYNC.download_file(
    dbname="nios4_remote_key",
    pathfile="/path/fattura.pdf",
    filename="fattura.pdf",
    tablename="invoices",
    fieldname="allegato",
    gguid="6ff3a0a1-4ece-4f0e-9b5a-2f3f8b9b4c51"
)
print(resp)
```

> Nel record, `allegato` conterrà un JSON con metadati; `file_allegato` il nome file. Il record viene messo in `lo_syncbox`.

### Sync selettivo per tabelle

```python
# Ricevi dati solo per alcune tabelle
SYNC.enabled_getdata_tables = ["invoices", "orders"]

# Invia dati solo per alcune tabelle
SYNC.enabled_setdata_tables = ["orders"]

# (Opzionale) Crea solo alcune tabelle ricevendo struttura
SYNC.enabled_create_tables = ["so_localusers", "orders"]
```

---

## Gestione errori

Tutte le classi espongono un contenitore errori `error_n4` condiviso:

```python
if not SYNC.syncro("nios4_remote_key"):
    print("Errore:", SYNC.err.errorcode, SYNC.err.errormessage)
```

In generale:

- codici `E0xx` → errori locali (DB/connessioni/IO),
- HTTP status code o `KO` dal server → messaggi remoti in `errormessage`.

---

## Sicurezza & note operative

- Salva **token/credenziali** in variabili d’ambiente o `.env`. Non committare segreti.
- `download_file()` invia i byte del file all’endpoint remoto: valuta **dimensioni** e **tipi** permessi.
- Le query costruite dinamicamente usano escaping semplificato per gli apici — **non usare input non sanificati** di utenti finali.
- Assicurati che l’orologio di sistema sia **sincronizzato (UTC)**: il flusso usa `tid()` come ordinamento temporale.

---

## Troubleshooting

- **`Please login first to synchronize (E019)`**  
  Fornisci `token` valido o `username/password` per eseguire `login()`.

- **`None` in ritorno dalle query`**  
  Verifica credenziali MySQL, nome DB e permessi; controlla `err.errormessage`.

- **Problemi di schema**  
  Cancella o ripristina tabelle core solo se necessario. `database_nios4.initializedb()` ricrea la struttura minima.

- **Date non parsabili durante install_data**  
  I valori data devono essere numeri `YYYYMMDDHHMMSS`; in caso contrario vengono ignorati/loggati.

---

## Sviluppo

Suggerimenti:

- Linting: `ruff` o `flake8`
- Tipi: `mypy`
- Formattazione: `black`

Esempio:

```bash
pip install ruff mypy black
ruff check .
mypy .
black .
```

---

## Test

Puoi usare `pytest` per testare i percorsi principali (mockando rete e DB):

```bash
pip install pytest pytest-mock
pytest
```

Linee guida:

- Mock `requests` e `urllib.request.urlopen` per le chiamate remote.
- Usa un **database temporaneo** per i test di integrazione.

---

## Licenza

Il codice include una clausola di esclusione responsabilità in stile **BSD** negli header dei file.  
Per l’uso su GitHub, si consiglia di aggiungere un file `LICENSE` (es. **BSD-3-Clause**) che rifletta i termini già presenti nelle intestazioni.

---

## Crediti

Copyright © 2020–2024  
**Davide Sbreviglieri**

Contribuzioni e suggerimenti sono benvenuti via Pull Request o Issues.
