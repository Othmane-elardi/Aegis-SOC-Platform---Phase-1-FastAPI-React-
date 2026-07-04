import { useQuery } from "@tanstack/react-query";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "../lib/api";
import { Badge, Card, KpiCard, PageHeader } from "../components/ui";

interface SocData {
  kpis: {
    risk_score: number;
    risk_trend: number;
    open_incidents: number;
    critical_incidents: number;
    mttr_hours: number;
    mttd_minutes: number;
    sla_compliance: number;
    coverage_pct: number;
    assets_at_risk: number;
  };
  severity_breakdown: Record<string, number>;
  alert_trend: { date: string; total: number; critical: number; resolved: number }[];
  mitre_coverage: { tactic: string; count: number }[];
  analyst_workload: { name: string; open: number; in_progress: number; resolved_today: number }[];
  recent_incidents: { id: string; title: string; severity: string; status: string; asset: string; risk_score: number }[];
}

const SEV_COLORS: Record<string, string> = { critical: "#f0453f", high: "#f5842a", medium: "#f5b729", low: "#34d399" };
const tooltipStyle = { background: "#111827", border: "1px solid #1f2a3d", borderRadius: 10, fontSize: 12, color: "#eef2f9" };

export default function Overview() {
  const { data, isLoading } = useQuery({
    queryKey: ["soc"],
    queryFn: async () => (await api.get<SocData>("/dashboards/soc")).data,
    refetchInterval: 30_000,
  });

  if (isLoading || !data) return <div className="text-muted">Chargement du tableau de bord…</div>;
  const k = data.kpis;
  const sevData = Object.entries(data.severity_breakdown).map(([name, value]) => ({ name, value }));

  return (
    <div>
      <PageHeader title="SOC Dashboard" subtitle="Vue temps réel du centre d'opérations — corrélation, priorisation, réponse" />

      <div className="mb-4 grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-6">
        <KpiCard icon="🛡" accent="high" label="Score de risque global" value={`${k.risk_score}`} hint={`${k.risk_trend > 0 ? "▲" : "▼"} ${Math.abs(k.risk_trend)} pts / 7j`} />
        <KpiCard icon="⚑" accent="info" label="Incidents ouverts" value={k.open_incidents} />
        <KpiCard icon="🔴" accent="crit" label="Incidents critiques" value={k.critical_incidents} />
        <KpiCard icon="🛠" accent="brand" label="MTTR moyen" value={`${k.mttr_hours}h`} hint={`MTTD ${k.mttd_minutes} min`} />
        <KpiCard icon="✅" accent="low" label="Conformité SLA" value={`${k.sla_compliance}%`} />
        <KpiCard icon="📡" accent="brand" label="Couverture détection" value={`${k.coverage_pct}%`} hint={`${k.assets_at_risk} actifs à risque`} />
      </div>

      <div className="mb-4 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card title="Volume d'alertes (14 jours)" badge="temps réel">
            <ResponsiveContainer width="100%" height={240}>
              <AreaChart data={data.alert_trend} margin={{ left: -18, right: 8, top: 8 }}>
                <defs>
                  <linearGradient id="gTotal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#2dd4bf" stopOpacity={0.35} />
                    <stop offset="100%" stopColor="#2dd4bf" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#6f7d98" }} tickFormatter={(d) => d.slice(5)} />
                <YAxis tick={{ fontSize: 10, fill: "#6f7d98" }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Area type="monotone" dataKey="total" stroke="#2dd4bf" strokeWidth={2} fill="url(#gTotal)" />
                <Area type="monotone" dataKey="critical" stroke="#f0453f" strokeWidth={1.5} fillOpacity={0} />
              </AreaChart>
            </ResponsiveContainer>
          </Card>
        </div>
        <Card title="Répartition par sévérité">
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={sevData} dataKey="value" nameKey="name" innerRadius={55} outerRadius={90} paddingAngle={2}>
                {sevData.map((e) => (
                  <Cell key={e.name} fill={SEV_COLORS[e.name] ?? "#5b8def"} stroke="none" />
                ))}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-2 flex flex-wrap justify-center gap-3 text-[11px]">
            {sevData.map((e) => (
              <span key={e.name} className="flex items-center gap-1.5 text-body">
                <span className="h-2.5 w-2.5 rounded-full" style={{ background: SEV_COLORS[e.name] }} />
                {e.name} · <b className="text-heading">{e.value}</b>
              </span>
            ))}
          </div>
        </Card>
      </div>

      <div className="mb-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="Couverture MITRE ATT&CK" badge="par tactique">
          <ResponsiveContainer width="100%" height={230}>
            <BarChart data={data.mitre_coverage} margin={{ left: -18, right: 8 }}>
              <XAxis dataKey="tactic" tick={{ fontSize: 9, fill: "#6f7d98" }} interval={0} angle={-25} textAnchor="end" height={60} />
              <YAxis tick={{ fontSize: 10, fill: "#6f7d98" }} />
              <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "rgba(255,255,255,.03)" }} />
              <Bar dataKey="count" fill="#5b8def" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Charge par analyste">
          <table className="w-full text-[12.5px]">
            <thead>
              <tr className="text-left text-[10.5px] uppercase tracking-wide text-muted">
                <th className="py-2">Analyste</th>
                <th>Ouverts</th>
                <th>En cours</th>
                <th>Résolus (j)</th>
              </tr>
            </thead>
            <tbody>
              {data.analyst_workload.map((a) => (
                <tr key={a.name} className="border-t border-border/60">
                  <td className="py-2 font-medium text-heading">{a.name}</td>
                  <td>{a.open}</td>
                  <td>{a.in_progress}</td>
                  <td className="font-mono text-low">{a.resolved_today}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </div>

      <Card title="Incidents récents" badge="8 derniers">
        <div className="space-y-2">
          {data.recent_incidents.map((i) => (
            <div key={i.id} className="flex items-center gap-3 rounded-xl border border-border bg-surface2 px-4 py-2.5">
              <Badge kind="sev" value={i.severity} />
              <span className="font-mono text-[11px] text-muted">{i.id}</span>
              <span className="truncate text-[13px] text-heading">{i.title}</span>
              <span className="ml-auto font-mono text-[11px] text-muted">{i.asset}</span>
              <Badge kind="status" value={i.status} />
              <span className="w-10 text-right font-mono text-[12px] font-bold text-high">{i.risk_score}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
