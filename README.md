# Aegis SOC Platform

Plateforme SOC **enterprise** (SaaS-ready) — refonte complète en architecture moderne :
**FastAPI + PostgreSQL + React + TypeScript + TailwindCSS**.

> État : **Phases 1 à 4 livrées** — architecture, authentification JWT + RBAC,
> isolation **multi-tenant réelle** (pas seulement préparée), et **26 modules
> fonctionnels** couvrant Dashboards, Detection & Response, Threat Intelligence,
> Governance, IA et Platform, chacun alimenté par de vrais endpoints API. La
> Phase 5 (SSO, facturation, observabilité) est livrée en mode démo — architecture
> et UI réelles, sans connexion à un fournisseur d'identité ou de paiement tiers.
>
> **Incident Management est réellement actionnable** (statut, assignation, notes,
> historique — persisté en base) et la plateforme peut se connecter à un **vrai
> cluster Wazuh/Elasticsearch** pour ingérer de vraies alertes, les faire analyser
> par une IA réelle (Groq/OpenRouter/DeepSeek/Ollama), les enrichir via VirusTotal
> et déclencher une réponse active (blocage IP, isolation…) — voir « Mode réel »
> ci-dessous. `DEMO_MODE=true` reste le défaut : aucun appel réseau externe.

## Architecture

```
soc-platform/
├── backend/            # API FastAPI (Python)
│   ├── app/
│   │   ├── core/       # config, sécurité (JWT + bcrypt)
│   │   ├── db/         # SQLAlchemy 2.0, session, seed (tenants + comptes démo)
│   │   ├── models/     # ORM (User, Tenant — isolation multi-tenant appliquée)
│   │   ├── schemas/    # Pydantic v2
│   │   ├── services/   # logique métier + données de démo
│   │   └── api/        # routers versionnés /api/v1
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/           # React + TS + Vite + Tailwind + TanStack Query + Recharts
│   ├── src/
│   │   ├── lib/        # client API (axios), contexte d'auth
│   │   ├── components/ # Layout (shell), UI (cards, badges)
│   │   ├── pages/      # 26 pages (une par module — voir liste ci-dessous)
│   │   └── modules.ts  # catalogue des 26 modules (navigation)
│   └── Dockerfile
└── docker-compose.yml  # postgres + redis + backend + frontend
```

## Modules livrés

| Groupe | Modules |
|---|---|
| **Dashboards** | SOC Dashboard · Executive (CISO) · Analyst Workspace |
| **Detection & Response** | Incident Management · Case Management · SIEM · SOAR Playbooks · Threat Hunting · Detection Engineering |
| **Threat Intel** | Threat Intelligence · IOC Management · MITRE ATT&CK · UEBA |
| **Governance** | Asset Management · Vulnerabilities · Compliance Center · Risk Management |
| **IA** | AI Copilot · Knowledge Base (RAG) |
| **Platform** | Reports Center · Audit Center (auditor/soc_manager) · Administration (admin) · Marketplace · Identity & SSO (admin) · Billing & Subscription (admin) · Observability |

Chaque module a un routeur API dédié (`backend/app/api/routes/`), un générateur de
données de démo déterministe (`backend/app/services/demo_data.py`) et une page React
correspondante (`frontend/src/pages/`) — plus aucun placeholder « roadmap ».

## Démarrage rapide (développement)

### 1. Backend (Python 3.11+)

