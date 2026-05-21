"""
Generate 6 months of realistic synthetic restaurant data.
Run: python -m app.data.seed
"""
import random
from datetime import date, timedelta
from decimal import Decimal

import numpy as np
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models.db_models import Base, Ingredient, Recipe, RecipeIngredient, Purchase, Sale, Stock

random.seed(42)
np.random.seed(42)

INGREDIENTS = [
    ("Bœuf entrecôte", "kg", "viande", "Maison Dupont"),
    ("Poulet fermier", "kg", "viande", "Volailles Martin"),
    ("Saumon frais", "kg", "poisson", "Marée Fraîche"),
    ("Pommes de terre", "kg", "légume", "Primeur Local"),
    ("Oignons", "kg", "légume", "Primeur Local"),
    ("Ail", "kg", "légume", "Primeur Local"),
    ("Crème fraîche", "L", "laitier", "Fromagerie Bertrand"),
    ("Beurre", "kg", "laitier", "Fromagerie Bertrand"),
    ("Farine T65", "kg", "épicerie", "Minoterie Centrale"),
    ("Vin rouge", "L", "boisson", "Cave du Patron"),
    ("Huile d'olive", "L", "épicerie", "Oliviers & Co"),
    ("Tomates", "kg", "légume", "Primeur Local"),
    ("Champignons", "kg", "légume", "Champignonnière Bio"),
    ("Lardons", "kg", "charcuterie", "Charcuterie Renard"),
    ("Parmesan", "kg", "laitier", "Fromagerie Bertrand"),
    ("Pâtes fraîches", "kg", "épicerie", "Pasta Nobile"),
    ("Citron", "pcs", "fruit", "Primeur Local"),
    ("Thym", "kg", "épice", "Herbes & Saveurs"),
    ("Sel", "kg", "épice", "Épicerie Fine"),
    ("Poivre", "kg", "épice", "Épicerie Fine"),
]

BASE_PRICES = {
    "Bœuf entrecôte": 22.0,
    "Poulet fermier": 8.5,
    "Saumon frais": 18.0,
    "Pommes de terre": 0.8,
    "Oignons": 0.6,
    "Ail": 4.0,
    "Crème fraîche": 3.2,
    "Beurre": 9.0,
    "Farine T65": 0.9,
    "Vin rouge": 6.0,
    "Huile d'olive": 8.5,
    "Tomates": 2.2,
    "Champignons": 5.5,
    "Lardons": 7.0,
    "Parmesan": 18.0,
    "Pâtes fraîches": 4.5,
    "Citron": 0.3,
    "Thym": 12.0,
    "Sel": 0.5,
    "Poivre": 15.0,
}

RECIPES_DATA = [
    ("Entrecôte sauce bordelaise", "plat", 28.0, [
        ("Bœuf entrecôte", 0.25), ("Vin rouge", 0.10), ("Beurre", 0.03),
        ("Oignons", 0.05), ("Thym", 0.002), ("Sel", 0.005), ("Poivre", 0.002),
    ]),
    ("Poulet rôti aux herbes", "plat", 18.5, [
        ("Poulet fermier", 0.30), ("Thym", 0.003), ("Ail", 0.02),
        ("Huile d'olive", 0.03), ("Sel", 0.005), ("Citron", 1.0),
    ]),
    ("Pavé de saumon", "plat", 22.0, [
        ("Saumon frais", 0.18), ("Crème fraîche", 0.05), ("Citron", 0.5),
        ("Thym", 0.002), ("Beurre", 0.02), ("Sel", 0.003),
    ]),
    ("Tagliatelles carbonara", "plat", 14.0, [
        ("Pâtes fraîches", 0.15), ("Lardons", 0.08), ("Parmesan", 0.04),
        ("Crème fraîche", 0.04), ("Sel", 0.003), ("Poivre", 0.002),
    ]),
    ("Bœuf bourguignon", "plat", 24.0, [
        ("Bœuf entrecôte", 0.28), ("Vin rouge", 0.20), ("Champignons", 0.10),
        ("Lardons", 0.06), ("Oignons", 0.08), ("Beurre", 0.03),
        ("Farine T65", 0.02), ("Thym", 0.003),
    ]),
    ("Gratin dauphinois", "accompagnement", 6.5, [
        ("Pommes de terre", 0.25), ("Crème fraîche", 0.08), ("Ail", 0.01),
        ("Beurre", 0.02), ("Sel", 0.003), ("Poivre", 0.001),
    ]),
    ("Salade tomates mozzarella", "entrée", 9.0, [
        ("Tomates", 0.15), ("Huile d'olive", 0.02), ("Sel", 0.002), ("Poivre", 0.001),
    ]),
    ("Pasta al pomodoro", "plat", 12.0, [
        ("Pâtes fraîches", 0.15), ("Tomates", 0.20), ("Ail", 0.01),
        ("Huile d'olive", 0.03), ("Parmesan", 0.03), ("Sel", 0.003),
    ]),
    ("Risotto aux champignons", "plat", 16.0, [
        ("Champignons", 0.12), ("Vin rouge", 0.05), ("Beurre", 0.04),
        ("Parmesan", 0.05), ("Oignons", 0.05), ("Sel", 0.003),
    ]),
    ("Poulet basquaise", "plat", 19.0, [
        ("Poulet fermier", 0.28), ("Tomates", 0.20), ("Oignons", 0.10),
        ("Ail", 0.015), ("Huile d'olive", 0.03), ("Thym", 0.002),
    ]),
]

