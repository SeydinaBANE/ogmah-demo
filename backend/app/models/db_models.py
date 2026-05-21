from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import (
    String, Numeric, Integer, Date, DateTime, ForeignKey, Text, Boolean, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)  # kg, L, pcs
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # viande, légume, etc.
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    purchases: Mapped[list["Purchase"]] = relationship(back_populates="ingredient")
    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship(back_populates="ingredient")


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # entrée, plat, dessert
    selling_price: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship(back_populates="recipe")
    sales: Mapped[list["Sale"]] = relationship(back_populates="recipe")


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), nullable=False)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)  # in ingredient unit

    recipe: Mapped["Recipe"] = relationship(back_populates="recipe_ingredients")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="recipe_ingredients")


class Purchase(Base):
    """Records each supplier purchase with price per unit at time of purchase."""
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"), nullable=False)
    supplier: Mapped[str] = mapped_column(String(100), nullable=False)
    purchase_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)  # € per unit
    is_anomaly: Mapped[bool] = mapped_column(Boolean, default=False)
    anomaly_score: Mapped[float | None] = mapped_column(Numeric(6, 4), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    ingredient: Mapped["Ingredient"] = relationship(back_populates="purchases")


class Sale(Base):
    """Daily sales aggregated per recipe."""
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"), nullable=False)
    sale_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity_sold: Mapped[int] = mapped_column(Integer, nullable=False)
    revenue: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    recipe: Mapped["Recipe"] = relationship(back_populates="sales")


class Stock(Base):
    """Current stock level per ingredient."""
    __tablename__ = "stock"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"), nullable=False, unique=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    ingredient: Mapped["Ingredient"] = relationship()