```bash
cd backend
python -m venv .venv
# Windows : .venv\Scripts\activate    |    Linux/Mac : source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- API : http://127.0.0.1:8000  ·  Docs interactives (Swagger) : http://127.0.0.1:8000/docs
- Base **SQLite** créée automatiquement (`aegis.db`), comptes de démo amorcés au 1er démarrage.

### 2. Frontend (Node 18+)

```bash
cd frontend
npm install
npm run dev
```

- UI : http://localhost:5173 (proxy `/api` → backend automatiquement)

### Comptes de démonstration

| Rôle        | E-mail                | Mot de passe  |
|-------------|-----------------------|---------------|
| Admin       | admin@aegis.local     | admin1234     |
| CISO        | ciso@aegis.local      | ciso1234      |
| SOC Manager | manager@aegis.local   | manager1234   |
| Analyste    | analyst@aegis.local   | analyst1234   |
| Auditeur    | auditor@aegis.local   | auditor1234   |

La vue **Executive** n'est accessible qu'aux rôles CISO / SOC Manager (démonstration du RBAC).

### Multi-tenant : comptes d'autres organisations

Pour vérifier l'isolation entre tenants (module **Administration**, `/api/v1/admin/overview`),
deux tenants de démonstration supplémentaires sont amorcés — chacun avec ses propres comptes,
invisibles depuis un autre tenant :

| Tenant | Admin | Mot de passe |
|---|---|---|
| Globex Financial Group (`globex`) | admin@globex.demo | admin1234 |
| Northwind Energy (`northwind`)     | admin@northwind.demo | admin1234 |

## Mode réel — connecter un vrai Wazuh/ELK

Par défaut (`DEMO_MODE=true`), aucune intégration n'appelle de service externe.
Pour brancher une vraie stack Wazuh + Elasticsearch, une IA et VirusTotal :

1. Copier `backend/.env.example` en `backend/.env`.
2. Passer `DEMO_MODE=false`.
3. Renseigner `WAZUH_HOST`, `WAZUH_USER`, `WAZUH_PASS`, `ES_HOST`, `ES_USER`,
   `ES_PASS` (accessibles uniquement si le backend tourne sur le même réseau que
   ces machines — des IP privées ne sont pas joignables depuis un poste distant).
4. Renseigner au moins une clé IA (`GROQ_API_KEY` recommandé — gratuit et rapide
   sur [console.groq.com](https://console.groq.com)) pour l'analyse d'alerte et
   le Copilot. Sans clé, le pipeline reste fonctionnel mais avec une analyse
   dégradée (score basé uniquement sur le niveau Wazuh).
5. `VT_API_KEY` (optionnel) active l'enrichissement IOC réel via VirusTotal.
6. Redémarrer le backend : un pipeline en tâche de fond (`services/wazuh_ingest.py`)
   interroge Wazuh/ES toutes les 30s, fait analyser chaque nouvelle alerte par
   l'IA, l'enrichit, déclenche une réponse active si le niveau de risque le
   justifie, et crée un incident **persistant** consultable/actionnable dans
   Incident Management.

Le statut de connexion réel (`● Wazuh connecté` / `○ Wazuh injoignable`) s'affiche
sur les pages **SIEM** et **SOAR Playbooks**. Aucun de ces identifiants ne doit
jamais être commité — `backend/.env` est ignoré par git.

**Module Red Team (exécution de commandes via SSH) volontairement exclu** de
cette intégration — capacité offensive à part, nécessitant une revue de
sécurité dédiée avant toute activation.

## Déploiement (Docker)

```bash
docker compose up --build
```

- Frontend : http://localhost:8080  ·  Backend : http://localhost:8000  ·  Postgres : 5432

## Sécurité

- Mots de passe hachés **bcrypt**, jetons **JWT** signés, RBAC par rôle côté API.
- `SECRET_KEY` et mots de passe admin **à changer** en production (voir `backend/.env.example`).
- **Isolation multi-tenant appliquée** : modèle `Tenant` dédié, `tenant_id` porté par le JWT et
  par `User`, toutes les requêtes d'administration filtrées par tenant (`api/routes/admin.py`,
  `api/routes/billing.py`) — un admin ne voit et ne gère jamais les comptes d'une autre organisation.

## Roadmap

- **Phase 1 (livrée)** — Architecture, Auth/RBAC, Dashboards, Incident Management
- **Phase 2 (livrée)** — SIEM, SOAR (playbooks), Threat Intelligence, Detection Engineering
- **Phase 3 (livrée)** — IA (Copilot, RAG/Knowledge Base), UEBA
- **Phase 4 (livrée)** — Compliance, isolation multi-tenant réelle, Marketplace
- **Phase 5 (démo)** — Identity & SSO, Billing & Subscription, Observability : UI et API réelles,
  données simulées (pas d'intégration IdP/paiement/monitoring tiers — nécessiterait des clés
  d'API externes hors du périmètre de cette démo)
