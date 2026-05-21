const BASE = "/api";

export async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json() as Promise<T>;
}

export async function postJSON<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json() as Promise<T>;
}

export interface KPI {
  monthly_revenue: number;
  monthly_covers: number;
  daily_avg_revenue: number;
  daily_avg_covers: number;
}

export interface DailySale {
  sale_date: string;
  total_revenue: number;
  total_covers: number;
}

export interface RecipeMargin {
  recipe_id: number;
  recipe_name: string;
  category: string;
  selling_price: number;
  ingredient_cost: number;
  food_cost_ratio: number;
  margin_pct: number;
  is_below_target: boolean;
  optimization_opportunity_eur: number;
}

export interface MarginReport {
  recipes: RecipeMargin[];
  avg_food_cost_ratio: number;
  below_target_count: number;
  total_optimization_opportunity_eur: number;
}

export interface Anomaly {
  purchase_id: number;
  ingredient_name: string;
  supplier: string;
  purchase_date: string;
  unit_price: number;
  rolling_avg_price: number;
  price_deviation_pct: number;
  anomaly_score: number;
}

export interface ForecastPoint {
  forecast_date: string;
  predicted_qty: number;
  lower_bound: number;
  upper_bound: number;
}

export interface ForecastResult {
  recipe_id: number;
  recipe_name: string;
  model_rmse: number;
  forecast: ForecastPoint[];
}

export interface Recipe {
  id: number;
  name: string;
  category: string;
  selling_price: number;
  is_active: boolean;
}
