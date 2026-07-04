import { useQuery } from "@tanstack/react-query";
import { Badge, Card, KpiCard, PageHeader } from "../components/ui";
import { api } from "../lib/api";

interface Provider {
  id: string;
  name: string;
  protocol: string;
  status: string;
  connected_users: number;
  provisioning: string;
  last_sync: string;
  cert_expires_at: string | null;
}
interface Overview {
  summary: { providers_active: number; sso_logins_today: number; provisioned_users: number; cert_expiring_soon: number };
  providers: Provider[];
}

export default function Sso() {
  const { data, isLoading } = useQuery({
    queryKey: ["sso"],
    queryFn: async () => (await api.get<Overview>("/sso/overview")).data,
  });

  if (isLoading || !data) return <div className="text-muted">Chargement de la configuration SSO…</div>;
  const s = data.summary;

  return (
    <div>
      <PageHeader title="Identity & SSO" subtitle="Fournisseurs d'identité fédérée — SAML 2.0 / OIDC, provisioning SCIM" />

      <div className="mb-4 grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard icon="🔐" accent="brand" label="Fournisseurs actifs" value={s.providers_active} />
        <KpiCard icon="🔑" accent="info" label="Connexions SSO (jour)" value={s.sso_logins_today} />
        <KpiCard icon="👥" accent="low" label="Utilisateurs provisionnés" value={s.provisioned_users} />
        <KpiCard icon="⚠" accent="med" label="Certificats à renouveler" value={s.cert_expiring_soon} />
      </div>

      <Card title="Fournisseurs d'identité" badge={`${data.providers.length}`}>
        <div className="space-y-2.5">
          {data.providers.map((p) => (
            <div key={p.id} className="rounded-xl border border-border bg-surface2 px-4 py-3">
              <div className="flex items-center justify-between">
                <span className="text-[13px] font-semibold text-heading">{p.name}</span>
                <Badge kind="op" value={p.status} />
              </div>
              <div className="mt-1.5 flex flex-wrap gap-3 text-[11px] text-muted">
                <span className="rounded-md border border-border bg-bg px-1.5 py-0.5">{p.protocol}</span>
                <span>Provisioning : {p.provisioning}</span>
                <span>{p.connected_users} utilisateurs connectés</span>
                <span>Dernière synchro : {new Date(p.last_sync).toLocaleString("fr-FR")}</span>
                {p.cert_expires_at && <span>Certificat expire le {new Date(p.cert_expires_at).toLocaleDateString("fr-FR")}</span>}
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
