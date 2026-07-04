import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./lib/auth";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Overview from "./pages/Overview";
import Executive from "./pages/Executive";
import Incidents from "./pages/Incidents";
import ThreatIntel from "./pages/ThreatIntel";
import Mitre from "./pages/Mitre";
import Assets from "./pages/Assets";
import Vulnerabilities from "./pages/Vulnerabilities";
import Compliance from "./pages/Compliance";
import ModulePlaceholder from "./pages/ModulePlaceholder";
import { MODULES } from "./modules";

function Protected({ children }: { children: JSX.Element }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="grid h-screen place-items-center text-muted">Chargement…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        element={
          <Protected>
            <Layout />
          </Protected>
        }
      >
        <Route path="/" element={<Overview />} />
        <Route path="/executive" element={<Executive />} />
        <Route path="/incidents" element={<Incidents />} />
        <Route path="/threat-intel" element={<ThreatIntel />} />
        <Route path="/mitre" element={<Mitre />} />
        <Route path="/assets" element={<Assets />} />
        <Route path="/vulns" element={<Vulnerabilities />} />
        <Route path="/compliance" element={<Compliance />} />
        {/* Modules de la roadmap : squelettes honnêtes (badge « Roadmap ») pour
            montrer l'étendue de la plateforme sans simuler une profondeur absente. */}
        {MODULES.filter((m) => m.roadmap).map((m) => (
          <Route key={m.path} path={m.path} element={<ModulePlaceholder module={m} />} />
        ))}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
