import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Card, KpiCard, PageHeader } from "../components/ui";
import { api } from "../lib/api";

interface Insight {
  id: string;
  category: string;
  text: string;
  confidence: number;
  related_incident: string;
  generated_at: string;
}
interface Overview {
  summary: { insights_today: number; avg_confidence: number; incidents_auto_triaged: number; analyst_hours_saved: number };
  insights: Insight[];
}
interface AskResponse {
  question: string;
  answer: string;
  answered_at: string;
}

const SUGGESTIONS = [
  "Quels sont les incidents critiques ouverts ?",
  "Résume les vulnérabilités critiques",
  "Quel est notre score de conformité ?",
  "Quels sont les risques les plus élevés ?",
];

export default function Copilot() {
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState<AskResponse[]>([]);

  const { data, isLoading } = useQuery({
    queryKey: ["copilot"],
    queryFn: async () => (await api.get<Overview>("/copilot/overview")).data,
  });

  const ask = useMutation({
    mutationFn: async (q: string) => (await api.post<AskResponse>("/copilot/ask", { question: q })).data,
    onSuccess: (res) => setHistory((h) => [res, ...h]),
  });

  function submit(q: string) {
    if (!q.trim()) return;
    ask.mutate(q);
    setQuestion("");
  }

  if (isLoading || !data) return <div className="text-muted">Chargement de l'assistant IA…</div>;
  const s = data.summary;

  return (
    <div>
      <PageHeader title="AI Copilot" subtitle="Assistant IA — insights automatiques et réponses contextualisées sur vos données SOC" />

      <div className="mb-4 grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard icon="✨" accent="brand" label="Insights générés (jour)" value={s.insights_today} />
        <KpiCard icon="🎯" accent="info" label="Confiance moyenne" value={`${s.avg_confidence}%`} />
        <KpiCard icon="🤖" accent="low" label="Incidents auto-triés" value={s.incidents_auto_triaged} />
        <KpiCard icon="⏱" accent="med" label="Heures analyste économisées" value={s.analyst_hours_saved} />
      </div>

      <div className="mb-4">
        <Card title="Demander à Copilot">
          <div className="flex gap-2">
            <input
              className="input"
              placeholder="Posez une question sur vos incidents, vulnérabilités, risques ou conformité…"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && submit(question)}
            />
            <button className="btn-brand whitespace-nowrap" onClick={() => submit(question)} disabled={ask.isPending}>
              {ask.isPending ? "…" : "Envoyer"}
            </button>
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => submit(s)}
                className="rounded-lg border border-border bg-surface2 px-2.5 py-1 text-[11px] text-muted hover:text-heading"
              >
                {s}
              </button>
            ))}
          </div>
          {history.length > 0 && (
            <div className="mt-4 space-y-3 border-t border-border/60 pt-4">
              {history.map((h, i) => (
                <div key={i}>
                  <div className="text-[12.5px] font-semibold text-heading">🧑 {h.question}</div>
                  <div className="mt-1 rounded-xl border border-border bg-surface2 px-3.5 py-2.5 text-[12.5px] text-body">
                    ✨ {h.answer}
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      <Card title="Insights automatiques" badge={`${data.insights.length}`}>
        <div className="space-y-2">
          {data.insights.map((i) => (
            <div key={i.id} className="rounded-xl border border-border bg-surface2 px-4 py-2.5">
              <div className="flex items-start justify-between gap-3">
                <span className="text-[12.5px] text-heading">{i.text}</span>
                <span className="whitespace-nowrap font-mono text-[11px] font-bold text-brand">{i.confidence}%</span>
              </div>
              <div className="mt-1.5 flex gap-3 text-[11px] text-muted">
                <span className="rounded-md border border-border bg-bg px-1.5 py-0.5 uppercase">{i.category}</span>
                <span>{i.related_incident}</span>
                <span className="ml-auto">{new Date(i.generated_at).toLocaleString("fr-FR")}</span>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
