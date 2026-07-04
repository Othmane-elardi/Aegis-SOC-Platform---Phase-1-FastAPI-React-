import type { ModuleDef } from "../modules";
import { PageHeader } from "../components/ui";

export default function ModulePlaceholder({ module }: { module: ModuleDef }) {
  return (
    <div>
      <PageHeader title={module.label} subtitle={`Module « ${module.group} » — planifié dans la roadmap produit`} />
      <div className="card grid place-items-center py-20 text-center">
        <div className="mb-4 text-5xl opacity-40">{module.icon}</div>
        <div className="mb-1 rounded-lg bg-info/15 px-3 py-1 text-[11px] font-bold uppercase tracking-wider text-info">
          Roadmap
        </div>
        <h3 className="mt-3 font-display text-lg font-semibold text-heading">{module.label}</h3>
        <p className="mt-2 max-w-md text-sm text-muted">
          Ce module fait partie de la plateforme cible. L'architecture (API versionnée, RBAC, multi-tenant,
          composants UI) est déjà en place pour l'accueillir — il sera livré dans une prochaine itération.
        </p>
      </div>
    </div>
  );
}
