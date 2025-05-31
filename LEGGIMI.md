## Premessa
Questo progetto è stato sviluppato per funzionare con Python 3 e serve per poter di interagire direttamente con il sincronizzatore dei dati di Nios4.

Il sistema cloud di Nios4 si base principalmente su due tipi di database:

- Il primo database è quello che passa per il server di sincronizzazione di D-One, dove i dati sono formattati come stringhe json per essere archiviati e scambiate tra i vari dispositivi che lo richiedono. Questo permette di avere un database con tabelle identiche non differenziate in base ai dati che conterrano.

- Il secondo database è quello cloud utilizzato dalla versione web, dove i dati sono salvati all'interno dei loro rispettivi campi e tabelle per poter essere utilizzati direttamente dal front-end.

Le API di Nios4 [https://developer.nios4.com/web-api] sono state realizzate per leggere e scrivere i dati direttamente dal database della versione web.

In questo progetto si utilizzeranno invece le API che interagiscono con i dati direttamente all'interno del database di sincronizzazione.
La differenza principale e che mentre le API per il cloud gestiscono normalmente un record alla volta con l'utilizzo diretto del sincronizzatore  è possibile gestire molti record contemporaneamente sia in lettura che in scrittura.

Un'altra caratteristica del progetto e che i dati vengono suddivisi (se necessario) in pacchetti. Ossia sopra a un certo numero di dati (sia in lettura che in scrittura) il programma li dividerà in più pacchetti da spedire e ricevere per evitare un sovraccarico sulla rete e una possibile perdita di dati.

Attualmente non vengono gestiti i file e le immagini. Questi verranno gestiti in una versione futura del progetto.

Il progetto è stato testato su un Raspberry 3.

## Dipendenze
L'unica dipendenza che normalmente va installata è quella per sqlite3 per gestire il database. Tutta la gestione del database è stata realizzata su una classe esterna per permettere di creare una eventuale classe collegata ad un altro tipo di database.

Per installare sqlite3 (dopo aver dato i soliti comandi di update e upgrade) digitare il seguente comando dal terminale:

`sudo apt-get install sqlite3`

## Eseguire il progetto
Per eseguire il progetto per prima cosa hai bisogno di un account della D-One e di un database cloud creato da Nios4 (va benissimo anche la versione gratis)

- vai sul sito [https://web.nios4.com]
- registrati se non lo hai ancora fatto e crea un database cloud. La versione gratuita non scade mai.

Fatto questo apri il file test.py e inserisci i dati del tuo account e il nome del database. Questo nome normalmente è visibile sul programma. Se non lo vedi vai sul sito [https://www.d-one.store], accedi con i tuoi dati ed entra nel pannello di gestione dei database. Il nome che ti interessa è scritto tra parentesi a fianco del titolo del database.

```sh
from sync_nios4 import sync_nios4

username = "username"
password = "password"
dbname = "numberdb"

sincro = sync_nios4(username,password)

valori = sincro.login()
if sincro.err.error == True:
    print("ERROR -> " + sincro.err.errormessage)

sincro.syncro(dbname)
if sincro.err.error == True:
    print("ERROR -> " + sincro.err.errormessage)
```

## Creare dati e sincronizzarli
Ora che è presente il database è possibile inserire i dati all'interno delle tabelle. Ricordarsi che le tabelle so_ e lo_ sono di sistema, questo vuol dire che comunque puoi scrivere e modificare i dati, ma se non si conosce la loro funzione si creeranno dei malfunzionamenti sui programmi.

Le cose da ricordare per un corretto utilizzo del programma sono:

- Creare sempre record che non contengano `nil`. All'interno della classe del database è presente un metodo per creare un nuovo record che può essere usato per evitare questo problema `[db_nios4.newrow]`.

- Per inviare dati al sincronizzatore occorre modificare il valore della colonna `tid`. Questa colonna contiene il momento in cui è stato modificato il record. Alla fine di ogni sincronizzazione il programma salva il momento dell'invio/ricezione dei dati. Alla prossima sincronizzazione controllerà solamente i record che hanno un momento temporale maggiore di quello salvato. Utilizzare la funzione `[utility_nios4.tid]` per recuperare il corretto formato del valore di tid



