import { useEffect, useState } from "react";
import { fetchJSON, Anomaly } from "../api/client";

function SeverityBadge({ pct }: { pct: number }) {
  const abs = Math.abs(pct);
  const [color, label] =
    abs >= 40 ? ["bg-red-100 text-red-700", "Critique"] :
    abs >= 25 ? ["bg-orange-100 text-orange-700", "Élevée"] :
                ["bg-yellow-100 text-yellow-700", "Modérée"];
  return <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${color}`}>{label}</span>;
}

export default function AnomalyPanel() {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = (d: number) => {
    setLoading(true);
    setError(null);
    fetchJSON<Anomaly[]>(`/anomalies/?days=${d}`)
      .then(setAnomalies)
      .catch(() => setError("Erreur lors de l'analyse des anomalies. Vérifiez que le backend est démarré."))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(days); }, [days]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-gray-900">Anomalies d'achat fournisseurs</h1>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm"
        >
          <option value={7}>7 derniers jours</option>
          <option value={30}>30 derniers jours</option>
          <option value={90}>90 derniers jours</option>
        </select>
      </div>

      {loading && <p className="text-sm text-gray-400">Analyse en cours…</p>}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">{error}</div>
      )}

      {!loading && !error && anomalies.length === 0 && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-6 text-center text-green-700">
          Aucune anomalie détectée sur la période.
        </div>
      )}

      {!loading && !error && anomalies.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                {["Ingrédient", "Fournisseur", "Date", "Prix unitaire", "Moy. 30j", "Écart", "Sévérité"].map(h => (
                  <th key={h} className="px-4 py-3 text-left font-medium text-gray-600">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {anomalies.map((a) => (
                <tr key={a.purchase_id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium">{a.ingredient_name}</td>
                  <td className="px-4 py-3 text-gray-600">{a.supplier}</td>
                  <td className="px-4 py-3 text-gray-600">
                    {new Date(a.purchase_date).toLocaleDateString("fr-FR")}
                  </td>
                  <td className="px-4 py-3 font-mono">{a.unit_price.toFixed(2)} €</td>
                  <td className="px-4 py-3 font-mono text-gray-500">{a.rolling_avg_price.toFixed(2)} €</td>
                  <td className="px-4 py-3">
                    <span className={a.price_deviation_pct > 0 ? "text-red-600 font-semibold" : "text-green-600 font-semibold"}>
                      {a.price_deviation_pct > 0 ? "+" : ""}{a.price_deviation_pct.toFixed(1)} %
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <SeverityBadge pct={a.price_deviation_pct} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
