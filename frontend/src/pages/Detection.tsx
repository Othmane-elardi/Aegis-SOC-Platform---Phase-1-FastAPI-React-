import { useQuery } from "@tanstack/react-query";
import { Badge, Card, KpiCard, PageHeader } from "../components/ui";
import { api } from "../lib/api";

interface Rule {
  id: string;
  name: string;
  mitre_tactic: string;
  mitre_id: string;
  severity: string;
  status: string;
  false_positive_rate: number;
  hits_7d: number;
  author: string;
  updated_at: string;
}
interface Overview {
  summary: { total: number; enabled: number; avg_fp_rate: number; hits_7d: number };
  rules: Rule[];
}

export default function Detection() {
  const { data, isLoading } = useQuery({
    queryKey: ["detection"],
    queryFn: async () => (await api.get<Overview>("/detection/overview")).data,
  });

  if (isLoading || !data) return <div className="text-muted">Chargement des règles de détection…</div>;
  const s = data.summary;

  return (
    <div>
      <PageHeader title="Detection Engineering" subtitle="Cycle de vie des règles de détection — précision, tuning, couverture MITRE" />

      <div className="mb-4 grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard icon="⟠" accent="brand" label="Règles totales" value={s.total} />
        <KpiCard icon="🟢" accent="low" label="Activées" value={s.enabled} />
        <KpiCard icon="⚠" accent="med" label="Taux faux positifs moyen" value={`${s.avg_fp_rate}%`} />
        <KpiCard icon="🎯" accent="info" label="Correspondances (7j)" value={s.hits_7d} />
      </div>

      <Card title="Règles de détection" badge={`${data.rules.length}`}>
        <table className="w-full text-[12.5px]">
          <thead>
            <tr className="text-left text-[10.5px] uppercase tracking-wide text-muted">
              <th className="py-2">Règle</th>
              <th>Tactique MITRE</th>
              <th>Sévérité</th>
              <th>Statut</th>
              <th>Faux positifs</th>
              <th>Hits (7j)</th>
              <th>Auteur</th>
            </tr>
          </thead>
          <tbody>
            {data.rules.map((r) => (
              <tr key={r.id} className="border-t border-border/60">
                <td className="py-2.5 text-heading">{r.name}</td>
                <td className="text-body">
                  <span className="font-mono text-[11px] text-muted">{r.mitre_id}</span> {r.mitre_tactic}
                </td>
                <td>
                  <Badge kind="sev" value={r.severity} />
                </td>
                <td>
                  <Badge kind="op" value={r.status} />
                </td>
                <td className="font-mono text-body">{r.false_positive_rate}%</td>
                <td className="font-mono font-bold text-high">{r.hits_7d}</td>
                <td className="text-body">{r.author}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
