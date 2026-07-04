import { useQuery } from "@tanstack/react-query";
import { Badge, Card, KpiCard, PageHeader } from "../components/ui";
import { api } from "../lib/api";

interface Framework {
  name: string;
  score: number;
  controls_total: number;
  controls_passed: number;
  controls_failed: number;
  last_audit: string;
  next_audit: string;
}
interface Control {
  id: string;
  framework: string;
  category: string;
  name: string;
  status: string;
  evidence_count: number;
  owner: string;
}
interface Overview {
  frameworks: Framework[];
  controls: Control[];
  summary: { overall_score: number; frameworks_tracked: number; controls_failed: number };
}

export default function Compliance() {
  const { data, isLoading } = useQuery({
    queryKey: ["compliance"],
    queryFn: async () => (await api.get<Overview>("/compliance/overview")).data,
  });

  if (isLoading || !data) return <div className="text-muted">Chargement du référentiel de conformité…</div>;
  const s = data.summary;

  return (
    <div>
      <PageHeader title="Compliance Center" subtitle="Suivi des référentiels réglementaires et des contrôles associés" />

      <div className="mb-4 grid grid-cols-2 gap-4 md:grid-cols-3">
        <KpiCard icon="✔" accent="brand" label="Score global" value={`${s.overall_score}%`} />
        <KpiCard icon="📋" accent="info" label="Référentiels suivis" value={s.frameworks_tracked} />
        <KpiCard icon="⛔" accent="crit" label="Contrôles en échec" value={s.controls_failed} />
      </div>

      <div className="mb-4 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        {data.frameworks.map((f) => (
          <Card key={f.name} title={f.name}>
            <div className="mb-2 flex items-baseline justify-between">
              <span className="font-mono text-[26px] font-bold text-heading">{f.score}%</span>
              <span className="text-[11px] text-muted">
                {f.controls_passed}/{f.controls_total} contrôles
              </span>
            </div>
            <div className="mb-3 h-2 overflow-hidden rounded-full bg-surface2">
              <div
                className="h-full rounded-full"
                style={{ width: `${f.score}%`, background: f.score >= 90 ? "#34d399" : f.score >= 80 ? "#f5b729" : "#f5842a" }}
              />
            </div>
            <div className="flex justify-between text-[11px] text-body">
              <span>Dernier audit : {new Date(f.last_audit).toLocaleDateString("fr-FR")}</span>
              <span>Prochain : {new Date(f.next_audit).toLocaleDateString("fr-FR")}</span>
            </div>
          </Card>
        ))}
      </div>

      <Card title="Contrôles" badge={`${data.controls.length}`}>
        <div className="max-h-[420px] overflow-auto">
          <table className="w-full text-[12.5px]">
            <thead className="sticky top-0 bg-surface">
              <tr className="text-left text-[10.5px] uppercase tracking-wide text-muted">
                <th className="py-2">ID</th>
                <th>Référentiel</th>
                <th>Catégorie</th>
                <th>Propriétaire</th>
                <th>Preuves</th>
                <th>Statut</th>
              </tr>
            </thead>
            <tbody>
              {data.controls.map((c) => (
                <tr key={c.id} className="border-t border-border/60">
                  <td className="py-2 font-mono text-[11px] text-muted">{c.id}</td>
                  <td className="text-body">{c.framework}</td>
                  <td className="text-heading">{c.category}</td>
                  <td className="text-body">{c.owner}</td>
                  <td className="font-mono text-body">{c.evidence_count}</td>
                  <td>
                    <Badge kind="compliance" value={c.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
