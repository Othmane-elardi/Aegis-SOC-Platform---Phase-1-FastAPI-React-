import { useQuery } from "@tanstack/react-query";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { Card, KpiCard, PageHeader } from "../components/ui";
import { api } from "../lib/api";

interface Risk {
  id: string;
  title: string;
  category: string;
  likelihood: number;
  impact: number;
  score: number;
  level: string;
  owner: string;
  status: string;
  updated_at: string;
}
interface Overview {
  summary: {
    total: number;
    critical_high: number;
    open: number;
    avg_score: number;
    by_category: Record<string, number>;
  };
  items: Risk[];
}

const LEVEL_COLORS: Record<string, string> = { critical: "#f0453f", high: "#f5842a", medium: "#f5b729", low: "#34d399" };
const CAT_COLORS = ["#5b8def", "#2dd4bf", "#f5b729", "#f5842a", "#34d399"];
const tooltipStyle = { background: "#111827", border: "1px solid #1f2a3d", borderRadius: 10, fontSize: 12, color: "#eef2f9" };

export default function Risk() {
  const { data, isLoading } = useQuery({
    queryKey: ["risk"],
    queryFn: async () => (await api.get<Overview>("/risk/overview")).data,
  });

  if (isLoading || !data) return <div className="text-muted">Chargement du registre des risques…</div>;
  const s = data.summary;
  const catData = Object.entries(s.by_category).map(([name, value]) => ({ name, value }));

  return (
    <div>
      <PageHeader title="Risk Management" subtitle="Registre des risques, évaluation probabilité × impact et traitement" />

      <div className="mb-4 grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard icon="📈" accent="brand" label="Risques suivis" value={s.total} />
        <KpiCard icon="🔴" accent="crit" label="Critiques / élevés" value={s.critical_high} />
        <KpiCard icon="🔓" accent="info" label="Ouverts" value={s.open} />
        <KpiCard icon="📊" accent="med" label="Score moyen" value={s.avg_score} />
      </div>

      <div className="mb-4 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card title="Répartition par catégorie">
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={catData} dataKey="value" nameKey="name" innerRadius={45} outerRadius={80} paddingAngle={2}>
                {catData.map((e, i) => (
                  <Cell key={e.name} fill={CAT_COLORS[i % CAT_COLORS.length]} stroke="none" />
                ))}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-2 flex flex-wrap justify-center gap-2.5 text-[11px]">
            {catData.map((e, i) => (
              <span key={e.name} className="flex items-center gap-1.5 text-body">
                <span className="h-2.5 w-2.5 rounded-full" style={{ background: CAT_COLORS[i % CAT_COLORS.length] }} />
                {e.name} · <b className="text-heading">{e.value}</b>
              </span>
            ))}
          </div>
        </Card>

        <div className="lg:col-span-2">
          <Card title="Registre des risques" badge={`${data.items.length}`}>
            <div className="max-h-[420px] overflow-auto">
              <table className="w-full text-[12.5px]">
                <thead className="sticky top-0 bg-surface">
                  <tr className="text-left text-[10.5px] uppercase tracking-wide text-muted">
                    <th className="py-2">Risque</th>
                    <th>Catégorie</th>
                    <th>P × I</th>
                    <th>Niveau</th>
                    <th>Propriétaire</th>
                    <th>Statut</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((r) => (
                    <tr key={r.id} className="border-t border-border/60">
                      <td className="max-w-[260px] truncate py-2 text-heading">{r.title}</td>
                      <td className="text-body">{r.category}</td>
                      <td className="font-mono text-body">{r.likelihood} × {r.impact} = {r.score}</td>
                      <td>
                        <span className="font-bold uppercase" style={{ color: LEVEL_COLORS[r.level] }}>
                          {r.level}
                        </span>
                      </td>
                      <td className="text-body">{r.owner}</td>
                      <td className="text-body">{r.status.replace("_", " ")}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
