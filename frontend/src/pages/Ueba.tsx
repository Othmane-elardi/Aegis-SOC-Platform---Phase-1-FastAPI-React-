import { useQuery } from "@tanstack/react-query";
import { Badge, Card, KpiCard, PageHeader } from "../components/ui";
import { api } from "../lib/api";

interface Entity {
  id: string;
  name: string;
  department: string;
  risk_score: number;
  anomalies_7d: number;
  baseline_deviation_pct: number;
  last_anomaly: string;
}
interface Anomaly {
  id: string;
  entity: string;
  department: string;
  type: string;
  severity: string;
  detected_at: string;
}
interface Overview {
  summary: {
    entities_monitored: number;
    high_risk: number;
    anomalies_today: number;
    avg_risk_score: number;
  };
  entities: Entity[];
  anomalies: Anomaly[];
}

function riskColor(score: number) {
  return score >= 70 ? "#f0453f" : score >= 40 ? "#f5842a" : "#34d399";
}

export default function Ueba() {
  const { data, isLoading } = useQuery({
    queryKey: ["ueba"],
    queryFn: async () => (await api.get<Overview>("/ueba/overview")).data,
  });

  if (isLoading || !data) return <div className="text-muted">Chargement de l'analyse comportementale…</div>;
  const s = data.summary;

  return (
    <div>
      <PageHeader title="UEBA" subtitle="Analyse comportementale des utilisateurs et entités — détection d'anomalies" />

      <div className="mb-4 grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard icon="👣" accent="brand" label="Entités surveillées" value={s.entities_monitored} />
        <KpiCard icon="🔴" accent="crit" label="Risque élevé" value={s.high_risk} />
        <KpiCard icon="⚡" accent="high" label="Anomalies aujourd'hui" value={s.anomalies_today} />
        <KpiCard icon="📊" accent="med" label="Score de risque moyen" value={s.avg_risk_score} />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="Entités les plus à risque" badge={`${data.entities.length} suivies`}>
          <div className="max-h-[480px] overflow-auto">
            <table className="w-full text-[12.5px]">
              <thead className="sticky top-0 bg-surface">
                <tr className="text-left text-[10.5px] uppercase tracking-wide text-muted">
                  <th className="py-2">Entité</th>
                  <th>Département</th>
                  <th>Anomalies (7j)</th>
                  <th>Déviation</th>
                  <th className="text-right">Risque</th>
                </tr>
              </thead>
              <tbody>
                {data.entities.slice(0, 20).map((e) => (
                  <tr key={e.id} className="border-t border-border/60">
                    <td className="py-2 text-heading">{e.name}</td>
                    <td className="text-body">{e.department}</td>
                    <td className="font-mono text-body">{e.anomalies_7d}</td>
                    <td className="font-mono text-body">{e.baseline_deviation_pct > 0 ? "+" : ""}{e.baseline_deviation_pct}%</td>
                    <td className="text-right font-mono font-bold" style={{ color: riskColor(e.risk_score) }}>
                      {e.risk_score}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        <Card title="Anomalies détectées" badge={`${data.anomalies.length} récentes`}>
          <div className="max-h-[480px] space-y-2 overflow-auto">
            {data.anomalies.map((a) => (
              <div key={a.id} className="rounded-xl border border-border bg-surface2 px-4 py-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-[13px] font-semibold text-heading">{a.entity}</span>
                  <Badge kind="sev" value={a.severity} />
                </div>
                <div className="mt-1 text-[12px] text-body">{a.type}</div>
                <div className="mt-1 flex justify-between text-[11px] text-muted">
                  <span>{a.department}</span>
                  <span>{new Date(a.detected_at).toLocaleString("fr-FR")}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
