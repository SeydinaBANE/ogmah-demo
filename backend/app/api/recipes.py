from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import Recipe, Sale
from app.ml.margin_optimizer import MarginOptimizer

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


class RecipeOut(BaseModel):
    id: int
    name: str
    category: str
    selling_price: float
    is_active: bool


class MarginOut(BaseModel):
    recipe_id: int
    recipe_name: str
    category: str
    selling_price: float
    ingredient_cost: float
    food_cost_ratio: float
    margin_pct: float
    is_below_target: bool
    optimization_opportunity_eur: float


class MarginReportOut(BaseModel):
    recipes: list[MarginOut]
    avg_food_cost_ratio: float
    below_target_count: int
    total_optimization_opportunity_eur: float


@router.get("/", response_model=list[RecipeOut])
def list_recipes(db: Session = Depends(get_db)):
    recipes = db.query(Recipe).filter(Recipe.is_active == True).all()
    return [RecipeOut(
        id=r.id, name=r.name, category=r.category,
        selling_price=float(r.selling_price), is_active=r.is_active
    ) for r in recipes]


@router.get("/margin-analysis", response_model=MarginReportOut)
def margin_analysis(db: Session = Depends(get_db)):
    optimizer = MarginOptimizer()
    report = optimizer.analyze(db)
    return MarginReportOut(
        recipes=[MarginOut(**vars(r)) for r in report.recipes],
        avg_food_cost_ratio=report.avg_food_cost_ratio,
        below_target_count=report.below_target_count,
        total_optimization_opportunity_eur=report.total_optimization_opportunity_eur,
    )
