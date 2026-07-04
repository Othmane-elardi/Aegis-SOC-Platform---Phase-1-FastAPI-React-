import clsx from "clsx";
import type { ReactNode } from "react";

export function PageHeader({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <div className="mb-6">
      <h1 className="font-display text-2xl font-semibold tracking-tight text-heading">{title}</h1>
      {subtitle && <p className="mt-1 text-sm text-muted">{subtitle}</p>}
    </div>
  );
}

const ACCENT: Record<string, string> = {
  brand: "text-brand",
  crit: "text-crit",
  high: "text-high",
  med: "text-med",
  low: "text-low",
  info: "text-info",
};
// Couleurs inline (évite les classes Tailwind dynamiques, non détectées par le JIT).
const HEX: Record<string, string> = {
  brand: "#2dd4bf",
  crit: "#f0453f",
  high: "#f5842a",
  med: "#f5b729",
  low: "#34d399",
  info: "#5b8def",
};

export function KpiCard({
  label,
  value,
  hint,
  accent = "brand",
  icon,
}: {
  label: string;
  value: ReactNode;
  hint?: ReactNode;
  accent?: keyof typeof ACCENT;
  icon?: string;
}) {
  return (
    <div className="card relative overflow-hidden">
      <div className="absolute inset-x-0 top-0 h-[3px]" style={{ background: HEX[accent] }} />
      <div className="mb-3 grid h-10 w-10 place-items-center rounded-xl bg-surface2 text-lg">{icon ?? "▦"}</div>
      <div className={clsx("font-mono text-[28px] font-bold leading-none tracking-tight", ACCENT[accent])}>{value}</div>
      <div className="mt-1.5 text-[12px] text-muted">{label}</div>
      {hint && <div className="mt-2 text-[11px] text-body">{hint}</div>}
    </div>
  );
}

export function Card({ title, badge, children }: { title?: string; badge?: string; children: ReactNode }) {
  return (
    <div className="card">
      {title && (
        <div className="mb-4 flex items-center justify-between">
          <h3 className="flex items-center gap-2 pl-3 text-[13px] font-bold text-heading before:absolute before:h-4 before:w-[3px] before:-translate-x-3 before:rounded before:bg-brand">
            {title}
          </h3>
          {badge && <span className="rounded-lg border border-border bg-bg px-2 py-0.5 font-mono text-[10.5px] text-muted">{badge}</span>}
        </div>
      )}
      {children}
    </div>
  );
}

const SEV: Record<string, string> = {
  critical: "bg-crit/15 text-crit border-crit/40",
  high: "bg-high/15 text-high border-high/40",
  medium: "bg-med/15 text-med border-med/40",
  low: "bg-low/15 text-low border-low/40",
};
const STATUS: Record<string, string> = {
  new: "bg-info/15 text-info border-info/40",
  investigating: "bg-med/15 text-med border-med/40",
  contained: "bg-brand/15 text-brand border-brand/40",
  resolved: "bg-low/15 text-low border-low/40",
  open: "bg-crit/15 text-crit border-crit/40",
  patching: "bg-med/15 text-med border-med/40",
  patched: "bg-low/15 text-low border-low/40",
  accepted_risk: "bg-info/15 text-info border-info/40",
  active: "bg-crit/15 text-crit border-crit/40",
  monitored: "bg-med/15 text-med border-med/40",
  dormant: "bg-muted/15 text-muted border-border",
  online: "bg-low/15 text-low border-low/40",
  offline: "bg-muted/15 text-muted border-border",
  whitelisted: "bg-info/15 text-info border-info/40",
  expired: "bg-muted/15 text-muted border-border",
  in_review: "bg-med/15 text-med border-med/40",
  closed: "bg-low/15 text-low border-low/40",
};
const VERDICT: Record<string, string> = {
  malicious: "bg-crit/15 text-crit border-crit/40",
  suspicious: "bg-med/15 text-med border-med/40",
  clean: "bg-low/15 text-low border-low/40",
};
const COVERAGE: Record<string, string> = {
  covered: "bg-low/15 text-low border-low/40",
  partial: "bg-med/15 text-med border-med/40",
  none: "bg-crit/15 text-crit border-crit/40",
};
const COMPLIANCE: Record<string, string> = {
  compliant: "bg-low/15 text-low border-low/40",
  partial: "bg-med/15 text-med border-med/40",
  non_compliant: "bg-crit/15 text-crit border-crit/40",
};

const BADGE_MAPS = { sev: SEV, status: STATUS, verdict: VERDICT, coverage: COVERAGE, compliance: COMPLIANCE };

export function Badge({ kind, value }: { kind: keyof typeof BADGE_MAPS; value: string }) {
  const map = BADGE_MAPS[kind];
  return (
    <span className={clsx("rounded-md border px-2 py-0.5 text-[10px] font-bold uppercase", map[value] ?? "border-border text-muted")}>
      {value.replace(/_/g, " ")}
    </span>
  );
}
