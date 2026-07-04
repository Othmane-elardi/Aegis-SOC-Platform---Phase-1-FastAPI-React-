// Catalogue des modules de la plateforme, groupés pour la navigation latérale.
// `roadmap: true` = module prévu (écran squelette). Les autres sont livrés.
export interface ModuleDef {
  path: string;
  label: string;
  group: string;
  icon: string;
  roadmap?: boolean;
  roles?: string[]; // visible seulement pour ces rôles (admin voit tout)
}

export const MODULES: ModuleDef[] = [
  // Dashboards
  { path: "/", label: "SOC Dashboard", group: "Dashboards", icon: "▤" },
  { path: "/executive", label: "Executive (CISO)", group: "Dashboards", icon: "◆", roles: ["ciso", "soc_manager"] },
  { path: "/analyst", label: "Analyst Workspace", group: "Dashboards", icon: "◱" },
  // Detection & Response
  { path: "/incidents", label: "Incident Management", group: "Detection & Response", icon: "⚑" },
  { path: "/cases", label: "Case Management", group: "Detection & Response", icon: "🗂" },
  { path: "/siem", label: "SIEM", group: "Detection & Response", icon: "🛢" },
  { path: "/soar", label: "SOAR Playbooks", group: "Detection & Response", icon: "⚙" },
  { path: "/hunting", label: "Threat Hunting", group: "Detection & Response", icon: "🎯" },
  { path: "/detection", label: "Detection Engineering", group: "Detection & Response", icon: "⟠" },
  // Threat Intelligence
  { path: "/threat-intel", label: "Threat Intelligence", group: "Threat Intel", icon: "🛰" },
  { path: "/iocs", label: "IOC Management", group: "Threat Intel", icon: "⬡" },
  { path: "/mitre", label: "MITRE ATT&CK", group: "Threat Intel", icon: "⛃" },
  { path: "/ueba", label: "UEBA", group: "Threat Intel", icon: "👣" },
  // Governance
  { path: "/assets", label: "Asset Management", group: "Governance", icon: "🖥" },
  { path: "/vulns", label: "Vulnerabilities", group: "Governance", icon: "🐞" },
  { path: "/compliance", label: "Compliance Center", group: "Governance", icon: "✔" },
  { path: "/risk", label: "Risk Management", group: "Governance", icon: "📈" },
  // AI
  { path: "/copilot", label: "AI Copilot", group: "AI", icon: "✨", roadmap: true },
  { path: "/kb", label: "Knowledge Base (RAG)", group: "AI", icon: "📚", roadmap: true },
  // Platform
  { path: "/reports", label: "Reports Center", group: "Platform", icon: "🖨", roadmap: true },
  { path: "/audit", label: "Audit Center", group: "Platform", icon: "🧾", roles: ["auditor", "soc_manager"] },
  { path: "/admin", label: "Administration", group: "Platform", icon: "🛡", roles: ["admin"] },
];

export const GROUPS = ["Dashboards", "Detection & Response", "Threat Intel", "Governance", "AI", "Platform"];
