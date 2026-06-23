import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "tickets.db")


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.secret_key = os.getenv("APP_SECRET_KEY", "dev-secret-key")

    init_db()

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/ticket/new", methods=["GET", "POST"])
    def new_ticket():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            category = request.form.get("category", "").strip()
            title = request.form.get("title", "").strip()
            description = request.form.get("description", "").strip()
            priority = request.form.get("priority", "Media").strip()

            ai_answer = helpdesk_agent(category, title, description)

            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(
                    """
                    INSERT INTO tickets
                    (name, email, category, title, description, priority, status, ai_answer, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        name,
                        email,
                        category,
                        title,
                        description,
                        priority,
                        "Aperto",
                        ai_answer,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    ),
                )
                conn.commit()

            return render_template("ticket_created.html", ai_answer=ai_answer, title=title)

        return render_template("new_ticket.html")

    @app.route("/admin", methods=["GET", "POST"])
    def admin_login():
        if request.method == "POST":
            password = request.form.get("password", "")
            if password == os.getenv("HELPDESK_ADMIN_PASSWORD", "admin123"):
                session["admin"] = True
                return redirect(url_for("dashboard"))
            return render_template("admin_login.html", error="Password non corretta")

        return render_template("admin_login.html")

    @app.route("/dashboard")
    def dashboard():
        if not session.get("admin"):
            return redirect(url_for("admin_login"))

        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            tickets = conn.execute(
                "SELECT * FROM tickets ORDER BY created_at DESC"
            ).fetchall()

        return render_template("dashboard.html", tickets=tickets)

    @app.route("/ticket/<int:ticket_id>", methods=["GET", "POST"])
    def ticket_detail(ticket_id):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))

        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row

            if request.method == "POST":
                status = request.form.get("status", "Aperto")
                operator_note = request.form.get("operator_note", "")
                conn.execute(
                    "UPDATE tickets SET status = ?, operator_note = ? WHERE id = ?",
                    (status, operator_note, ticket_id),
                )
                conn.commit()
                return redirect(url_for("dashboard"))

            ticket = conn.execute(
                "SELECT * FROM tickets WHERE id = ?", (ticket_id,)
            ).fetchone()

        return render_template("ticket_detail.html", ticket=ticket)

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))

    @app.route("/manifest.json")
    def manifest():
        return jsonify({
            "name": "HelpDesk AI Ticketing",
            "short_name": "HelpDesk AI",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#111827",
            "icons": []
        })

    return app


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                category TEXT,
                title TEXT,
                description TEXT,
                priority TEXT,
                status TEXT,
                ai_answer TEXT,
                operator_note TEXT DEFAULT '',
                created_at TEXT
            )
            """
        )
        conn.commit()


def helpdesk_agent(category, title, description):
    text = f"{category} {title} {description}".lower()

    if any(word in text for word in ["password", "login", "accesso", "credenziali"]):
        return """Possibile problema di accesso.

Prova questi passaggi:
1. Controlla che Caps Lock sia disattivato.
2. Reimposta la password dal portale aziendale.
3. Cancella cache e cookie del browser.
4. Prova da finestra anonima.
5. Se usi Microsoft 365, verifica MFA/Authenticator.

Se non riesci ancora ad accedere, il ticket resta aperto per il tecnico di secondo livello."""

    if any(word in text for word in ["stampante", "printer", "stampa"]):
        return """Possibile problema stampante.

Prova questi passaggi:
1. Controlla se la stampante è accesa e collegata alla rete.
2. Verifica che non ci siano fogli bloccati.
3. Rimuovi e reinserisci la stampante dal PC.
4. Controlla se la stampante corretta è impostata come predefinita.
5. Riavvia lo spooler di stampa.

Se il problema continua, serve verifica tecnica."""

    if any(word in text for word in ["vpn", "ivanti", "forticlient", "connessione remota"]):
        return """Possibile problema VPN.

Prova questi passaggi:
1. Controlla la connessione Internet.
2. Riavvia il client VPN.
3. Verifica username, password e MFA.
4. Prova a cambiare rete, ad esempio hotspot mobile.
5. Controlla se ci sono aggiornamenti del client VPN.

Se la VPN non si connette ancora, il ticket va al tecnico."""

    if any(word in text for word in ["internet", "rete", "wifi", "wi-fi", "connessione"]):
        return """Possibile problema di rete.

Prova questi passaggi:
1. Disconnetti e riconnetti il Wi-Fi.
2. Riavvia il router se sei a casa.
3. Prova con cavo Ethernet.
4. Apri il Prompt dei comandi e prova: ping 8.8.8.8
5. Se il ping funziona ma i siti no, potrebbe essere DNS.

Se non si risolve, il ticket resta aperto."""

    if any(word in text for word in ["lento", "prestazioni", "bloccato", "crash", "freeze"]):
        return """Possibile problema di prestazioni PC.

Prova questi passaggi:
1. Riavvia il PC.
2. Chiudi programmi inutilizzati.
3. Controlla spazio libero su disco.
4. Apri Gestione attività e verifica CPU/RAM.
5. Controlla aggiornamenti Windows.

Se il PC resta lento, serve analisi con tecnico."""

    if any(word in text for word in ["email", "outlook", "posta"]):
        return """Possibile problema email/Outlook.

Prova questi passaggi:
1. Controlla se Outlook Web funziona dal browser.
2. Riavvia Outlook.
3. Verifica connessione Internet.
4. Controlla spazio mailbox.
5. Rimuovi e riconfigura il profilo Outlook solo se autorizzato.

Se il problema continua, il ticket resta aperto."""

    return """Ho analizzato la richiesta, ma non ho trovato una procedura automatica sicura.

Il ticket resta aperto per un operatore umano.
Nel frattempo, aggiungi se possibile:
- screenshot dell'errore;
- quando è iniziato il problema;
- dispositivo usato;
- rete usata;
- messaggio di errore preciso."""
