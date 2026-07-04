import { useQuery } from "@tanstack/react-query";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Badge, Card, KpiCard, PageHeader } from "../components/ui";
import { api } from "../lib/api";

interface Tactic {
  id: string;
  tactic: string;
  count: number;
}
interface Technique {
  id: string;
  name: string;
  tactic_id: string;
  tactic: string;
  detections: number;
  coverage: string;
  incidents_mapped: number;
}
interface Overview {
  tactics: Tactic[];
  techniques: Technique[];
  summary: {
    total_techniques: number;
    covered: number;
    partial: number;
    not_covered: number;
    coverage_pct: number;
  };
}

const tooltipStyle = { background: "#111827", border: "1px solid #1f2a3d", borderRadius: 10, fontSize: 12, color: "#eef2f9" };

export default function Mitre() {
  const { data, isLoading } = useQuery({
    queryKey: ["mitre"],
    queryFn: async () => (await api.get<Overview>("/mitre/overview")).data,
  });

  if (isLoading || !data) return <div className="text-muted">Chargement de la matrice ATT&CK…</div>;
  const s = data.summary;

  return (
    <div>
      <PageHeader title="MITRE ATT&CK Center" subtitle="Couverture de détection cartographiée par tactique et technique" />

      <div className="mb-4 grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard icon="⛃" accent="brand" label="Techniques suivies" value={s.total_techniques} />
        <KpiCard icon="✅" accent="low" label="Couvertes" value={s.covered} />
        <KpiCard icon="◐" accent="med" label="Partielles" value={s.partial} />
        <KpiCard icon="⛔" accent="crit" label="Non couvertes" value={s.not_covered} hint={`Couverture globale ${s.coverage_pct}%`} />
      </div>

      <div className="mb-4">
        <Card title="Volume de détections par tactique">
          <ResponsiveContainer width="100%" height={230}>
            <BarChart data={data.tactics} margin={{ left: -18, right: 8 }}>
              <XAxis dataKey="tactic" tick={{ fontSize: 9, fill: "#6f7d98" }} interval={0} angle={-25} textAnchor="end" height={60} />
              <YAxis tick={{ fontSize: 10, fill: "#6f7d98" }} />
              <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "rgba(255,255,255,.03)" }} />
              <Bar dataKey="count" fill="#5b8def" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <Card title="Techniques ATT&CK" badge={`${data.techniques.length} techniques`}>
        <table className="w-full text-[12.5px]">
          <thead>
            <tr className="text-left text-[10.5px] uppercase tracking-wide text-muted">
              <th className="py-2">ID</th>
              <th>Technique</th>
              <th>Tactique</th>
              <th>Détections</th>
              <th>Incidents liés</th>
              <th>Couverture</th>
            </tr>
          </thead>
          <tbody>
            {data.techniques.map((t) => (
              <tr key={t.id} className="border-t border-border/60">
                <td className="py-2 font-mono text-[11px] text-muted">{t.id}</td>
                <td className="text-heading">{t.name}</td>
                <td className="text-body">{t.tactic}</td>
                <td className="font-mono text-body">{t.detections}</td>
                <td className="font-mono text-body">{t.incidents_mapped}</td>
                <td>
                  <Badge kind="coverage" value={t.coverage} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
