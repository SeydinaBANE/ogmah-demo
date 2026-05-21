import { useEffect, useState } from "react";
import {
  ComposedChart, Area, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import { fetchJSON, Recipe, ForecastResult } from "../api/client";

export default function ForecastChart() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [forecast, setForecast] = useState<ForecastResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchJSON<Recipe[]>("/recipes/")
      .then((data) => {
        setRecipes(data);
        if (data.length > 0) setSelectedId(data[0].id);
      })
      .catch(() => setError("Impossible de charger les recettes."));
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    setLoading(true);
    setError(null);
    fetchJSON<ForecastResult>(`/forecast/${selectedId}?days=30`)
      .then(setForecast)
      .catch(() => setError("Erreur lors du calcul des prévisions."))
      .finally(() => setLoading(false));
  }, [selectedId]);

  // Two separate keys for confidence interval — Recharts doesn't support array dataKey
  const chartData = forecast?.forecast.map((p) => ({
    date: new Date(p.forecast_date).toLocaleDateString("fr-FR", { day: "2-digit", month: "2-digit" }),
    "Prévision": +p.predicted_qty.toFixed(1),
    "upper_bound": +p.upper_bound.toFixed(1),
    "lower_bound": +p.lower_bound.toFixed(1),
  }));

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-gray-900">Prévision de demande</h1>
        <select
          value={selectedId ?? ""}
          onChange={(e) => setSelectedId(Number(e.target.value))}
          className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm"
        >
          {recipes.map((r) => (
            <option key={r.id} value={r.id}>{r.name}</option>
          ))}
        </select>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">{error}</div>
      )}

      {loading && <p className="text-sm text-gray-400">Calcul du modèle…</p>}

      {!loading && !error && !forecast && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 text-center text-yellow-700 text-sm">
          Pas de données suffisantes pour cette recette (minimum 14 jours d'historique requis).
        </div>
      )}

      {!loading && forecast && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-4 mb-4">
            <h2 className="font-medium text-gray-800">{forecast.recipe_name}</h2>
            <span className="text-xs text-gray-400">RMSE modèle : {forecast.model_rmse} portions/jour</span>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} label={{ value: "Portions/jour", angle: -90, position: "insideLeft", style: { fontSize: 11 } }} />
              <Tooltip
                formatter={(value: number, name: string) => {
                  if (name === "upper_bound") return [value, "Borne haute"];
                  if (name === "lower_bound") return [value, "Borne basse"];
                  return [value, name];
                }}
              />
              <Legend formatter={(value) => value === "upper_bound" ? "Intervalle de confiance" : value === "lower_bound" ? "" : value} />
              {/* Render upper bound filled, then lower bound in white to create a band effect */}
              <Area type="monotone" dataKey="upper_bound" stroke="#93c5fd" strokeWidth={0} fill="#bfdbfe" fillOpacity={0.4} legendType="rect" />
              <Area type="monotone" dataKey="lower_bound" stroke="#93c5fd" strokeWidth={0} fill="white" fillOpacity={1} legendType="none" />
              <Line
                type="monotone"
                dataKey="Prévision"
                stroke="#0284c7"
                strokeWidth={2}
                dot={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
