import os
from openai import OpenAI


def analizza_ticket(category, title, description):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return "Errore: OPENAI_API_KEY non configurata su Render."

    try:
        client = OpenAI(api_key=api_key)

        prompt = f"""
Sei un tecnico Help Desk IT Senior.

Categoria: {category}
Titolo: {title}
Descrizione: {description}

Rispondi in italiano con questo formato:

Categoria:
Priorità:
Escalation:
Soluzione:
Risposta utente:
Nota tecnica:
"""

        risposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Sei un agente AI Help Desk professionale."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        return risposta.choices[0].message.content

    except Exception as e:
        return f"Errore Agent AI: {str(e)}"
