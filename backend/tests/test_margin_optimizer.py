"""Unit tests for MarginOptimizer — uses mock DB data."""
import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch


def _make_mock_recipe(id: int, name: str, price: float, ingredients: list) -> MagicMock:
    recipe = MagicMock()
    recipe.id = id
    recipe.name = name
    recipe.category = "plat"
    recipe.selling_price = Decimal(str(price))
    recipe.is_active = True

    ris = []
    for ing_id, qty in ingredients:
        ri = MagicMock()
        ri.ingredient_id = ing_id
        ri.quantity = Decimal(str(qty))
        ris.append(ri)
    recipe.recipe_ingredients = ris
    return recipe


def test_food_cost_ratio_calculation():
    """Verify the food cost ratio formula: ingredient_cost / selling_price."""
    # ingredient 1: price 5€/kg, quantity 0.2kg → cost 1€
    # ingredient 2: price 3€/L, quantity 0.1L → cost 0.3€
    # total ingredient cost = 1.30€, selling price = 10€
    # food cost ratio = 0.13 (13%)

    from app.ml.margin_optimizer import MarginOptimizer

    optimizer = MarginOptimizer()

    latest_prices = {1: 5.0, 2: 3.0}
    monthly_qty = {42: 50}
    recipe = _make_mock_recipe(42, "Test Recette", 10.0, [(1, 0.2), (2, 0.1)])

    with patch.object(optimizer, "_get_latest_prices", return_value=latest_prices), \
         patch.object(optimizer, "_get_monthly_avg_qty", return_value=monthly_qty):

        db = MagicMock()
        db.execute.return_value.scalars.return_value.all.return_value = [recipe]

        report = optimizer.analyze(db)

    assert len(report.recipes) == 1
    r = report.recipes[0]
    assert abs(r.ingredient_cost - 1.30) < 0.01
    assert abs(r.food_cost_ratio - 0.13) < 0.01
    assert abs(r.margin_pct - 87.0) < 0.5
    assert not r.is_below_target  # 13% < 30% target


def test_below_target_recipe_detected():
    """Recipes with food cost > 30% should be flagged."""
    from app.ml.margin_optimizer import MarginOptimizer

    optimizer = MarginOptimizer()
    # ingredient cost = 5€, selling price = 12€ → food cost = 41.7%
    latest_prices = {1: 50.0}
    monthly_qty = {1: 20}
    recipe = _make_mock_recipe(1, "Recette Chère", 12.0, [(1, 0.1)])

    with patch.object(optimizer, "_get_latest_prices", return_value=latest_prices), \
         patch.object(optimizer, "_get_monthly_avg_qty", return_value=monthly_qty):

        db = MagicMock()
        db.execute.return_value.scalars.return_value.all.return_value = [recipe]

        report = optimizer.analyze(db)

    assert report.below_target_count == 1
    assert report.recipes[0].is_below_target
    assert report.total_optimization_opportunity_eur > 0
