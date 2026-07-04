import { useQuery } from "@tanstack/react-query";
import { Badge, Card, KpiCard, PageHeader } from "../components/ui";
import { api } from "../lib/api";

interface ThreatActor {
  name: string;
  origin: string;
  motivation: string;
  sophistication: string;
  campaigns_active: number;
  iocs_linked: number;
  targeted_sectors: string[];
  last_seen: string;
}
interface Campaign {
  id: string;
  name: string;
  actor: string;
  target_sector: string;
  primary_tactic: string;
  iocs_count: number;
  status: string;
  started_at: string;
}
interface Indicator {
  type: string;
  value: string;
  verdict: string;
  sources: number;
  first_seen: string;
}
interface Overview {
  summary: {
    total_indicators: number;
    malicious_pct: number;
    new_today: number;
    active_campaigns: number;
    actors_tracked: number;
    feeds_connected: number;
  };
  actors: ThreatActor[];
  campaigns: Campaign[];
  feed: Indicator[];
}

export default function ThreatIntel() {
  const { data, isLoading } = useQuery({
    queryKey: ["threat-intel"],
    queryFn: async () => (await api.get<Overview>("/threat-intel/overview")).data,
    refetchInterval: 30_000,
  });

  if (isLoading || !data) return <div className="text-muted">Chargement du renseignement sur la menace…</div>;
  const s = data.summary;

  return (
    <div>
      <PageHeader title="Threat Intelligence" subtitle="Acteurs, campagnes et indicateurs de compromission agrégés multi-flux" />

      <div className="mb-4 grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-6">
        <KpiCard icon="🛰" accent="brand" label="Indicateurs totaux" value={s.total_indicators.toLocaleString("fr-FR")} />
        <KpiCard icon="☣" accent="crit" label="Malveillants" value={`${s.malicious_pct}%`} />
        <KpiCard icon="🆕" accent="info" label="Nouveaux aujourd'hui" value={s.new_today} />
        <KpiCard icon="🎯" accent="high" label="Campagnes actives" value={s.active_campaigns} />
        <KpiCard icon="🕷" accent="med" label="Acteurs suivis" value={s.actors_tracked} />
        <KpiCard icon="🔌" accent="low" label="Flux connectés" value={s.feeds_connected} />
      </div>

      <div className="mb-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="Acteurs de la menace" badge={`${data.actors.length} suivis`}>
          <div className="space-y-2.5">
            {data.actors.map((a) => (
              <div key={a.name} className="rounded-xl border border-border bg-surface2 px-4 py-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-[13px] font-semibold text-heading">{a.name}</span>
                  <span className="font-mono text-[11px] text-muted">{a.campaigns_active} campagne(s)</span>
                </div>
                <div className="mt-1 flex flex-wrap items-center gap-2 text-[11px] text-body">
                  <span>{a.origin}</span> · <span>{a.motivation}</span> ·
                  <span className="font-mono text-muted">{a.iocs_linked} IOCs</span>
                </div>
                <div className="mt-1.5 flex flex-wrap gap-1.5">
                  {a.targeted_sectors.map((sec) => (
                    <span key={sec} className="rounded-md border border-border bg-bg px-1.5 py-0.5 text-[10px] text-muted">
                      {sec}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Campagnes suivies" badge={`${data.campaigns.length}`}>
          <div className="space-y-2">
            {data.campaigns.map((c) => (
              <div key={c.id} className="flex items-center gap-3 rounded-xl border border-border bg-surface2 px-4 py-2.5">
                <Badge kind="status" value={c.status} />
                <div className="min-w-0 flex-1">
                  <div className="truncate text-[13px] text-heading">{c.name}</div>
                  <div className="text-[11px] text-muted">{c.actor} · {c.target_sector} · {c.primary_tactic}</div>
                </div>
                <span className="font-mono text-[11px] text-muted">{c.iocs_count} IOCs</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Card title="Flux d'indicateurs (IOC)" badge="20 derniers">
        <table className="w-full text-[12.5px]">
          <thead>
            <tr className="text-left text-[10.5px] uppercase tracking-wide text-muted">
              <th className="py-2">Type</th>
              <th>Valeur</th>
              <th>Verdict</th>
              <th>Sources</th>
              <th>Première détection</th>
            </tr>
          </thead>
          <tbody>
            {data.feed.map((f, i) => (
              <tr key={i} className="border-t border-border/60">
                <td className="py-2 font-mono text-[11px] uppercase text-muted">{f.type}</td>
                <td className="max-w-[280px] truncate font-mono text-[11.5px] text-heading">{f.value}</td>
                <td>
                  <Badge kind="verdict" value={f.verdict} />
                </td>
                <td className="text-body">{f.sources}</td>
                <td className="text-body">{new Date(f.first_seen).toLocaleDateString("fr-FR")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
