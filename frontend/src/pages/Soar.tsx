import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Badge, Card, KpiCard, PageHeader } from "../components/ui";
import { api } from "../lib/api";

interface Playbook {
  id: string;
  name: string;
  trigger: string;
  category: string;
  status: string;
  executions_30d: number;
  success_rate: number;
  avg_duration_sec: number;
  last_run: string;
}
interface Overview {
  summary: { total: number; active: number; executions_today: number; time_saved_hours: number };
  playbooks: Playbook[];
}
interface WazuhStatus {
  connected: boolean;
  demo_mode: boolean;
  wazuh_host: string;
}
interface TriggerResult {
  success: boolean;
  action_label?: string;
  agent_id?: string;
  error?: string;
  demo?: boolean;
  triggered_by: string;
}

const ACTIONS = [
  { value: "firewall-drop", label: "Blocage IP (firewall-drop)" },
  { value: "restart-wazuh-agent", label: "Redémarrage agent" },
  { value: "network-isolation", label: "Isolation réseau" },
];

export default function Soar() {
  const [agentName, setAgentName] = useState("");
  const [srcIp, setSrcIp] = useState("");
  const [action, setAction] = useState(ACTIONS[0].value);
  const [result, setResult] = useState<TriggerResult | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["soar"],
    queryFn: async () => (await api.get<Overview>("/soar/overview")).data,
  });

  const { data: wazuhStatus } = useQuery({
    queryKey: ["soar-status"],
    queryFn: async () => (await api.get<WazuhStatus>("/soar/status")).data,
    refetchInterval: 30_000,
  });

  const trigger = useMutation({
    mutationFn: async () => (await api.post<TriggerResult>("/soar/trigger", { agent_name: agentName, src_ip: srcIp, action })).data,
    onSuccess: setResult,
  });

  if (isLoading || !data) return <div className="text-muted">Chargement des playbooks…</div>;
  const s = data.summary;

  return (
    <div>
      <div className="mb-6 flex items-start justify-between gap-3">
        <PageHeader title="SOAR Playbooks" subtitle="Automatisation de la réponse à incident — orchestration et exécution" />
        {wazuhStatus && (
          <span
            className={`mt-1 whitespace-nowrap rounded-lg border px-2.5 py-1 text-[11px] font-bold uppercase ${
              wazuhStatus.demo_mode
                ? "border-info/40 bg-info/15 text-info"
                : wazuhStatus.connected
                  ? "border-low/40 bg-low/15 text-low"
                  : "border-crit/40 bg-crit/15 text-crit"
            }`}
          >
            {wazuhStatus.demo_mode ? "Mode démo" : wazuhStatus.connected ? "● Wazuh connecté" : "○ Wazuh injoignable"}
          </span>
        )}
      </div>

      <div className="mb-4 grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard icon="⚙" accent="brand" label="Playbooks" value={s.total} />
        <KpiCard icon="🟢" accent="low" label="Actifs" value={s.active} />
        <KpiCard icon="▶" accent="info" label="Exécutions aujourd'hui" value={s.executions_today} />
        <KpiCard icon="⏱" accent="med" label="Temps économisé (h)" value={s.time_saved_hours} />
      </div>

      <div className="mb-4">
        <Card title="Déclencher une réponse active" badge="Wazuh Active Response">
          <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
            <input className="input" placeholder="Nom de l'agent (ex. SRV-WEB01)" value={agentName} onChange={(e) => setAgentName(e.target.value)} />
            <input className="input" placeholder="IP source (optionnel)" value={srcIp} onChange={(e) => setSrcIp(e.target.value)} />
            <select className="input" value={action} onChange={(e) => setAction(e.target.value)}>
              {ACTIONS.map((a) => (
                <option key={a.value} value={a.value}>{a.label}</option>
              ))}
            </select>
            <button
              className="btn-brand"
              disabled={!agentName.trim() || trigger.isPending}
              onClick={() => trigger.mutate()}
            >
              {trigger.isPending ? "Exécution…" : "Déclencher"}
            </button>
          </div>
          {result && (
            <div
              className={`mt-3 rounded-lg border px-3.5 py-2.5 text-[12.5px] ${
                result.success ? "border-low/40 bg-low/10 text-low" : "border-crit/40 bg-crit/10 text-crit"
              }`}
            >
              {result.success
                ? `✅ ${result.action_label} exécuté avec succès${result.demo ? " (simulation démo)" : ` — agent ${result.agent_id}`} par ${result.triggered_by}`
                : `❌ Échec : ${result.error}`}
            </div>
          )}
        </Card>
      </div>

      <Card title="Playbooks d'automatisation" badge={`${data.playbooks.length}`}>
        <table className="w-full text-[12.5px]">
          <thead>
            <tr className="text-left text-[10.5px] uppercase tracking-wide text-muted">
              <th className="py-2">Playbook</th>
              <th>Déclencheur</th>
              <th>Catégorie</th>
              <th>Statut</th>
              <th>Exécutions (30j)</th>
              <th>Taux de succès</th>
              <th>Durée moy.</th>
            </tr>
          </thead>
          <tbody>
            {data.playbooks.map((p) => (
              <tr key={p.id} className="border-t border-border/60">
                <td className="py-2.5 text-heading">{p.name}</td>
                <td className="max-w-[220px] truncate text-body">{p.trigger}</td>
                <td className="text-body">{p.category}</td>
                <td>
                  <Badge kind="op" value={p.status} />
                </td>
                <td className="font-mono text-body">{p.executions_30d}</td>
                <td className="font-mono font-bold text-low">{p.success_rate}%</td>
                <td className="font-mono text-body">{p.avg_duration_sec}s</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
