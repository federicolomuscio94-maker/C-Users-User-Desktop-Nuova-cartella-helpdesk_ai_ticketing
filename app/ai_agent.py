import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def analizza_ticket(category, title, description):

    prompt = f"""
Sei un tecnico Help Desk IT Senior.

Analizza questo ticket.

Categoria:
{category}

Titolo:
{title}

Descrizione:
{description}

Rispondi in italiano.

Formato:

Categoria:
Priorità:
Escalation:
Soluzione:
Risposta utente:
Nota tecnica:
"""

    risposta = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "Sei un agente AI Help Desk professionale."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return risposta.choices[0].message.content
