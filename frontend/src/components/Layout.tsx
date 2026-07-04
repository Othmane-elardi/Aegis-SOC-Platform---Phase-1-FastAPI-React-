import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { GROUPS, MODULES } from "../modules";
import clsx from "clsx";

function canSee(roles: string[] | undefined, role: string) {
  if (!roles) return true;
  return role === "admin" || roles.includes(role);
}

export default function Layout() {
  const { user, logout } = useAuth();
  const role = user?.role ?? "readonly";

  return (
    <div className="flex h-screen overflow-hidden bg-bg text-body">
      {/* Sidebar */}
      <aside className="flex w-64 flex-shrink-0 flex-col border-r border-border bg-surface">
        <div className="flex h-16 items-center gap-3 border-b border-border px-5">
          <div className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-[#0e5a52] to-brand font-display text-sm font-bold text-[#041512]">
            Æ
          </div>
          <div>
            <div className="font-display text-[15px] font-semibold text-heading">Aegis</div>
            <div className="font-mono text-[10px] text-muted">SOC Platform</div>
          </div>
        </div>

        <nav className="flex-1 space-y-4 overflow-y-auto px-3 py-4">
          {GROUPS.map((group) => {
            const items = MODULES.filter((m) => m.group === group && canSee(m.roles, role));
            if (!items.length) return null;
            return (
              <div key={group}>
                <div className="mb-1 px-3 text-[9.5px] font-extrabold uppercase tracking-[0.14em] text-muted">
                  {group}
                </div>
                {items.map((m) => (
                  <NavLink
                    key={m.path}
                    to={m.path}
                    end={m.path === "/"}
                    className={({ isActive }) =>
                      clsx(
                        "flex items-center gap-2.5 rounded-lg px-3 py-2 text-[13px] font-medium transition",
                        isActive
                          ? "bg-brand/10 font-bold text-brand shadow-[inset_2px_0_0_theme(colors.brand.DEFAULT)]"
                          : "text-body hover:bg-surface2 hover:text-heading"
                      )
                    }
                  >
                    <span className="w-5 text-center text-sm opacity-90">{m.icon}</span>
                    <span className="truncate">{m.label}</span>
                    {m.roadmap && (
                      <span className="ml-auto rounded bg-info/15 px-1.5 py-0.5 text-[8.5px] font-bold text-info">
                        SOON
                      </span>
                    )}
                  </NavLink>
                ))}
              </div>
            );
          })}
        </nav>
      </aside>

      {/* Main */}
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-16 flex-shrink-0 items-center gap-4 border-b border-border bg-surface/70 px-6 backdrop-blur">
          <input
            placeholder="Rechercher un incident, un actif, une IP…  (⌘K)"
            className="input max-w-md py-2 font-mono text-xs"
          />
          <div className="ml-auto flex items-center gap-3">
            <span className="rounded-lg bg-gradient-to-br from-med to-high px-2.5 py-1 text-[10px] font-extrabold uppercase tracking-wider text-[#2a1600]">
              ● Démo
            </span>
            <div className="text-right">
              <div className="text-[13px] font-semibold text-heading">{user?.full_name}</div>
              <div className="font-mono text-[10px] uppercase text-muted">{role}</div>
            </div>
            <button
              onClick={logout}
              className="rounded-xl border border-border px-3 py-2 text-xs font-semibold text-body transition hover:border-crit hover:text-crit"
            >
              Déconnexion
            </button>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
