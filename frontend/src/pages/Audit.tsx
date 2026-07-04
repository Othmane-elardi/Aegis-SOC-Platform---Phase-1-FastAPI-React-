import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, KpiCard, PageHeader } from "../components/ui";
import { api } from "../lib/api";

interface AuditEntry {
  id: string;
  timestamp: string;
  actor: string;
  action: string;
  target: string;
  ip_address: string;
  result: string;
}
interface Overview {
  summary: { events_today: number; failed_logins_24h: number; admin_actions_7d: number; exports_7d: number };
  items: AuditEntry[];
}

export default function Audit() {
  const [onlyFailed, setOnlyFailed] = useState(false);
  const { data, isLoading } = useQuery({
    queryKey: ["audit"],
    queryFn: async () => (await api.get<Overview>("/audit/overview")).data,
  });

  if (isLoading || !data) return <div className="text-muted">Chargement du journal d'audit…</div>;
  const s = data.summary;
  const items = onlyFailed ? data.items.filter((a) => a.result === "failed") : data.items;

  return (
    <div>
      <PageHeader title="Audit Center" subtitle="Journal des actions utilisateurs et système — traçabilité complète" />

      <div className="mb-4 grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard icon="🧾" accent="brand" label="Événements aujourd'hui" value={s.events_today} />
        <KpiCard icon="🔒" accent="crit" label="Échecs de connexion (24h)" value={s.failed_logins_24h} />
        <KpiCard icon="🛡" accent="med" label="Actions admin (7j)" value={s.admin_actions_7d} />
        <KpiCard icon="📤" accent="info" label="Exports (7j)" value={s.exports_7d} />
      </div>

      <Card title="Journal" badge={`${items.length} / ${data.items.length}`}>
        <div className="mb-3">
          <button
            onClick={() => setOnlyFailed((v) => !v)}
            className={`rounded-lg border px-2.5 py-1 text-[11px] ${
              onlyFailed ? "border-crit bg-crit/15 text-crit" : "border-border bg-surface2 text-muted"
            }`}
          >
            {onlyFailed ? "Échecs uniquement" : "Tous les événements"}
          </button>
        </div>
        <div className="max-h-[560px] overflow-auto">
          <table className="w-full text-[12.5px]">
            <thead className="sticky top-0 bg-surface">
              <tr className="text-left text-[10.5px] uppercase tracking-wide text-muted">
                <th className="py-2">Horodatage</th>
                <th>Acteur</th>
                <th>Action</th>
                <th>Cible</th>
                <th>IP</th>
                <th>Résultat</th>
              </tr>
            </thead>
            <tbody>
              {items.map((a) => (
                <tr key={a.id} className="border-t border-border/60">
                  <td className="py-2 font-mono text-[11px] text-muted">{new Date(a.timestamp).toLocaleString("fr-FR")}</td>
                  <td className="text-body">{a.actor}</td>
                  <td className="text-heading">{a.action}</td>
                  <td className="text-body">{a.target}</td>
                  <td className="font-mono text-[11px] text-muted">{a.ip_address}</td>
                  <td className={a.result === "failed" ? "font-bold uppercase text-crit" : "font-bold uppercase text-low"}>
                    {a.result}
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
