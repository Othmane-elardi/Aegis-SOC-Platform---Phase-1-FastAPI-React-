import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Badge, Card, KpiCard, PageHeader } from "../components/ui";
import { api } from "../lib/api";

interface VtResult {
  found?: boolean;
  error?: string;
  demo?: boolean;
  malicious?: number;
  suspicious?: number;
  total_engines?: number;
  verdict?: string;
  link?: string;
  message?: string;
}

interface Ioc {
  id: string;
  type: string;
  value: string;
  verdict: string;
  confidence: number;
  source: string;
  tags: string[];
  matches: number;
  status: string;
  added_at: string;
  expires_at: string;
}
interface Overview {
  summary: {
    total: number;
    active: number;
    expiring_soon: number;
    matches_today: number;
    false_positive_rate: number;
  };
  items: Ioc[];
}

const TYPES = ["", "ip", "domain", "hash", "url"];

const IOC_TYPES = [
  { value: "ip", label: "IP" }, { value: "domain", label: "Domaine" },
  { value: "sha256", label: "Hash (SHA256/MD5)" }, { value: "url", label: "URL" },
];

export default function Iocs() {
  const [type, setType] = useState("");
  const [lookupType, setLookupType] = useState("ip");
  const [lookupValue, setLookupValue] = useState("");
  const [vtResult, setVtResult] = useState<VtResult | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["iocs"],
    queryFn: async () => (await api.get<Overview>("/iocs/overview")).data,
  });

  const lookup = useMutation({
    mutationFn: async () => (await api.post<VtResult>("/iocs/lookup", { ioc_type: lookupType, ioc_value: lookupValue })).data,
    onSuccess: setVtResult,
  });

  if (isLoading || !data) return <div className="text-muted">Chargement des indicateurs…</div>;
  const s = data.summary;
  const items = type ? data.items.filter((i) => i.type === type) : data.items;

  return (
    <div>
      <PageHeader title="IOC Management" subtitle="Cycle de vie des indicateurs de compromission — ajout, expiration, correspondances" />

      <div className="mb-4 grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-5">
        <KpiCard icon="⬡" accent="brand" label="IOCs totaux" value={s.total} />
        <KpiCard icon="🟢" accent="low" label="Actifs" value={s.active} />
        <KpiCard icon="⏳" accent="med" label="Expirent sous 7j" value={s.expiring_soon} />
        <KpiCard icon="🎯" accent="info" label="Correspondances (jour)" value={s.matches_today} />
        <KpiCard icon="⚠" accent="high" label="Taux faux positifs" value={`${s.false_positive_rate}%`} />
      </div>

      <div className="mb-4">
        <Card title="Recherche VirusTotal" badge="enrichissement">
          <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
            <select className="input" value={lookupType} onChange={(e) => setLookupType(e.target.value)}>
              {IOC_TYPES.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
            <input
              className="input md:col-span-2"
              placeholder="Valeur à rechercher (ex. 185.220.101.5)"
              value={lookupValue}
              onChange={(e) => setLookupValue(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && lookupValue.trim() && lookup.mutate()}
            />
            <button className="btn-brand" disabled={!lookupValue.trim() || lookup.isPending} onClick={() => lookup.mutate()}>
              {lookup.isPending ? "Recherche…" : "Rechercher"}
            </button>
          </div>
          {vtResult && (
            <div className="mt-3 rounded-lg border border-border bg-surface2 px-3.5 py-2.5 text-[12.5px]">
              {vtResult.error ? (
                <span className="text-crit">{vtResult.error}</span>
              ) : vtResult.found === false ? (
                <span className="text-muted">{vtResult.message}</span>
              ) : (
                <span className="text-body">
                  Verdict : <b className={vtResult.verdict === "MALICIOUS" ? "text-crit" : vtResult.verdict === "SUSPICIOUS" ? "text-med" : "text-low"}>{vtResult.verdict}</b>
                  {" "}— {vtResult.malicious}/{vtResult.total_engines} moteurs malveillants
                  {vtResult.demo && <span className="ml-2 text-muted">(résultat simulé — VT_API_KEY non configuré)</span>}
                </span>
              )}
            </div>
          )}
        </Card>
      </div>

      <Card title="Indicateurs" badge={`${items.length} / ${data.items.length}`}>
        <div className="mb-3 flex flex-wrap gap-2">
          {TYPES.map((t) => (
            <button
              key={t}
              onClick={() => setType(t)}
              className={`rounded-lg border px-2.5 py-1 text-[11px] uppercase ${
                type === t ? "border-brand bg-brand/15 text-brand" : "border-border bg-surface2 text-muted"
              }`}
            >
              {t || "Tous types"}
            </button>
          ))}
        </div>
        <div className="max-h-[560px] overflow-auto">
          <table className="w-full text-[12.5px]">
            <thead className="sticky top-0 bg-surface">
              <tr className="text-left text-[10.5px] uppercase tracking-wide text-muted">
                <th className="py-2">Valeur</th>
                <th>Verdict</th>
                <th>Confiance</th>
                <th>Source</th>
                <th>Tags</th>
                <th>Correspondances</th>
                <th>Statut</th>
                <th>Expire</th>
              </tr>
            </thead>
            <tbody>
              {items.map((i) => (
                <tr key={i.id} className="border-t border-border/60">
                  <td className="py-2 max-w-[220px] truncate font-mono text-[11.5px] text-heading">{i.value}</td>
                  <td>
                    <Badge kind="verdict" value={i.verdict} />
                  </td>
                  <td className="font-mono text-body">{i.confidence}%</td>
                  <td className="text-body">{i.source}</td>
                  <td className="text-body">
                    <div className="flex flex-wrap gap-1">
                      {i.tags.map((t) => (
                        <span key={t} className="rounded-md border border-border bg-surface2 px-1.5 py-0.5 text-[10px] text-muted">
                          {t}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="font-mono font-bold text-high">{i.matches}</td>
                  <td>
                    <Badge kind="status" value={i.status} />
                  </td>
                  <td className="text-[11px] text-muted">{new Date(i.expires_at).toLocaleDateString("fr-FR")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
