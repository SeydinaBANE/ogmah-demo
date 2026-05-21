"""
Computes food-cost ratio and margin per recipe using the most recent purchase prices.
Identifies recipes below target margin and suggests optimizations.
"""
from dataclasses import dataclass
from decimal import Decimal

import pandas as pd
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.db_models import Recipe, RecipeIngredient, Ingredient, Purchase

TARGET_FOOD_COST_RATIO = 0.30  # 30% max


@dataclass
class RecipeMargin:
    recipe_id: int
    recipe_name: str
    category: str
    selling_price: float
    ingredient_cost: float
    food_cost_ratio: float
    margin_pct: float
    is_below_target: bool
    optimization_opportunity_eur: float  # monthly revenue impact if cost reaches target


@dataclass
class MarginReport:
    recipes: list[RecipeMargin]
    avg_food_cost_ratio: float
    below_target_count: int
    total_optimization_opportunity_eur: float


class MarginOptimizer:
    def _get_latest_prices(self, db: Session) -> dict[int, float]:
        """Returns the most recent unit_price per ingredient_id."""
        subq = (
            select(Purchase.ingredient_id, func.max(Purchase.purchase_date).label("max_date"))
            .group_by(Purchase.ingredient_id)
            .subquery()
        )
        rows = db.execute(
            select(Purchase.ingredient_id, Purchase.unit_price)
            .join(subq, (Purchase.ingredient_id == subq.c.ingredient_id) &
                        (Purchase.purchase_date == subq.c.max_date))
        ).fetchall()
        return {row.ingredient_id: float(row.unit_price) for row in rows}

    def _get_monthly_avg_qty(self, db: Session) -> dict[int, float]:
        """Returns average monthly quantity sold per recipe over last 30 days."""
        from datetime import date, timedelta
        cutoff = date.today() - timedelta(days=30)
        from app.models.db_models import Sale
        rows = db.execute(
            select(Sale.recipe_id, func.sum(Sale.quantity_sold).label("total_qty"))
            .where(Sale.sale_date >= cutoff)
            .group_by(Sale.recipe_id)
        ).fetchall()
        return {row.recipe_id: float(row.total_qty) for row in rows}

    def analyze(self, db: Session) -> MarginReport:
        latest_prices = self._get_latest_prices(db)
        monthly_qty = self._get_monthly_avg_qty(db)

        recipes = db.execute(
            select(Recipe).where(Recipe.is_active == True)
        ).scalars().all()

        margins = []
        for recipe in recipes:
            ingredient_cost = 0.0
            for ri in recipe.recipe_ingredients:
                price = latest_prices.get(ri.ingredient_id)
                if price is None:
                    continue
                ingredient_cost += price * float(ri.quantity)

            selling_price = float(recipe.selling_price)
            if selling_price == 0:
                continue

            food_cost_ratio = ingredient_cost / selling_price
            margin_pct = (1 - food_cost_ratio) * 100

            qty = monthly_qty.get(recipe.id, 0)
            # If we could bring food_cost to target, this is the monthly savings
            if food_cost_ratio > TARGET_FOOD_COST_RATIO:
                excess_cost = (food_cost_ratio - TARGET_FOOD_COST_RATIO) * selling_price
                opportunity = excess_cost * qty
            else:
                opportunity = 0.0

            margins.append(RecipeMargin(
                recipe_id=recipe.id,
                recipe_name=recipe.name,
                category=recipe.category,
                selling_price=selling_price,
                ingredient_cost=round(ingredient_cost, 4),
                food_cost_ratio=round(food_cost_ratio, 4),
                margin_pct=round(margin_pct, 2),
                is_below_target=food_cost_ratio > TARGET_FOOD_COST_RATIO,
                optimization_opportunity_eur=round(opportunity, 2),
            ))

        margins.sort(key=lambda r: r.food_cost_ratio, reverse=True)

        avg_ratio = sum(m.food_cost_ratio for m in margins) / len(margins) if margins else 0
        below_target = sum(1 for m in margins if m.is_below_target)
        total_opportunity = sum(m.optimization_opportunity_eur for m in margins)

        return MarginReport(
            recipes=margins,
            avg_food_cost_ratio=round(avg_ratio, 4),
            below_target_count=below_target,
            total_optimization_opportunity_eur=round(total_opportunity, 2),
        )
