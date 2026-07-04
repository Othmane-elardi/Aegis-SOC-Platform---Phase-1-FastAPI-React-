import { useQuery } from "@tanstack/react-query";
import { Card, KpiCard, PageHeader } from "../components/ui";
import { api } from "../lib/api";

interface PlatformUser {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  tenant_id: string;
  created_at: string;
}
interface Overview {
  users: PlatformUser[];
  system: {
    mfa_enforced: boolean;
    sso_enabled: boolean;
    session_timeout_min: number;
    password_policy: string;
    api_keys_active: number;
    data_retention_days: number;
  };
  license: { plan: string; seats_used: number; seats_total: number; renews_at: string };
}

export default function Admin() {
  const { data, isLoading } = useQuery({
    queryKey: ["admin"],
    queryFn: async () => (await api.get<Overview>("/admin/overview")).data,
  });

  if (isLoading || !data) return <div className="text-muted">Chargement de l'administration…</div>;
  const { system, license } = data;

  return (
    <div>
      <PageHeader title="Administration" subtitle="Comptes de la plateforme, sécurité et licence — accès restreint aux administrateurs" />

      <div className="mb-4 grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard icon="👥" accent="brand" label="Comptes" value={data.users.length} />
        <KpiCard icon="🔑" accent="info" label="Clés API actives" value={system.api_keys_active} />
        <KpiCard icon="💺" accent="med" label="Licences utilisées" value={`${license.seats_used}/${license.seats_total}`} />
        <KpiCard icon="🛡" accent="low" label="MFA imposé" value={system.mfa_enforced ? "Oui" : "Non"} />
      </div>

      <div className="mb-4 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card title="Comptes utilisateurs" badge={`${data.users.length}`}>
            <table className="w-full text-[12.5px]">
              <thead>
                <tr className="text-left text-[10.5px] uppercase tracking-wide text-muted">
                  <th className="py-2">Nom</th>
                  <th>E-mail</th>
                  <th>Rôle</th>
                  <th>Statut</th>
                  <th>Créé le</th>
                </tr>
              </thead>
              <tbody>
                {data.users.map((u) => (
                  <tr key={u.id} className="border-t border-border/60">
                    <td className="py-2.5 text-heading">{u.full_name || "—"}</td>
                    <td className="font-mono text-[11.5px] text-body">{u.email}</td>
                    <td className="text-body uppercase">{u.role}</td>
                    <td className={u.is_active ? "font-bold text-low" : "font-bold text-muted"}>
                      {u.is_active ? "Actif" : "Désactivé"}
                    </td>
                    <td className="text-[11px] text-muted">{new Date(u.created_at).toLocaleDateString("fr-FR")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>

        <Card title="Sécurité & licence">
          <div className="space-y-3 text-[12.5px]">
            <div className="flex justify-between">
              <span className="text-body">SSO</span>
              <span className="font-semibold text-heading">{system.sso_enabled ? "Activé" : "Désactivé"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-body">Expiration session</span>
              <span className="font-semibold text-heading">{system.session_timeout_min} min</span>
            </div>
            <div className="flex justify-between">
              <span className="text-body">Rétention des données</span>
              <span className="font-semibold text-heading">{system.data_retention_days} j</span>
            </div>
            <div className="border-t border-border/60 pt-3 text-[11.5px] text-muted">{system.password_policy}</div>
            <div className="border-t border-border/60 pt-3">
              <div className="flex justify-between">
                <span className="text-body">Plan</span>
                <span className="font-semibold text-heading">{license.plan}</span>
              </div>
              <div className="mt-1 flex justify-between">
                <span className="text-body">Renouvellement</span>
                <span className="font-semibold text-heading">{new Date(license.renews_at).toLocaleDateString("fr-FR")}</span>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
