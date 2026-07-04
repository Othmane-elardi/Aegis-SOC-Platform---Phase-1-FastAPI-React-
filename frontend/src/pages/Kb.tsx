import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, KpiCard, PageHeader } from "../components/ui";
import { api } from "../lib/api";

interface Article {
  id: string;
  title: string;
  category: string;
  module: string;
  author: string;
  views: number;
  updated_at: string;
}
interface Overview {
  summary: { total: number; categories: number; updated_7d: number; searches_today: number };
  articles: Article[];
}

const CATEGORY_LABELS: Record<string, string> = {
  playbook: "Playbook",
  procedure: "Procédure",
  "threat-profile": "Profil de menace",
  policy: "Politique",
};
const CATEGORY_ICONS: Record<string, string> = { playbook: "⚙", procedure: "📋", "threat-profile": "🕷", policy: "📜" };

export default function Kb() {
  const [category, setCategory] = useState("");
  const [search, setSearch] = useState("");
  const { data, isLoading } = useQuery({
    queryKey: ["kb"],
    queryFn: async () => (await api.get<Overview>("/kb/overview")).data,
  });

  if (isLoading || !data) return <div className="text-muted">Chargement de la base de connaissances…</div>;
  const s = data.summary;
  const categories = Array.from(new Set(data.articles.map((a) => a.category)));
  const items = data.articles.filter(
    (a) => (!category || a.category === category) && a.title.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <PageHeader title="Knowledge Base" subtitle="Playbooks, procédures et profils de menace — recherche augmentée (RAG)" />

      <div className="mb-4 grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard icon="📚" accent="brand" label="Articles" value={s.total} />
        <KpiCard icon="🗂" accent="info" label="Catégories" value={s.categories} />
        <KpiCard icon="🆕" accent="low" label="Mis à jour (7j)" value={s.updated_7d} />
        <KpiCard icon="🔎" accent="med" label="Recherches (jour)" value={s.searches_today} />
      </div>

      <Card title="Articles" badge={`${items.length} / ${data.articles.length}`}>
        <div className="mb-3 flex flex-wrap items-center gap-2">
          <input
            className="input max-w-[260px]"
            placeholder="Rechercher un article…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button
            onClick={() => setCategory("")}
            className={`rounded-lg border px-2.5 py-1 text-[11px] ${
              category === "" ? "border-brand bg-brand/15 text-brand" : "border-border bg-surface2 text-muted"
            }`}
          >
            Toutes catégories
          </button>
          {categories.map((c) => (
            <button
              key={c}
              onClick={() => setCategory(c)}
              className={`rounded-lg border px-2.5 py-1 text-[11px] ${
                category === c ? "border-brand bg-brand/15 text-brand" : "border-border bg-surface2 text-muted"
              }`}
            >
              {CATEGORY_LABELS[c] ?? c}
            </button>
          ))}
        </div>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          {items.map((a) => (
            <div key={a.id} className="rounded-xl border border-border bg-surface2 px-4 py-3">
              <div className="flex items-start gap-2">
                <span className="text-lg">{CATEGORY_ICONS[a.category] ?? "📄"}</span>
                <div className="min-w-0 flex-1">
                  <div className="truncate text-[13px] font-semibold text-heading">{a.title}</div>
                  <div className="mt-1 text-[11px] text-muted">
                    {a.module} · {a.author}
                  </div>
                </div>
              </div>
              <div className="mt-2 flex justify-between text-[11px] text-muted">
                <span>{a.views} vues</span>
                <span>Mis à jour le {new Date(a.updated_at).toLocaleDateString("fr-FR")}</span>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
