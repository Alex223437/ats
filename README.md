# ATS – Automatizovaný Obchodní Systém

Tento projekt je moderní webová aplikace pro správu automatizovaných obchodních strategií. Umožňuje uživatelům:

- vytvářet a testovat vlastní strategie,
- používat modely umělé inteligence pro predikci pohybů na trhu,
- vizualizovat výsledky a statistiky v přehledném rozhraní,
- napojit se na brokerskou platformu a provádět reálné obchody.

## Požadavky

- [Docker](https://www.docker.com/)
- [Node.js](https://nodejs.org/) (doporučeno verze 18+)
- [NPM](https://www.npmjs.com/)

## Lokální spuštění

### 1. Backend (FastAPI + PostgreSQL)

Ve složce `server/` je připraven Docker setup. Pro spuštění stačí:

```bash
cd server
docker-compose up --build
```

> Backend poběží na adrese `http://localhost:8000`

### 2. Frontend (React)

Ve složce `ats-client/` spusť klient pomocí:

```bash
cd ats-client
npm install
npm run dev
```

> Frontend poběží na `http://localhost:5173`

## Struktura projektu

```
.
├── ats-client/       # frontend (React)
└── server/           # backend (FastAPI, PostgreSQL, TensorFlow, Docker)
```

## Poznámky

- Model umělé inteligence je trénován pomocí TensorFlow (LSTM + CNN).
- Backend i frontend jsou rozdělené do samostatných komponent (modulární architektura).
- Pro produkční nasazení je možné snadno upravit `Dockerfile` a přidat reverse proxy (např. Nginx).

---

### Autor

Aliaksei Sidoryk – Bakalářská práce (2025)  
Univerzita Tomáše Bati ve Zlíně
