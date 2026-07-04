import { useQuery } from "@tanstack/react-query";
import { Badge, Card, KpiCard, PageHeader } from "../components/ui";
import { api } from "../lib/api";

interface Hunt {
  id: string;
  hypothesis: string;
  status: string;
  analyst: string;
  mitre_tactic: string;
  findings: number;
  started_at: string;
}
interface Overview {
  summary: { total: number; active: number; findings_total: number; coverage_pct: number };
  hunts: Hunt[];
}

export default function Hunting() {
  const { data, isLoading } = useQuery({
    queryKey: ["hunting"],
    queryFn: async () => (await api.get<Overview>("/hunting/overview")).data,
  });

  if (isLoading || !data) return <div className="text-muted">Chargement des campagnes de chasse…</div>;
  const s = data.summary;

  return (
    <div>
      <PageHeader title="Threat Hunting" subtitle="Investigations proactives par hypothèse — au-delà des alertes automatiques" />

      <div className="mb-4 grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard icon="🎯" accent="brand" label="Campagnes de chasse" value={s.total} />
        <KpiCard icon="🔎" accent="info" label="En cours" value={s.active} />
        <KpiCard icon="🚩" accent="high" label="Découvertes totales" value={s.findings_total} />
        <KpiCard icon="📡" accent="low" label="Couverture MITRE" value={`${s.coverage_pct}%`} />
      </div>

      <Card title="Campagnes" badge={`${data.hunts.length}`}>
        <div className="space-y-2.5">
          {data.hunts.map((h) => (
            <div key={h.id} className="rounded-xl border border-border bg-surface2 px-4 py-3">
              <div className="flex items-start justify-between gap-3">
                <span className="text-[13px] font-semibold text-heading">{h.hypothesis}</span>
                <Badge kind="op" value={h.status} />
              </div>
              <div className="mt-1.5 flex items-center gap-3 text-[11px] text-muted">
                <span>{h.analyst}</span>
                <span>·</span>
                <span>Tactique : {h.mitre_tactic}</span>
                <span>·</span>
                <span>Démarré le {new Date(h.started_at).toLocaleDateString("fr-FR")}</span>
                <span className="ml-auto font-mono font-bold text-high">{h.findings} découverte(s)</span>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
