# Aegis SOC Platform

Plateforme SOC **enterprise** (SaaS-ready) — refonte complète en architecture moderne :
**FastAPI + PostgreSQL + React + TypeScript + TailwindCSS**.

> État : **Phases 1 à 3 livrées** (+ Compliance de la Phase 4) — architecture,
> authentification JWT + RBAC, et **22 modules fonctionnels** couvrant Dashboards,
> Detection & Response, Threat Intelligence, Governance, IA et Platform, chacun
> alimenté par des données de démo réalistes via de vrais endpoints API. Il ne
> reste de la roadmap que le multi-tenant appliqué, la marketplace et les
> fonctionnalités SaaS Enterprise (Phase 5).

## Architecture

```
soc-platform/
├── backend/            # API FastAPI (Python)
│   ├── app/
│   │   ├── core/       # config, sécurité (JWT + bcrypt)
│   │   ├── db/         # SQLAlchemy 2.0, session, seed
│   │   ├── models/     # ORM (User, multi-tenant ready)
│   │   ├── schemas/    # Pydantic v2
│   │   ├── services/   # logique métier + données de démo
│   │   └── api/        # routers versionnés /api/v1
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/           # React + TS + Vite + Tailwind + TanStack Query + Recharts
│   ├── src/
│   │   ├── lib/        # client API (axios), contexte d'auth
│   │   ├── components/ # Layout (shell), UI (cards, badges)
│   │   ├── pages/      # 22 pages (une par module — voir liste ci-dessous)
│   │   └── modules.ts  # catalogue des 22 modules (navigation)
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
| **Platform** | Reports Center · Audit Center (auditor/soc_manager) · Administration (admin) |

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

## Déploiement (Docker)

```bash
docker compose up --build
```

- Frontend : http://localhost:8080  ·  Backend : http://localhost:8000  ·  Postgres : 5432

## Sécurité

- Mots de passe hachés **bcrypt**, jetons **JWT** signés, RBAC par rôle côté API.
- `SECRET_KEY` et mots de passe admin **à changer** en production (voir `backend/.env.example`).
- Modèle `User` porte déjà `tenant_id` → **multi-tenant** préparé sans migration destructive.

## Roadmap

- **Phase 1 (livrée)** — Architecture, Auth/RBAC, Dashboards, Incident Management
- **Phase 2 (livrée)** — SIEM, SOAR (playbooks), Threat Intelligence, Detection Engineering
- **Phase 3 (livrée)** — IA (Copilot, RAG/Knowledge Base), UEBA
- **Phase 4 (partielle)** — Compliance ✅ livré · Multi-tenant (préparé via `tenant_id`,
  isolation non appliquée) et Marketplace restent à faire
- **Phase 5 (à faire)** — SaaS Enterprise (facturation, SSO SAML/OIDC, observabilité)
