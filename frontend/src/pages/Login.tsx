import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth";

export default function Login() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState("admin@aegis.local");
  const [password, setPassword] = useState("admin1234");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await login(email, password);
      nav("/");
    } catch {
      setError("Identifiants invalides");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid min-h-screen place-items-center bg-bg px-4">
      <div
        className="pointer-events-none fixed inset-0 opacity-60"
        style={{
          backgroundImage:
            "radial-gradient(circle at 15% 15%, rgba(45,212,191,.10) 0, transparent 40%), radial-gradient(circle at 85% 85%, rgba(91,141,239,.08) 0, transparent 45%)",
        }}
      />
      <form onSubmit={submit} className="card z-10 w-full max-w-sm">
        <div className="mb-6 flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-gradient-to-br from-[#0e5a52] to-brand font-display text-base font-bold text-[#041512]">
            Æ
          </div>
          <div>
            <div className="font-display text-lg font-semibold text-heading">Aegis SOC Platform</div>
            <div className="font-mono text-[11px] text-muted">Centre d'opérations sécurité</div>
          </div>
        </div>

        {error && (
          <div className="mb-4 rounded-lg border border-crit/40 bg-crit/10 px-3 py-2.5 text-[13px] font-semibold text-crit">
            {error}
          </div>
        )}

        <label className="mb-1.5 block text-xs font-semibold text-body">E-mail</label>
        <input className="input mb-3" value={email} onChange={(e) => setEmail(e.target.value)} type="email" autoFocus />
        <label className="mb-1.5 block text-xs font-semibold text-body">Mot de passe</label>
        <input className="input mb-5" value={password} onChange={(e) => setPassword(e.target.value)} type="password" />

        <button className="btn-brand w-full" disabled={busy}>
          {busy ? "Connexion…" : "Se connecter"}
        </button>

        <div className="mt-4 rounded-xl border border-med/30 bg-med/10 px-3 py-2.5 text-center text-[12px] text-body">
          <div className="mb-1 inline-block rounded bg-gradient-to-br from-med to-high px-2 py-0.5 text-[9px] font-extrabold uppercase tracking-wider text-[#2a1600]">
            Comptes démo
          </div>
          <div className="font-mono">
            admin · ciso · manager · analyst · auditor
            <br />
            <span className="text-muted">mot de passe : &lt;rôle&gt;1234</span>
          </div>
        </div>
      </form>
    </div>
  );
}
