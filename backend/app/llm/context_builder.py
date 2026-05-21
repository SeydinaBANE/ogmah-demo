"""
Builds structured context from DB data for grounding the LLM assistant.
Keeps answers factual — no hallucinations.
"""
from datetime import date, timedelta

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.db_models import Recipe, Sale, Purchase, Ingredient, Stock


def build_business_context(db: Session) -> str:
    today = date.today()
    month_start = today.replace(day=1)
    last_30 = today - timedelta(days=30)

    # Monthly revenue + sales
    monthly_sales = db.execute(
        select(func.sum(Sale.revenue), func.sum(Sale.quantity_sold))
        .where(Sale.sale_date >= month_start)
    ).one()
    monthly_revenue = float(monthly_sales[0] or 0)
    monthly_covers = int(monthly_sales[1] or 0)

    # Active recipes count
    recipe_count = db.execute(
        select(func.count()).select_from(Recipe).where(Recipe.is_active == True)
    ).scalar()

    # Anomalies in last 30 days
    anomaly_count = db.execute(
        select(func.count())
        .select_from(Purchase)
        .where(Purchase.purchase_date >= last_30, Purchase.is_anomaly == True)
    ).scalar()

    # Top 5 selling dishes this month
    top_dishes = db.execute(
        select(Recipe.name, func.sum(Sale.quantity_sold).label("qty"))
        .join(Sale, Sale.recipe_id == Recipe.id)
        .where(Sale.sale_date >= month_start)
        .group_by(Recipe.name)
        .order_by(func.sum(Sale.quantity_sold).desc())
        .limit(5)
    ).fetchall()

    # Recent anomalous purchases
    anomalies = db.execute(
        select(Ingredient.name, Purchase.supplier, Purchase.purchase_date, Purchase.unit_price, Purchase.anomaly_score)
        .join(Ingredient)
        .where(Purchase.purchase_date >= last_30, Purchase.is_anomaly == True)
        .order_by(Purchase.purchase_date.desc())
        .limit(5)
    ).fetchall()

    lines = [
        f"=== DONNÉES MÉTIER (au {today.strftime('%d/%m/%Y')}) ===",
        f"Restaurant actif avec {recipe_count} recettes.",
        f"Ce mois-ci : CA = {monthly_revenue:.0f}€, {monthly_covers} couverts vendus.",
        f"Anomalies d'achat (30 derniers jours) : {anomaly_count} détectées.",
        "",
        "Top 5 plats vendus ce mois-ci :",
    ]
    for dish, qty in top_dishes:
        lines.append(f"  - {dish} : {qty} portions")

    if anomalies:
        lines.append("")
        lines.append("Achats suspects récents :")
        for name, supplier, pdate, price, score in anomalies:
            lines.append(f"  - {name} (fournisseur: {supplier}) le {pdate} à {price:.2f}€/unité")

    return "\n".join(lines)


def build_recipe_context(db: Session) -> str:
    """Returns recipe + current ingredient cost details."""
    from app.ml.margin_optimizer import MarginOptimizer
    optimizer = MarginOptimizer()
    report = optimizer.analyze(db)

    lines = ["=== ANALYSE DES MARGES RECETTES ==="]
    for r in report.recipes:
        status = "⚠ SOUS OBJECTIF" if r.is_below_target else "OK"
        lines.append(
            f"  {r.recipe_name} ({r.category}): prix vente {r.selling_price:.2f}€, "
            f"coût matière {r.ingredient_cost:.2f}€, "
            f"food cost ratio {r.food_cost_ratio*100:.1f}% [{status}]"
        )

    lines.append(f"Ratio food cost moyen : {report.avg_food_cost_ratio*100:.1f}%")
    lines.append(f"Objectif cible : ≤ 30%")
    return "\n".join(lines)
