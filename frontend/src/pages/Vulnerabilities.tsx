import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Badge, Card, KpiCard, PageHeader } from "../components/ui";
import { api } from "../lib/api";

interface Vuln {
  id: string;
  title: string;
  cvss: number;
  severity: string;
  asset: string;
  status: string;
  exploit_available: boolean;
  published_at: string;
  days_open: number;
}
interface Overview {
  summary: {
    total: number;
    open: number;
    critical_open: number;
    exploit_available: number;
    patch_compliance_pct: number;
    avg_days_to_patch: number;
  };
  items: Vuln[];
}

const STATUSES = ["", "open", "patching", "patched", "accepted_risk"];

export default function Vulnerabilities() {
  const [status, setStatus] = useState("");
  const { data, isLoading } = useQuery({
    queryKey: ["vulnerabilities"],
    queryFn: async () => (await api.get<Overview>("/vulnerabilities/overview")).data,
  });

  if (isLoading || !data) return <div className="text-muted">Chargement des vulnérabilités…</div>;
  const s = data.summary;
  const items = status ? data.items.filter((v) => v.status === status) : data.items;

  return (
    <div>
      <PageHeader title="Vulnerability Management" subtitle="Exposition CVE, priorisation et cycle de remédiation" />

      <div className="mb-4 grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-6">
        <KpiCard icon="🐞" accent="brand" label="Vulnérabilités totales" value={s.total} />
        <KpiCard icon="🔓" accent="info" label="Ouvertes" value={s.open} />
        <KpiCard icon="🔴" accent="crit" label="Critiques ouvertes" value={s.critical_open} />
        <KpiCard icon="💣" accent="high" label="Exploit disponible" value={s.exploit_available} />
        <KpiCard icon="✅" accent="low" label="Conformité patch" value={`${s.patch_compliance_pct}%`} />
        <KpiCard icon="⏱" accent="med" label="Délai moyen (j)" value={s.avg_days_to_patch} />
      </div>

      <Card title="CVE recensées" badge={`${items.length} / ${data.items.length}`}>
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
        <div className="max-h-[520px] overflow-auto">
          <table className="w-full text-[12.5px]">
            <thead className="sticky top-0 bg-surface">
              <tr className="text-left text-[10.5px] uppercase tracking-wide text-muted">
                <th className="py-2">CVE</th>
                <th>Titre</th>
                <th>CVSS</th>
                <th>Sévérité</th>
                <th>Actif</th>
                <th>Statut</th>
                <th className="text-right">Jours ouverts</th>
              </tr>
            </thead>
            <tbody>
              {items.map((v) => (
                <tr key={v.id} className="border-t border-border/60">
                  <td className="py-2 font-mono text-[11px] text-muted">{v.id}</td>
                  <td className="max-w-[320px] truncate text-heading">
                    {v.exploit_available && <span className="mr-1 text-crit" title="Exploit disponible">💣</span>}
                    {v.title}
                  </td>
                  <td className="font-mono font-bold text-high">{v.cvss}</td>
                  <td>
                    <Badge kind="sev" value={v.severity} />
                  </td>
                  <td className="font-mono text-[11px] text-body">{v.asset}</td>
                  <td>
                    <Badge kind="status" value={v.status} />
                  </td>
                  <td className="text-right font-mono text-body">{v.days_open || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
