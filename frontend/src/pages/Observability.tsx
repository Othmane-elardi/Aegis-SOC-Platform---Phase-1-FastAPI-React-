import { useQuery } from "@tanstack/react-query";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Card, KpiCard, PageHeader } from "../components/ui";
import { api } from "../lib/api";

interface Service {
  name: string;
  status: string;
  uptime_pct_30d: number;
  latency_p95_ms: number;
}
interface Overview {
  summary: { overall_uptime_pct: number; avg_latency_ms: number; error_rate_pct: number; platform_incidents_30d: number };
  services: Service[];
  latency_trend: { time: string; p50: number; p95: number; p99: number }[];
}

const tooltipStyle = { background: "#111827", border: "1px solid #1f2a3d", borderRadius: 10, fontSize: 12, color: "#eef2f9" };

export default function Observability() {
  const { data, isLoading } = useQuery({
    queryKey: ["observability"],
    queryFn: async () => (await api.get<Overview>("/observability/overview")).data,
    refetchInterval: 30_000,
  });

  if (isLoading || !data) return <div className="text-muted">Chargement de l'observabilité…</div>;
  const s = data.summary;

  return (
    <div>
      <PageHeader title="Observability" subtitle="Santé de la plateforme — disponibilité, latence, taux d'erreur" />

      <div className="mb-4 grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard icon="📶" accent="brand" label="Disponibilité (30j)" value={`${s.overall_uptime_pct}%`} />
        <KpiCard icon="⚡" accent="info" label="Latence moyenne (p95)" value={`${s.avg_latency_ms} ms`} />
        <KpiCard icon="⚠" accent="med" label="Taux d'erreur" value={`${s.error_rate_pct}%`} />
        <KpiCard icon="🚨" accent="crit" label="Incidents plateforme (30j)" value={s.platform_incidents_30d} />
      </div>

      <div className="mb-4">
        <Card title="Latence API (24h)" badge="p50 / p95 / p99">
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={data.latency_trend} margin={{ left: -18, right: 8, top: 8 }}>
              <XAxis dataKey="time" tick={{ fontSize: 10, fill: "#6f7d98" }} interval={3} />
              <YAxis tick={{ fontSize: 10, fill: "#6f7d98" }} />
              <Tooltip contentStyle={tooltipStyle} />
              <Line type="monotone" dataKey="p50" stroke="#34d399" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="p95" stroke="#5b8def" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="p99" stroke="#f0453f" strokeWidth={1.5} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <Card title="Services" badge={`${data.services.length}`}>
        <table className="w-full text-[12.5px]">
          <thead>
            <tr className="text-left text-[10.5px] uppercase tracking-wide text-muted">
              <th className="py-2">Service</th>
              <th>Statut</th>
              <th>Disponibilité (30j)</th>
              <th className="text-right">Latence p95</th>
            </tr>
          </thead>
          <tbody>
            {data.services.map((svc) => (
              <tr key={svc.name} className="border-t border-border/60">
                <td className="py-2.5 text-heading">{svc.name}</td>
                <td>
                  <span className="flex items-center gap-1.5">
                    <span
                      className="h-2 w-2 rounded-full"
                      style={{ background: svc.status === "operational" ? "#34d399" : "#f5b729" }}
                    />
                    <span className="text-body">{svc.status === "operational" ? "Opérationnel" : "Dégradé"}</span>
                  </span>
                </td>
                <td className="font-mono text-body">{svc.uptime_pct_30d}%</td>
                <td className="text-right font-mono text-body">{svc.latency_p95_ms} ms</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
