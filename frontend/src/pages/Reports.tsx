import { useQuery } from "@tanstack/react-query";
import { Card, KpiCard, PageHeader } from "../components/ui";
import { api } from "../lib/api";

interface Report {
  id: string;
  name: string;
  type: string;
  format: string;
  schedule: string;
  last_generated: string;
  recipients: number;
  status: string;
}
interface Overview {
  summary: { total: number; scheduled: number; generated_this_month: number; recipients_total: number };
  items: Report[];
}

const TYPE_LABELS: Record<string, string> = {
  executive: "Exécutif",
  compliance: "Conformité",
  "incident-summary": "Résumé incidents",
  custom: "Personnalisé",
};
const SCHEDULE_LABELS: Record<string, string> = { weekly: "Hebdomadaire", monthly: "Mensuel", quarterly: "Trimestriel" };

export default function Reports() {
  const { data, isLoading } = useQuery({
    queryKey: ["reports"],
    queryFn: async () => (await api.get<Overview>("/reports/overview")).data,
  });

  if (isLoading || !data) return <div className="text-muted">Chargement des rapports…</div>;
  const s = data.summary;

  return (
    <div>
      <PageHeader title="Reports Center" subtitle="Rapports planifiés et à la demande — exécutif, conformité, opérationnel" />

      <div className="mb-4 grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard icon="🖨" accent="brand" label="Rapports configurés" value={s.total} />
        <KpiCard icon="🗓" accent="info" label="Planifiés" value={s.scheduled} />
        <KpiCard icon="📄" accent="low" label="Générés ce mois" value={s.generated_this_month} />
        <KpiCard icon="👥" accent="med" label="Destinataires (total)" value={s.recipients_total} />
      </div>

      <Card title="Rapports" badge={`${data.items.length}`}>
        <table className="w-full text-[12.5px]">
          <thead>
            <tr className="text-left text-[10.5px] uppercase tracking-wide text-muted">
              <th className="py-2">Rapport</th>
              <th>Type</th>
              <th>Format</th>
              <th>Fréquence</th>
              <th>Dernière génération</th>
              <th>Destinataires</th>
              <th className="text-right">Action</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((r) => (
              <tr key={r.id} className="border-t border-border/60">
                <td className="py-2.5 text-heading">{r.name}</td>
                <td className="text-body">{TYPE_LABELS[r.type] ?? r.type}</td>
                <td className="font-mono text-[11px] text-muted">{r.format}</td>
                <td className="text-body">{SCHEDULE_LABELS[r.schedule] ?? r.schedule}</td>
                <td className="text-[11px] text-muted">{new Date(r.last_generated).toLocaleDateString("fr-FR")}</td>
                <td className="font-mono text-body">{r.recipients}</td>
                <td className="text-right">
                  <button
                    disabled={r.status === "generating"}
                    title="Démo — génération désactivée"
                    className="rounded-lg border border-border bg-surface2 px-2.5 py-1 text-[11px] text-muted disabled:opacity-50"
                  >
                    {r.status === "generating" ? "Génération…" : "Télécharger"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
