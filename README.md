# HelpDesk AI Ticketing

Sistema ticketing MVP con agente AI di primo livello.

## Funzioni
- Utente apre un ticket
- Agente AI propone una soluzione immediata
- Se il problema non si risolve, il ticket resta aperto per intervento umano
- Dashboard admin
- Sito installabile come app grazie al manifest PWA

## Avvio locale

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```

Poi apri:

```text
http://localhost:5000
```

Password admin di default:

```text
admin123
```

Cambiala nel file `.env`.

## Mettere online
Puoi caricarlo su un servizio come Render, Railway, Fly.io o un VPS.

Su Render:
1. Crea un repository GitHub con questi file.
2. Vai su Render.
3. New Web Service.
4. Collega il repository.
5. Build command: `pip install -r requirements.txt gunicorn`
6. Start command: `gunicorn run:app`
7. Aggiungi le variabili:
   - `APP_SECRET_KEY`
   - `HELPDESK_ADMIN_PASSWORD`

## App scaricabile
Questo progetto è una PWA: aprendo il sito da Chrome/Edge, l'utente può fare:
- PC: Installa app dalla barra del browser
- Android: Aggiungi alla schermata Home

Così sembra un'app, ma resta un sito facile da aggiornare.