DISH_POPULARITY = {
    "Entrecôte sauce bordelaise": 12,
    "Poulet rôti aux herbes": 18,
    "Pavé de saumon": 15,
    "Tagliatelles carbonara": 22,
    "Bœuf bourguignon": 10,
    "Gratin dauphinois": 25,
    "Salade tomates mozzarella": 20,
    "Pasta al pomodoro": 16,
    "Risotto aux champignons": 11,
    "Poulet basquaise": 14,
}


def create_ingredient_map(db: Session) -> dict[str, Ingredient]:
    ingredient_map = {}
    for name, unit, category, _ in INGREDIENTS:
        ing = Ingredient(name=name, unit=unit, category=category)
        db.add(ing)
        ingredient_map[name] = ing
    db.flush()
    return ingredient_map


def create_recipes(db: Session, ingredient_map: dict[str, Ingredient]) -> dict[str, Recipe]:
    recipe_map = {}
    for name, category, price, ingredients in RECIPES_DATA:
        recipe = Recipe(name=name, category=category, selling_price=Decimal(str(price)))
        db.add(recipe)
        db.flush()
        for ing_name, qty in ingredients:
            ri = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient_map[ing_name].id,
                quantity=Decimal(str(qty)),
            )
            db.add(ri)
        recipe_map[name] = recipe
    db.flush()
    return recipe_map


def generate_purchases(db: Session, ingredient_map: dict[str, Ingredient], start_date: date, end_date: date):
    current = start_date
    supplier_map = {name: supplier for name, _, _, supplier in INGREDIENTS}

    while current <= end_date:
        # Purchases happen 3x per week
        if current.weekday() in (0, 2, 4):
            for name, ingredient in ingredient_map.items():
                if random.random() < 0.7:  # not every ingredient every delivery
                    base_price = BASE_PRICES[name]
                    # Natural price drift over time (+5% over 6 months) + weekly noise
                    days_elapsed = (current - start_date).days
                    drift = 1 + (0.05 * days_elapsed / 180)
                    noise = random.gauss(1.0, 0.04)

                    # Inject anomalies on ~3% of purchases
                    is_anomaly = random.random() < 0.03
                    if is_anomaly:
                        noise = random.uniform(1.25, 1.60)  # big spike

                    unit_price = round(base_price * drift * noise, 4)
                    quantity = round(random.uniform(5, 30), 2)

                    purchase = Purchase(
                        ingredient_id=ingredient.id,
                        supplier=supplier_map[name],
                        purchase_date=current,
                        quantity=Decimal(str(quantity)),
                        unit_price=Decimal(str(unit_price)),
                        is_anomaly=is_anomaly,
                    )
                    db.add(purchase)
        current += timedelta(days=1)
    db.flush()


def generate_sales(db: Session, recipe_map: dict[str, Recipe], start_date: date, end_date: date):
    current = start_date
    while current <= end_date:
        # More sales on weekends
        weekend_boost = 1.4 if current.weekday() >= 4 else 1.0
        # Seasonal boost in summer (June-August)
        summer_boost = 1.2 if current.month in (6, 7, 8) else 1.0

        for recipe_name, recipe in recipe_map.items():
            base_qty = DISH_POPULARITY[recipe_name]
            noise = random.gauss(1.0, 0.15)
            qty = max(1, int(base_qty * weekend_boost * summer_boost * noise))
            revenue = Decimal(str(round(qty * float(recipe.selling_price), 2)))
            sale = Sale(
                recipe_id=recipe.id,
                sale_date=current,
                quantity_sold=qty,
                revenue=revenue,
            )
            db.add(sale)
        current += timedelta(days=1)
    db.flush()


def generate_stock(db: Session, ingredient_map: dict[str, Ingredient]):
    for ingredient in ingredient_map.values():
        stock = Stock(
            ingredient_id=ingredient.id,
            quantity=Decimal(str(round(random.uniform(10, 50), 2))),
        )
        db.add(stock)
    db.flush()


def seed():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        # Clear existing data
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()

        print("Seeding ingredients...")
        ingredient_map = create_ingredient_map(db)

        print("Seeding recipes...")
        recipe_map = create_recipes(db, ingredient_map)

        end_date = date.today()
        start_date = end_date - timedelta(days=180)

        print(f"Generating purchases ({start_date} → {end_date})...")
        generate_purchases(db, ingredient_map, start_date, end_date)

        print(f"Generating sales ({start_date} → {end_date})...")
        generate_sales(db, recipe_map, start_date, end_date)

        print("Generating stock levels...")
        generate_stock(db, ingredient_map)

        db.commit()
        print("Seed complete.")


if __name__ == "__main__":
    seed()
