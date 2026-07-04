import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../lib/api";
import { Badge, Card, PageHeader } from "../components/ui";
import { useAuth } from "../lib/auth";

interface Incident {
  id: string;
  title: string;
  description: string;
  severity: string;
  status: string;
  verdict: string;
  asset: string;
  source_ip: string;
  mitre_tactic: string;
  risk_score: number;
  assignee: string | null;
  priority: string;
  tags: string[];
  ai_analysis: Record<string, unknown>;
  threat_intel: Record<string, unknown>;
  active_response: Record<string, unknown>;
  timeline: { timestamp: string; event: string; actor: string }[];
  notes: { ts: string; text: string; author: string }[];
  source: string;
  sla_breached: boolean;
  created_at: string;
  updated_at: string;
}
interface IncidentList {
  items: Incident[];
  total: number;
  status_counts: Record<string, number>;
}

const SEVERITIES = ["", "critical", "high", "medium", "low"];
const STATUSES = ["", "new", "investigating", "contained", "resolved"];

function IncidentDetail({ id, onClose }: { id: string; onClose: () => void }) {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [note, setNote] = useState("");

  const { data: inc, isLoading } = useQuery({
    queryKey: ["incident", id],
    queryFn: async () => (await api.get<Incident>(`/incidents/${id}`)).data,
  });

  const patch = useMutation({
    mutationFn: async (body: Partial<{ status: string; assignee: string; note: string }>) =>
      (await api.patch<Incident>(`/incidents/${id}`, body)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["incident", id] });
      queryClient.invalidateQueries({ queryKey: ["incidents"] });
      setNote("");
    },
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4" onClick={onClose}>
      <div className="max-h-[85vh] w-full max-w-2xl overflow-y-auto rounded-2xl border border-border bg-surface p-6" onClick={(e) => e.stopPropagation()}>
        {isLoading || !inc ? (
          <div className="py-10 text-center text-muted">Chargement…</div>
        ) : (
          <>
            <div className="mb-4 flex items-start justify-between gap-3">
              <div>
                <div className="font-mono text-[11px] text-muted">{inc.id}</div>
                <h2 className="mt-1 font-display text-lg font-semibold text-heading">{inc.title}</h2>
              </div>
              <button onClick={onClose} className="rounded-lg border border-border bg-surface2 px-2.5 py-1 text-[12px] text-muted">
                Fermer
              </button>
            </div>

            <div className="mb-4 flex flex-wrap items-center gap-2">
              <Badge kind="sev" value={inc.severity} />
              <Badge kind="status" value={inc.status} />
              <span className="font-mono text-[11px] text-muted">{inc.asset} · {inc.source_ip}</span>
              <span className="ml-auto font-mono text-[13px] font-bold text-high">Risque {inc.risk_score}</span>
            </div>

            <div className="mb-4 grid grid-cols-2 gap-3">
              <div>
                <label className="mb-1 block text-[11px] text-muted">Statut</label>
                <select
                  className="input"
                  value={inc.status}
                  onChange={(e) => patch.mutate({ status: e.target.value })}
                  disabled={patch.isPending}
                >
                  {STATUSES.filter((s) => s).map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="mb-1 block text-[11px] text-muted">Assigné à</label>
                <div className="flex gap-2">
                  <input className="input" value={inc.assignee ?? ""} readOnly placeholder="Non assigné" />
                  <button
                    className="btn-brand whitespace-nowrap px-3 text-[12px]"
                    disabled={patch.isPending}
                    onClick={() => patch.mutate({ assignee: user?.full_name || user?.email || "" })}
                  >
                    M'assigner
                  </button>
                </div>
              </div>
            </div>

            <div className="mb-4">
              <label className="mb-1 block text-[11px] text-muted">Ajouter une note de réponse</label>
              <div className="flex gap-2">
                <input
                  className="input"
                  placeholder="Ex. IP source bloquée, hôte isolé, en attente de forensics…"
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && note.trim() && patch.mutate({ note })}
                />
                <button
                  className="btn-brand whitespace-nowrap px-3 text-[12px]"
                  disabled={!note.trim() || patch.isPending}
                  onClick={() => patch.mutate({ note })}
                >
                  Ajouter
                </button>
              </div>
            </div>

            {inc.notes.length > 0 && (
              <div className="mb-4">
                <div className="mb-1.5 text-[11px] font-bold uppercase tracking-wide text-muted">Notes analyste</div>
                <div className="space-y-1.5">
                  {inc.notes.map((n, i) => (
                    <div key={i} className="rounded-lg border border-border bg-surface2 px-3 py-2 text-[12px] text-body">
                      <span className="font-semibold text-heading">{n.author}</span> — {n.text}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {Object.keys(inc.ai_analysis).length > 0 && (
              <div className="mb-4 rounded-lg border border-brand/30 bg-brand/5 px-3.5 py-3">
                <div className="mb-1.5 text-[11px] font-bold uppercase tracking-wide text-brand">Analyse IA</div>
                <div className="text-[12.5px] text-body">
                  {String((inc.ai_analysis as Record<string, unknown>).explanation ?? "")}
                </div>
                {Array.isArray((inc.ai_analysis as Record<string, unknown>).recommendations) && (
                  <ul className="mt-1.5 list-inside list-disc text-[12px] text-body">
                    {((inc.ai_analysis as Record<string, unknown>).recommendations as string[]).map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            {Object.keys(inc.threat_intel).length > 0 && (
              <div className="mb-4">
                <div className="mb-1.5 text-[11px] font-bold uppercase tracking-wide text-muted">Threat Intel (VirusTotal)</div>
                <div className="space-y-1">
                  {Object.entries(inc.threat_intel).map(([key, val]) => (
                    <div key={key} className="rounded-lg border border-border bg-surface2 px-3 py-1.5 text-[12px] text-body">
                      {key} — {JSON.stringify(val)}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {Object.keys(inc.active_response).length > 0 && (
              <div className="mb-4 rounded-lg border border-border bg-surface2 px-3.5 py-2.5 text-[12.5px] text-body">
                <span className="font-bold uppercase text-muted">Réponse active : </span>
                {String((inc.active_response as Record<string, unknown>).action_label ?? "")} —{" "}
                {(inc.active_response as Record<string, unknown>).success ? "réussie" : "échouée"}
              </div>
            )}

            <div>
              <div className="mb-1.5 text-[11px] font-bold uppercase tracking-wide text-muted">Chronologie</div>
              <div className="space-y-1.5">
                {inc.timeline.map((t, i) => (
                  <div key={i} className="flex gap-3 text-[12px]">
                    <span className="w-32 shrink-0 font-mono text-muted">{new Date(t.timestamp).toLocaleString("fr-FR")}</span>
                    <span className="text-body">{t.event}</span>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default function Incidents() {
  const [severity, setSeverity] = useState("");
  const [status, setStatus] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);

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
                <tr key={i.id} onClick={() => setSelectedId(i.id)} className="cursor-pointer border-t border-border/60 hover:bg-surface2">
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

      {selectedId && <IncidentDetail id={selectedId} onClose={() => setSelectedId(null)} />}
    </div>
  );
}
