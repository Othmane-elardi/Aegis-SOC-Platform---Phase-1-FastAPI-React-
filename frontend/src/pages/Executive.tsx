import { useQuery } from "@tanstack/react-query";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../lib/api";
import { Card, KpiCard, PageHeader } from "../components/ui";

interface ExecData {
  kpis: {
    risk_score: number;
    sla_compliance: number;
    incidents_cost_eur: number;
    open_incidents: number;
    coverage_pct: number;
    compliance: Record<string, number>;
  };
  alert_trend: { date: string; total: number }[];
}

const tooltipStyle = { background: "#111827", border: "1px solid #1f2a3d", borderRadius: 10, fontSize: 12, color: "#eef2f9" };

export default function Executive() {
  const { data, isLoading } = useQuery({
    queryKey: ["exec"],
    queryFn: async () => (await api.get<ExecData>("/dashboards/executive")).data,
  });
  if (isLoading || !data) return <div className="text-muted">Chargement…</div>;
  const k = data.kpis;

  return (
    <div>
      <PageHeader title="Executive Dashboard" subtitle="Posture de sécurité, conformité et impact business — vue CISO" />

      <div className="mb-4 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <KpiCard icon="🛡" accent="high" label="Score de risque" value={k.risk_score} />
        <KpiCard icon="✅" accent="low" label="Conformité SLA" value={`${k.sla_compliance}%`} />
        <KpiCard icon="💶" accent="crit" label="Coût incidents (est.)" value={`${(k.incidents_cost_eur / 1000).toFixed(0)}k€`} />
        <KpiCard icon="📡" accent="brand" label="Couverture détection" value={`${k.coverage_pct}%`} />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card title="Tendance du volume d'alertes">
            <ResponsiveContainer width="100%" height={260}>
              <AreaChart data={data.alert_trend} margin={{ left: -18, right: 8, top: 8 }}>
                <defs>
                  <linearGradient id="gExec" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#5b8def" stopOpacity={0.35} />
                    <stop offset="100%" stopColor="#5b8def" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#6f7d98" }} tickFormatter={(d) => d.slice(5)} />
                <YAxis tick={{ fontSize: 10, fill: "#6f7d98" }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Area type="monotone" dataKey="total" stroke="#5b8def" strokeWidth={2} fill="url(#gExec)" />
              </AreaChart>
            </ResponsiveContainer>
          </Card>
        </div>

        <Card title="Conformité réglementaire">
          <div className="space-y-4 pt-1">
            {Object.entries(k.compliance).map(([name, pct]) => (
              <div key={name}>
                <div className="mb-1 flex justify-between text-[12px]">
                  <span className="text-body">{name}</span>
                  <span className="font-mono font-bold text-heading">{pct}%</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-surface2">
                  <div
                    className="h-full rounded-full"
                    style={{ width: `${pct}%`, background: pct >= 90 ? "#34d399" : pct >= 80 ? "#f5b729" : "#f5842a" }}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
