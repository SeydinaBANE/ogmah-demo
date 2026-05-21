"""
Conversational assistant powered by OpenRouter.
Grounds all answers in live DB context — no hallucinations.
Uses the OpenAI-compatible API with OpenRouter as the gateway.
"""
from dataclasses import dataclass, field

from openai import OpenAI, APIError, APITimeoutError, RateLimitError
from sqlalchemy.orm import Session

from app.database import settings
from app.llm.context_builder import build_business_context, build_recipe_context

SYSTEM_PROMPT = """Tu es l'assistant IA d'ogmah, spécialisé dans la gestion de restaurant.
Tu aides les restaurateurs à analyser leurs données : marges, coûts matières, anomalies d'achat, prévisions de ventes.

Règles absolues :
- Tu ne réponds QUE sur la base des données fournies dans le contexte. Jamais de chiffres inventés.
- Si une information n'est pas dans le contexte, dis-le clairement.
- Tes réponses sont concises, factuelles et actionnables.
- Tu parles toujours en français.
- Tu utilises le format markdown quand c'est utile (tableaux, listes).

Domaine métier :
- Food cost ratio cible : ≤ 30% (coût ingrédients / prix de vente)
- Marge brute = 1 - food cost ratio
- Une anomalie d'achat = prix fournisseur déviant de > 20% vs moyenne des 30 derniers jours
- Tu peux recommander des actions concrètes : renegocier fournisseur, ajuster prix, reformuler recette
"""


@dataclass
class Message:
    role: str  # "system", "user" or "assistant"
    content: str


@dataclass
class ChatSession:
    messages: list[Message] = field(default_factory=list)

    def add(self, role: str, content: str):
        self.messages.append(Message(role=role, content=content))

    def to_api_messages(self) -> list[dict]:
        return [{"role": m.role, "content": m.content} for m in self.messages]


class RestaurantAssistant:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com/ogmah-demo",
                "X-Title": "OgmahDemo Restaurant AI",
            },
        )

    def _build_system_content(self, db: Session) -> str:
        business_ctx = build_business_context(db)
        recipe_ctx = build_recipe_context(db)
        return f"{SYSTEM_PROMPT}\n\n{business_ctx}\n\n{recipe_ctx}"

    def chat(self, db: Session, session: ChatSession, user_message: str) -> str:
        session.add("user", user_message)

        # Build messages with fresh system context on each turn
        system_content = self._build_system_content(db)
        messages = [{"role": "system", "content": system_content}] + [
            {"role": m.role, "content": m.content}
            for m in session.messages
        ]

        try:
            response = self.client.chat.completions.create(
                model=settings.openrouter_model,
                messages=messages,
                max_tokens=1024,
                timeout=30,
            )
            assistant_reply = response.choices[0].message.content or ""
        except RateLimitError:
            assistant_reply = "Le service est temporairement surchargé. Réessayez dans quelques instants."
        except APITimeoutError:
            assistant_reply = "La requête a pris trop de temps. Réessayez."
        except APIError as e:
            assistant_reply = f"Erreur du service IA ({e.status_code}). Vérifiez la configuration de la clé API."

        if not assistant_reply:
            assistant_reply = "Je n'ai pas pu générer de réponse. Reformulez votre question."

        session.add("assistant", assistant_reply)
        return assistant_reply
