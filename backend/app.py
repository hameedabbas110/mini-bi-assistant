
import json
import os
import re

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai

from analytics import (
    total_revenue,
    top_product,
    monthly_revenue,
    top_region,
    compare_months,
)

load_dotenv()

app = Flask(__name__)
CORS(app)

ALLOWED_INTENTS = {
    "total_revenue",
    "top_product",
    "monthly_revenue",
    "top_region",
    "compare_months",
    "unknown",
}

MODEL_NAME = "gemini-3.5-flash-lite"


def rule_based_interpretation(question):
    """Recognize supported questions without calling an external AI."""
    q = question.lower().strip()

    if "revenue" in q and any(
        word in q for word in ["compare", "change", "between"]
    ):
        months = re.findall(r"\b(20\d{2}-(?:0[1-9]|1[0-2]))\b", q)
        if len(months) == 2:
            return {"intent": "compare_months", "months": months}
        return {"intent": "unknown", "months": []}

    if "monthly" in q and any(
        word in q for word in ["revenue", "sales"]
    ):
        return {"intent": "monthly_revenue", "months": []}

    if any(word in q for word in ["product", "item"]) and any(
        word in q for word in ["highest", "top", "best", "most"]
    ):
        return {"intent": "top_product", "months": []}

    if "region" in q and any(
        word in q for word in ["highest", "top", "best", "sales", "revenue"]
    ):
        return {"intent": "top_region", "months": []}

    if any(word in q for word in ["total", "overall"]) and any(
        word in q for word in ["revenue", "sales"]
    ):
        return {"intent": "total_revenue", "months": []}

    return {"intent": "unknown", "months": []}


def interpret_question(question):
    """Use Gemini when available; otherwise use safe rule-based fallback."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        result = rule_based_interpretation(question)
        result["method"] = "rules"
        return result

    prompt = f"""
Classify the user's business analytics question.
Return a JSON object with:
- intent: one of {sorted(ALLOWED_INTENTS)}
- months: an array of YYYY-MM strings

Rules:
- total_revenue: asks for total or overall revenue or sales
- top_product: asks which product or item has the highest revenue or sales
- monthly_revenue: asks for a monthly revenue or sales trend
- top_region: asks which region has the highest revenue or sales
- compare_months: asks to compare revenue between two months
- unknown: anything else or ambiguous
- For compare_months, extract exactly two valid YYYY-MM months.
- For all other intents, months must be an empty array.
- Never calculate or answer the business question.

User question:
{question}
"""

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": {
                    "type": "OBJECT",
                    "properties": {
                        "intent": {
                            "type": "STRING",
                            "enum": sorted(ALLOWED_INTENTS),
                        },
                        "months": {
                            "type": "ARRAY",
                            "items": {"type": "STRING"},
                        },
                    },
                    "required": ["intent", "months"],
                },
            },
        )

        result = json.loads(response.text or "{}")
        intent = result.get("intent")
        months = result.get("months")

        if intent not in ALLOWED_INTENTS or not isinstance(months, list):
            raise ValueError("Invalid AI classification.")

        if any(
            not isinstance(month, str)
            or not re.fullmatch(r"20\d{2}-(0[1-9]|1[0-2])", month)
            for month in months
        ):
            raise ValueError("Invalid month format.")

        if intent == "compare_months":
            if len(months) != 2:
                raise ValueError("Month comparison requires two months.")
        elif months:
            raise ValueError("Unexpected months for this intent.")

        return {
            "intent": intent,
            "months": months,
            "method": "llm",
        }

    except Exception:
        app.logger.warning(
            "Gemini interpretation failed; using rule-based fallback.",
            exc_info=True,
        )
        result = rule_based_interpretation(question)
        result["method"] = "rules"
        return result


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Mini AI Business Intelligence Assistant API is running."
    })


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Send a JSON object with a question."
        }), 400

    question = data.get("question")

    if not isinstance(question, str) or not question.strip():
        return jsonify({
            "error": "Question must be a non-empty string."
        }), 400

    question = question.strip()

    if len(question) > 500:
        return jsonify({
            "error": "Question must be 500 characters or fewer."
        }), 400

    classification = interpret_question(question)
    intent = classification["intent"]
    months = classification["months"]
    method = classification["method"]

    if intent == "unknown":
        return jsonify({
            "error": (
                "I could not understand that question. Try asking about "
                "total revenue, top product, monthly revenue, top region, "
                "or compare two months using YYYY-MM."
            ),
            "interpretation_method": method,
        }), 400

    try:
        if intent == "compare_months":
            result = compare_months(months[0], months[1])
        else:
            analytics_functions = {
                "total_revenue": total_revenue,
                "top_product": top_product,
                "monthly_revenue": monthly_revenue,
                "top_region": top_region,
            }
            result = analytics_functions[intent]()

        return jsonify({
            "question": question,
            "intent": intent,
            "answer": result,
            "source": (
                "Gemini interpretation + SQLite analytics query"
                if method == "llm"
                else "Rule-based interpretation + SQLite analytics query"
            ),
            "interpretation_method": method,
        })

    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        app.logger.exception("Analytics request failed")
        return jsonify({
            "error": "The analytics request failed. Please try again."
        }), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
