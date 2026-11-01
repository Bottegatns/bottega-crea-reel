# Bottega · Crea Reel ONLINE

Questa è una prima versione da pubblicare su Streamlit Community Cloud. **Non è già online**: per usarla dal browser va effettuata la pubblicazione.

## Pubblicazione (una sola volta)

1. Crea un repository GitHub privato e carica tutti i file di questa cartella (inclusa `assets`).
2. Vai su https://share.streamlit.io/ e crea una nuova app dal repository, indicando `app.py` come file principale.
3. Verifica che la piattaforma installi `ffmpeg` tramite `packages.txt`.
4. Apri l'indirizzo della nuova app dal browser, carica video e premi **CREA REEL**.

**Nota privacy:** se l'app deve essere usata solo dai volontari, verifica le opzioni di accesso disponibili nel piano scelto. Un repository GitHub privato non rende automaticamente privata la pagina dell'app. Evita di caricare filmati riservati in un'app pubblicamente accessibile.

## Dropbox (opzionale)

L'app può leggere direttamente la cartella Dropbox, ma serve un token Dropbox valido. Nelle impostazioni *Secrets* dell'app online aggiungi:

```toml
DROPBOX_ACCESS_TOKEN = "TOKEN_DA_CONFIGURARE"
```

Non inserire mai il token nel repository GitHub. Alcuni token Dropbox scadono: per uso continuativo servirà configurare OAuth con refresh token.

## Limiti attuali

- L'app usa il motore di montaggio automatico esistente: non analizza semanticamente prodotti, etichette o prezzi.
- Le scritte sono alternate e non dovrebbero sovrapporsi tra loro, ma vanno comunque controllate nell'anteprima.
- I limiti di memoria e dimensione video dipendono dall'hosting scelto.
- Il salvataggio automatico dell'MP4 in Dropbox non è ancora implementato; per ora il Reel si scarica con il pulsante.
