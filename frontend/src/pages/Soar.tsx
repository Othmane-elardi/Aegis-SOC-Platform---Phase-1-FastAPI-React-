import { useQuery } from "@tanstack/react-query";
import { Badge, Card, KpiCard, PageHeader } from "../components/ui";
import { api } from "../lib/api";

interface Playbook {
  id: string;
  name: string;
  trigger: string;
  category: string;
  status: string;
  executions_30d: number;
  success_rate: number;
  avg_duration_sec: number;
  last_run: string;
}
interface Overview {
  summary: { total: number; active: number; executions_today: number; time_saved_hours: number };
  playbooks: Playbook[];
}

export default function Soar() {
  const { data, isLoading } = useQuery({
    queryKey: ["soar"],
    queryFn: async () => (await api.get<Overview>("/soar/overview")).data,
  });

  if (isLoading || !data) return <div className="text-muted">Chargement des playbooks…</div>;
  const s = data.summary;

  return (
    <div>
      <PageHeader title="SOAR Playbooks" subtitle="Automatisation de la réponse à incident — orchestration et exécution" />

      <div className="mb-4 grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard icon="⚙" accent="brand" label="Playbooks" value={s.total} />
        <KpiCard icon="🟢" accent="low" label="Actifs" value={s.active} />
        <KpiCard icon="▶" accent="info" label="Exécutions aujourd'hui" value={s.executions_today} />
        <KpiCard icon="⏱" accent="med" label="Temps économisé (h)" value={s.time_saved_hours} />
      </div>

      <Card title="Playbooks d'automatisation" badge={`${data.playbooks.length}`}>
        <table className="w-full text-[12.5px]">
          <thead>
            <tr className="text-left text-[10.5px] uppercase tracking-wide text-muted">
              <th className="py-2">Playbook</th>
              <th>Déclencheur</th>
              <th>Catégorie</th>
              <th>Statut</th>
              <th>Exécutions (30j)</th>
              <th>Taux de succès</th>
              <th>Durée moy.</th>
            </tr>
          </thead>
          <tbody>
            {data.playbooks.map((p) => (
              <tr key={p.id} className="border-t border-border/60">
                <td className="py-2.5 text-heading">{p.name}</td>
                <td className="max-w-[220px] truncate text-body">{p.trigger}</td>
                <td className="text-body">{p.category}</td>
                <td>
                  <Badge kind="op" value={p.status} />
                </td>
                <td className="font-mono text-body">{p.executions_30d}</td>
                <td className="font-mono font-bold text-low">{p.success_rate}%</td>
                <td className="font-mono text-body">{p.avg_duration_sec}s</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
