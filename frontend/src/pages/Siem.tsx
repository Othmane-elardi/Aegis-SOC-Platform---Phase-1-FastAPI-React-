import { useQuery } from "@tanstack/react-query";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Badge, Card, KpiCard, PageHeader } from "../components/ui";
import { api } from "../lib/api";

interface SiemEvent {
  id: string;
  timestamp: string;
  source: string;
  category: string;
  message: string;
  host: string;
  severity: string;
}
interface Overview {
  summary: {
    events_per_sec: number;
    events_today: number;
    sources_connected: number;
    storage_used_tb: number;
    retention_days: number;
    mode: "demo" | "wazuh";
    connected: boolean;
  };
  sources: { source: string; events: number }[];
  events: SiemEvent[];
}

const tooltipStyle = { background: "#111827", border: "1px solid #1f2a3d", borderRadius: 10, fontSize: 12, color: "#eef2f9" };

export default function Siem() {
  const { data, isLoading } = useQuery({
    queryKey: ["siem"],
    queryFn: async () => (await api.get<Overview>("/siem/overview")).data,
    refetchInterval: 15_000,
  });

  if (isLoading || !data) return <div className="text-muted">Chargement du SIEM…</div>;
  const s = data.summary;

  return (
    <div>
      <div className="mb-6 flex items-start justify-between gap-3">
        <PageHeader title="SIEM" subtitle="Ingestion et corrélation d'événements de sécurité multi-sources" />
        <span
          className={`mt-1 whitespace-nowrap rounded-lg border px-2.5 py-1 text-[11px] font-bold uppercase ${
            s.mode === "wazuh" && s.connected
              ? "border-low/40 bg-low/15 text-low"
              : s.mode === "wazuh"
                ? "border-crit/40 bg-crit/15 text-crit"
                : "border-info/40 bg-info/15 text-info"
          }`}
        >
          {s.mode === "wazuh" ? (s.connected ? "● Wazuh connecté" : "○ Wazuh injoignable") : "Mode démo"}
        </span>
      </div>

      <div className="mb-4 grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-5">
        <KpiCard icon="⚡" accent="brand" label="Événements / sec" value={s.events_per_sec.toLocaleString("fr-FR")} />
        <KpiCard icon="📥" accent="info" label="Événements aujourd'hui" value={new Intl.NumberFormat("fr-FR", { notation: "compact" }).format(s.events_today)} />
        <KpiCard icon="🔌" accent="low" label="Sources connectées" value={s.sources_connected} />
        <KpiCard icon="🗄" accent="med" label="Stockage utilisé" value={`${s.storage_used_tb} To`} />
        <KpiCard icon="🕒" accent="high" label="Rétention" value={`${s.retention_days} j`} />
      </div>

      <div className="mb-4 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="lg:col-span-1">
          <Card title="Volume par source">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={data.sources} layout="vertical" margin={{ left: 8, right: 16 }}>
                <XAxis type="number" tick={{ fontSize: 10, fill: "#6f7d98" }} />
                <YAxis dataKey="source" type="category" width={130} tick={{ fontSize: 10, fill: "#6f7d98" }} />
                <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "rgba(255,255,255,.03)" }} />
                <Bar dataKey="events" fill="#2dd4bf" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </div>

        <div className="lg:col-span-2">
          <Card title="Événements récents" badge="temps réel">
            <div className="max-h-[420px] overflow-auto">
              <table className="w-full text-[12.5px]">
                <thead className="sticky top-0 bg-surface">
                  <tr className="text-left text-[10.5px] uppercase tracking-wide text-muted">
                    <th className="py-2">Heure</th>
                    <th>Source</th>
                    <th>Message</th>
                    <th>Hôte</th>
                    <th>Sévérité</th>
                  </tr>
                </thead>
                <tbody>
                  {data.events.map((e) => (
                    <tr key={e.id} className="border-t border-border/60">
                      <td className="py-2 font-mono text-[11px] text-muted">{new Date(e.timestamp).toLocaleTimeString("fr-FR")}</td>
                      <td className="text-body">{e.source}</td>
                      <td className="max-w-[260px] truncate text-heading">{e.message}</td>
                      <td className="font-mono text-[11px] text-body">{e.host}</td>
                      <td>
                        <Badge kind="sev" value={e.severity} />
                      </td>
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
