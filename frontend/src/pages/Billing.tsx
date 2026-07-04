import { useQuery } from "@tanstack/react-query";
import { Card, KpiCard, PageHeader } from "../components/ui";
import { api } from "../lib/api";

interface BillingInfo {
  plan: string;
  seats_total: number;
  seats_used: number;
  price_per_seat_eur: number;
  next_invoice_amount_eur: number;
  next_invoice_date: string;
  payment_method: string;
  usage: { api_calls_month: number; storage_gb: number; log_volume_gb_day: number };
}
interface Invoice {
  id: string;
  period: string;
  amount_eur: number;
  status: string;
  issued_at: string;
}
interface Overview {
  billing: BillingInfo;
  invoices: Invoice[];
}

export default function Billing() {
  const { data, isLoading } = useQuery({
    queryKey: ["billing"],
    queryFn: async () => (await api.get<Overview>("/billing/overview")).data,
  });

  if (isLoading || !data) return <div className="text-muted">Chargement de la facturation…</div>;
  const b = data.billing;

  return (
    <div>
      <PageHeader title="Billing & Subscription" subtitle="Plan, usage et historique de facturation du tenant" />

      <div className="mb-4 grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard icon="💳" accent="brand" label="Plan" value={b.plan} />
        <KpiCard icon="💺" accent="info" label="Sièges" value={`${b.seats_used}/${b.seats_total}`} />
        <KpiCard icon="🧾" accent="med" label="Prochaine facture" value={`${b.next_invoice_amount_eur.toLocaleString("fr-FR")} €`} />
        <KpiCard icon="📅" accent="low" label="Date de facturation" value={new Date(b.next_invoice_date).toLocaleDateString("fr-FR")} />
      </div>

      <div className="mb-4 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card title="Utilisation ce mois">
          <div className="space-y-3 text-[12.5px]">
            <div className="flex justify-between">
              <span className="text-body">Appels API</span>
              <span className="font-mono font-semibold text-heading">{b.usage.api_calls_month.toLocaleString("fr-FR")}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-body">Stockage</span>
              <span className="font-mono font-semibold text-heading">{b.usage.storage_gb} Go</span>
            </div>
            <div className="flex justify-between">
              <span className="text-body">Volume de logs</span>
              <span className="font-mono font-semibold text-heading">{b.usage.log_volume_gb_day} Go/jour</span>
            </div>
            <div className="border-t border-border/60 pt-3 flex justify-between">
              <span className="text-body">Prix par siège</span>
              <span className="font-mono font-semibold text-heading">{b.price_per_seat_eur} €/mois</span>
            </div>
            <div className="flex justify-between">
              <span className="text-body">Moyen de paiement</span>
              <span className="font-mono text-muted">{b.payment_method}</span>
            </div>
          </div>
        </Card>

        <div className="lg:col-span-2">
          <Card title="Historique de facturation" badge={`${data.invoices.length}`}>
            <table className="w-full text-[12.5px]">
              <thead>
                <tr className="text-left text-[10.5px] uppercase tracking-wide text-muted">
                  <th className="py-2">Facture</th>
                  <th>Période</th>
                  <th>Montant</th>
                  <th>Statut</th>
                  <th className="text-right">Action</th>
                </tr>
              </thead>
              <tbody>
                {data.invoices.map((inv) => (
                  <tr key={inv.id} className="border-t border-border/60">
                    <td className="py-2.5 font-mono text-[11px] text-muted">{inv.id}</td>
                    <td className="text-body capitalize">
                      {new Date(inv.period).toLocaleDateString("fr-FR", { month: "long", year: "numeric" })}
                    </td>
                    <td className="font-mono font-semibold text-heading">{inv.amount_eur.toLocaleString("fr-FR")} €</td>
                    <td className={inv.status === "paid" ? "font-bold text-low" : "font-bold text-med"}>
                      {inv.status === "paid" ? "Payée" : "En attente"}
                    </td>
                    <td className="text-right">
                      <button
                        title="Démo — téléchargement désactivé"
                        className="rounded-lg border border-border bg-surface2 px-2.5 py-1 text-[11px] text-muted"
                      >
                        PDF
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>
      </div>
    </div>
  );
}
