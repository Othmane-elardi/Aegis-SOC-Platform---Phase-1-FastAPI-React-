import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";
import { Badge, Card, PageHeader } from "../components/ui";

interface Incident {
  id: string;
  title: string;
  severity: string;
  status: string;
  asset: string;
  source_ip: string;
  mitre_tactic: string;
  risk_score: number;
  assignee: string | null;
  sla_breached: boolean;
  created_at: string;
}
interface IncidentList {
  items: Incident[];
  total: number;
  status_counts: Record<string, number>;
}

const SEVERITIES = ["", "critical", "high", "medium", "low"];
const STATUSES = ["", "new", "investigating", "contained", "resolved"];

export default function Incidents() {
  const [severity, setSeverity] = useState("");
  const [status, setStatus] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["incidents", severity, status],
    queryFn: async () =>
      (await api.get<IncidentList>("/incidents", { params: { severity: severity || undefined, status: status || undefined } })).data,
  });

  return (
    <div>
      <PageHeader title="Incident Management" subtitle="File d'incidents corrélés — triage, assignation, réponse" />

      <div className="mb-4 flex flex-wrap items-center gap-3">
        <select className="input max-w-[190px]" value={severity} onChange={(e) => setSeverity(e.target.value)}>
          {SEVERITIES.map((s) => (
            <option key={s} value={s}>
              {s ? s : "Toutes sévérités"}
            </option>
          ))}
        </select>
        <select className="input max-w-[190px]" value={status} onChange={(e) => setStatus(e.target.value)}>
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {s ? s : "Tous statuts"}
            </option>
          ))}
        </select>
        {data && (
          <div className="ml-auto flex gap-2 text-[11px] text-muted">
            {Object.entries(data.status_counts).map(([s, n]) => (
              <span key={s} className="rounded-lg border border-border bg-surface2 px-2.5 py-1">
                {s}: <b className="text-heading">{n}</b>
              </span>
            ))}
          </div>
        )}
      </div>

      <Card>
        {isLoading || !data ? (
          <div className="py-8 text-center text-muted">Chargement…</div>
        ) : (
          <table className="w-full text-[12.5px]">
            <thead>
              <tr className="text-left text-[10.5px] uppercase tracking-wide text-muted">
                <th className="py-2.5">ID</th>
                <th>Sévérité</th>
                <th>Titre</th>
                <th>Actif</th>
                <th>Tactique</th>
                <th>Assigné</th>
                <th>Statut</th>
                <th className="text-right">Risque</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((i) => (
                <tr key={i.id} className="cursor-pointer border-t border-border/60 hover:bg-surface2">
                  <td className="py-2.5 font-mono text-[11px] text-muted">{i.id}</td>
                  <td>
                    <Badge kind="sev" value={i.severity} />
                  </td>
                  <td className="max-w-[280px] truncate text-heading">
                    {i.sla_breached && <span className="mr-1 text-crit" title="SLA dépassé">⏱</span>}
                    {i.title}
                  </td>
                  <td className="font-mono text-[11px] text-body">{i.asset}</td>
                  <td className="text-body">{i.mitre_tactic}</td>
                  <td className="text-body">{i.assignee ?? <span className="text-muted">—</span>}</td>
                  <td>
                    <Badge kind="status" value={i.status} />
                  </td>
                  <td className="text-right font-mono font-bold text-high">{i.risk_score}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  );
}
