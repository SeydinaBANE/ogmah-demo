import { useEffect, useState } from "react";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis,
  Tooltip, CartesianGrid, ResponsiveContainer,
} from "recharts";
import { fetchJSON, KPI, DailySale, MarginReport } from "../api/client";

function KPICard({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-2xl font-semibold text-gray-900 mt-1">{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  );
}

export default function Dashboard() {
  const [kpi, setKpi] = useState<KPI | null>(null);
  const [sales, setSales] = useState<DailySale[]>([]);
  const [margins, setMargins] = useState<MarginReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      fetchJSON<KPI>("/sales/kpi"),
      fetchJSON<DailySale[]>("/sales/daily?days=30"),
      fetchJSON<MarginReport>("/recipes/margin-analysis"),
    ])
      .then(([kpiData, salesData, marginsData]) => {
        setKpi(kpiData);
        setSales(salesData);
        setMargins(marginsData);
      })
      .catch(() => setError("Erreur de chargement des données. Vérifiez que le backend est démarré."))
      .finally(() => setLoading(false));
  }, []);

  const topRecipes = margins?.recipes.slice(0, 8).map((r) => ({
    name: r.recipe_name.length > 18 ? r.recipe_name.slice(0, 18) + "…" : r.recipe_name,
    "Food Cost %": +(r.food_cost_ratio * 100).toFixed(1),
    fill: r.is_below_target ? "#ef4444" : "#22c55e",
  }));

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-sm text-gray-400">
        Chargement des données…
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-sm text-red-700">{error}</div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold text-gray-900">Tableau de bord</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPICard
          label="CA du mois"
          value={kpi ? `${kpi.monthly_revenue.toLocaleString("fr-FR", { maximumFractionDigits: 0 })} €` : "—"}
          sub={kpi ? `moy. ${kpi.daily_avg_revenue.toFixed(0)} €/jour` : undefined}
        />
        <KPICard
          label="Couverts du mois"
          value={kpi ? kpi.monthly_covers.toLocaleString("fr-FR") : "—"}
          sub={kpi ? `moy. ${kpi.daily_avg_covers.toFixed(0)}/jour` : undefined}
        />
        <KPICard
          label="Food cost moyen"
          value={margins ? `${(margins.avg_food_cost_ratio * 100).toFixed(1)} %` : "—"}
          sub="Objectif ≤ 30%"
        />
        <KPICard
          label="Recettes sous objectif"
          value={margins ? `${margins.below_target_count}` : "—"}
          sub={margins ? `Opportunité: ${margins.total_optimization_opportunity_eur.toFixed(0)} €/mois` : undefined}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="text-sm font-medium text-gray-700 mb-4">Ventes journalières (30 derniers jours)</h2>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={sales}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="sale_date"
                tickFormatter={(v) => new Date(v).toLocaleDateString("fr-FR", { day: "2-digit", month: "2-digit" })}
                tick={{ fontSize: 11 }}
              />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip
                formatter={(v: number) => [`${v.toFixed(0)} €`, "CA"]}
                labelFormatter={(l) => new Date(l).toLocaleDateString("fr-FR")}
              />
              <Line type="monotone" dataKey="total_revenue" stroke="#0284c7" strokeWidth={2} dot={false} name="CA (€)" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="text-sm font-medium text-gray-700 mb-4">Food Cost ratio par recette (cible ≤ 30%)</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={topRecipes} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis type="number" domain={[0, 50]} tick={{ fontSize: 11 }} unit="%" />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 10 }} width={120} />
              <Tooltip formatter={(v: number) => [`${v} %`, "Food Cost"]} />
              <Bar dataKey="Food Cost %" radius={[0, 4, 4, 0]}>
                {topRecipes?.map((entry, i) => (
                  <rect key={i} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
