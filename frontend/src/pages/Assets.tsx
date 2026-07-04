import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { Card, KpiCard, PageHeader } from "../components/ui";
import { api } from "../lib/api";

interface Asset {
  id: string;
  hostname: string;
  type: string;
  ip: string;
  os: string;
  owner: string;
  criticality: string;
  risk_score: number;
  vulnerabilities: number;
  status: string;
  last_seen: string;
}
interface Overview {
  summary: {
    total: number;
    critical: number;
    at_risk: number;
    offline: number;
    by_type: Record<string, number>;
  };
  items: Asset[];
}

const CRIT_COLORS: Record<string, string> = { critical: "#f0453f", high: "#f5842a", medium: "#f5b729", low: "#34d399" };
const TYPE_COLORS: Record<string, string> = { workstation: "#5b8def", server: "#2dd4bf", network: "#f5b729", cloud: "#f5842a", container: "#34d399" };
const tooltipStyle = { background: "#111827", border: "1px solid #1f2a3d", borderRadius: 10, fontSize: 12, color: "#eef2f9" };

export default function Assets() {
  const [type, setType] = useState("");
  const { data, isLoading } = useQuery({
    queryKey: ["assets"],
    queryFn: async () => (await api.get<Overview>("/assets/overview")).data,
  });

  if (isLoading || !data) return <div className="text-muted">Chargement de l'inventaire…</div>;
  const s = data.summary;
  const typeData = Object.entries(s.by_type).map(([name, value]) => ({ name, value }));
  const items = type ? data.items.filter((a) => a.type === type) : data.items;

  return (
    <div>
      <PageHeader title="Asset Management" subtitle="Inventaire des actifs, criticité métier et exposition au risque" />

      <div className="mb-4 grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard icon="🖥" accent="brand" label="Actifs surveillés" value={s.total} />
        <KpiCard icon="🔴" accent="crit" label="Criticité critique" value={s.critical} />
        <KpiCard icon="⚠" accent="high" label="À risque (score ≥ 70)" value={s.at_risk} />
        <KpiCard icon="📴" accent="med" label="Hors ligne" value={s.offline} />
      </div>

      <div className="mb-4 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card title="Répartition par type">
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={typeData} dataKey="value" nameKey="name" innerRadius={45} outerRadius={80} paddingAngle={2}>
                {typeData.map((e) => (
                  <Cell key={e.name} fill={TYPE_COLORS[e.name] ?? "#5b8def"} stroke="none" />
                ))}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-2 flex flex-wrap justify-center gap-3 text-[11px]">
            {typeData.map((e) => (
              <button
                key={e.name}
                onClick={() => setType(type === e.name ? "" : e.name)}
                className="flex items-center gap-1.5 text-body hover:text-heading"
              >
                <span className="h-2.5 w-2.5 rounded-full" style={{ background: TYPE_COLORS[e.name] }} />
                {e.name} · <b className="text-heading">{e.value}</b>
              </button>
            ))}
          </div>
        </Card>

        <div className="lg:col-span-2">
          <Card title="Inventaire des actifs" badge={type ? `filtré : ${type}` : `${items.length} actifs`}>
            <div className="max-h-[420px] overflow-auto">
              <table className="w-full text-[12.5px]">
                <thead className="sticky top-0 bg-surface">
                  <tr className="text-left text-[10.5px] uppercase tracking-wide text-muted">
                    <th className="py-2">Hôte</th>
                    <th>Type</th>
                    <th>IP</th>
                    <th>Propriétaire</th>
                    <th>Criticité</th>
                    <th>Vulns</th>
                    <th className="text-right">Risque</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((a) => (
                    <tr key={a.id} className="border-t border-border/60">
                      <td className="py-2 font-mono text-[11.5px] text-heading">
                        <span
                          className="mr-1.5 inline-block h-1.5 w-1.5 rounded-full align-middle"
                          style={{ background: a.status === "online" ? "#34d399" : "#6f7d98" }}
                        />
                        {a.hostname}
                      </td>
                      <td className="text-body">{a.type}</td>
                      <td className="font-mono text-[11px] text-muted">{a.ip}</td>
                      <td className="text-body">{a.owner}</td>
                      <td>
                        <span className="font-semibold" style={{ color: CRIT_COLORS[a.criticality] }}>
                          {a.criticality}
                        </span>
                      </td>
                      <td className="font-mono text-body">{a.vulnerabilities}</td>
                      <td className="text-right font-mono font-bold text-high">{a.risk_score}</td>
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
