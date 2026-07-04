import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, KpiCard, PageHeader } from "../components/ui";
import { api } from "../lib/api";

interface App {
  id: string;
  name: string;
  vendor: string;
  category: string;
  description: string;
  status: string;
  rating: number;
  installs: number;
}
interface Overview {
  summary: { total: number; installed: number; categories: number; avg_rating: number };
  apps: App[];
}

export default function Marketplace() {
  const [category, setCategory] = useState("");
  const { data, isLoading } = useQuery({
    queryKey: ["marketplace"],
    queryFn: async () => (await api.get<Overview>("/marketplace/overview")).data,
  });

  if (isLoading || !data) return <div className="text-muted">Chargement du marketplace…</div>;
  const s = data.summary;
  const categories = Array.from(new Set(data.apps.map((a) => a.category)));
  const apps = category ? data.apps.filter((a) => a.category === category) : data.apps;

  return (
    <div>
      <PageHeader title="Marketplace" subtitle="Catalogue d'intégrations tierces — sources de logs, ticketing, threat intel, cloud" />

      <div className="mb-4 grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard icon="🧩" accent="brand" label="Intégrations disponibles" value={s.total} />
        <KpiCard icon="✅" accent="low" label="Installées" value={s.installed} />
        <KpiCard icon="🗂" accent="info" label="Catégories" value={s.categories} />
        <KpiCard icon="⭐" accent="med" label="Note moyenne" value={s.avg_rating} />
      </div>

      <Card title="Intégrations" badge={`${apps.length} / ${data.apps.length}`}>
        <div className="mb-4 flex flex-wrap gap-2">
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
              {c}
            </button>
          ))}
        </div>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
          {apps.map((a) => (
            <div key={a.id} className="flex flex-col rounded-xl border border-border bg-surface2 px-4 py-3.5">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="text-[13px] font-semibold text-heading">{a.name}</div>
                  <div className="text-[11px] text-muted">{a.vendor} · {a.category}</div>
                </div>
                <span className="whitespace-nowrap font-mono text-[11px] text-med">★ {a.rating}</span>
              </div>
              <p className="mt-2 flex-1 text-[11.5px] text-body">{a.description}</p>
              <div className="mt-3 flex items-center justify-between">
                <span className="text-[11px] text-muted">{a.installs.toLocaleString("fr-FR")} installations</span>
                <button
                  disabled={a.status === "installed"}
                  title="Démo — installation désactivée"
                  className="rounded-lg border border-border bg-bg px-2.5 py-1 text-[11px] text-muted disabled:opacity-50"
                >
                  {a.status === "installed" ? "Installé" : "Installer"}
                </button>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
