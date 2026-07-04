import { useQuery } from "@tanstack/react-query";
import { Badge, Card, KpiCard, PageHeader } from "../components/ui";
import { api } from "../lib/api";

interface WsIncident {
  id: string;
  title: string;
  severity: string;
  status: string;
  asset: string;
  risk_score: number;
}
interface WsCase {
  id: string;
  title: string;
  priority: string;
  status: string;
  related_incidents: number;
}
interface Workspace {
  analyst: string;
  kpis: { open_assigned: number; resolved_today: number; avg_response_min: number; sla_at_risk: number };
  incidents: WsIncident[];
  cases: WsCase[];
  shift: { team_on_duty: string; handover_at: string };
}

export default function AnalystWorkspace() {
  const { data, isLoading } = useQuery({
    queryKey: ["analyst-workspace"],
    queryFn: async () => (await api.get<Workspace>("/analyst/workspace")).data,
  });

  if (isLoading || !data) return <div className="text-muted">Chargement de l'espace de travail…</div>;
  const k = data.kpis;

  return (
    <div>
      <PageHeader title="Analyst Workspace" subtitle={`Bienvenue, ${data.analyst} — votre file personnelle`} />

      <div className="mb-4 grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard icon="📋" accent="brand" label="Incidents assignés" value={k.open_assigned} />
        <KpiCard icon="✅" accent="low" label="Résolus aujourd'hui" value={k.resolved_today} />
        <KpiCard icon="⚡" accent="info" label="Temps de réponse moyen" value={`${k.avg_response_min} min`} />
        <KpiCard icon="⏱" accent="crit" label="À risque SLA" value={k.sla_at_risk} />
      </div>

      <div className="mb-4 rounded-xl border border-border bg-surface2 px-4 py-2.5 text-[12px] text-body">
        Équipe de garde : <b className="text-heading">{data.shift.team_on_duty}</b> · relève à{" "}
        <b className="text-heading">{new Date(data.shift.handover_at).toLocaleTimeString("fr-FR")}</b>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="Mes incidents" badge={`${data.incidents.length}`}>
          <div className="space-y-2">
            {data.incidents.map((i) => (
              <div key={i.id} className="flex items-center gap-3 rounded-xl border border-border bg-surface2 px-4 py-2.5">
                <Badge kind="sev" value={i.severity} />
                <span className="min-w-0 flex-1 truncate text-[13px] text-heading">{i.title}</span>
                <span className="font-mono text-[11px] text-muted">{i.asset}</span>
                <Badge kind="status" value={i.status} />
                <span className="w-8 text-right font-mono text-[12px] font-bold text-high">{i.risk_score}</span>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Mes dossiers" badge={`${data.cases.length}`}>
          <div className="space-y-2">
            {data.cases.map((c) => (
              <div key={c.id} className="flex items-center gap-3 rounded-xl border border-border bg-surface2 px-4 py-2.5">
                <Badge kind="sev" value={c.priority} />
                <span className="min-w-0 flex-1 truncate text-[13px] text-heading">{c.title}</span>
                <span className="font-mono text-[11px] text-muted">{c.related_incidents} incident(s)</span>
                <Badge kind="status" value={c.status} />
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
