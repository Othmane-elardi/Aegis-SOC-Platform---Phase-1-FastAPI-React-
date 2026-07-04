import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Badge, Card, KpiCard, PageHeader } from "../components/ui";
import { api } from "../lib/api";

interface CaseItem {
  id: string;
  title: string;
  priority: string;
  status: string;
  analyst: string;
  related_incidents: number;
  created_at: string;
  due_at: string;
  overdue: boolean;
}
interface Overview {
  summary: { total: number; open: number; overdue: number; closed: number };
  items: CaseItem[];
}

const STATUSES = ["", "open", "in_review", "closed"];

export default function Cases() {
  const [status, setStatus] = useState("");
  const { data, isLoading } = useQuery({
    queryKey: ["cases"],
    queryFn: async () => (await api.get<Overview>("/cases/overview")).data,
  });

  if (isLoading || !data) return <div className="text-muted">Chargement des dossiers d'investigation…</div>;
  const s = data.summary;
  const items = status ? data.items.filter((c) => c.status === status) : data.items;

  return (
    <div>
      <PageHeader title="Case Management" subtitle="Dossiers d'investigation regroupant incidents, preuves et suivi analyste" />

      <div className="mb-4 grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard icon="🗂" accent="brand" label="Dossiers totaux" value={s.total} />
        <KpiCard icon="🔓" accent="info" label="Ouverts" value={s.open} />
        <KpiCard icon="⏱" accent="crit" label="En retard (SLA)" value={s.overdue} />
        <KpiCard icon="✅" accent="low" label="Clôturés" value={s.closed} />
      </div>

      <Card title="Dossiers" badge={`${items.length} / ${data.items.length}`}>
        <div className="mb-3 flex flex-wrap gap-2">
          {STATUSES.map((st) => (
            <button
              key={st}
              onClick={() => setStatus(st)}
              className={`rounded-lg border px-2.5 py-1 text-[11px] ${
                status === st ? "border-brand bg-brand/15 text-brand" : "border-border bg-surface2 text-muted"
              }`}
            >
              {st ? st.replace("_", " ") : "Tous statuts"}
            </button>
          ))}
        </div>
        <div className="space-y-2">
          {items.map((c) => (
            <div key={c.id} className="flex items-center gap-3 rounded-xl border border-border bg-surface2 px-4 py-2.5">
              <Badge kind="sev" value={c.priority} />
              <span className="font-mono text-[11px] text-muted">{c.id}</span>
              <span className="max-w-[320px] truncate text-[13px] text-heading">
                {c.overdue && <span className="mr-1 text-crit" title="SLA dépassé">⏱</span>}
                {c.title}
              </span>
              <span className="text-[11px] text-body">{c.analyst}</span>
              <span className="font-mono text-[11px] text-muted">{c.related_incidents} incident(s)</span>
              <Badge kind="status" value={c.status} />
              <span className="ml-auto text-[11px] text-muted">échéance {new Date(c.due_at).toLocaleDateString("fr-FR")}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
