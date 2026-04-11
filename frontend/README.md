# frontend

Vue 3 + Vite SPA for driving MiroFish simulations.

## Layout

- `index.html`, `vite.config.js` - Vite entry and config.
- `src/main.js`, `src/App.vue` - app bootstrap.
- `src/router/` - client-side routes.
- `src/store/` - state management.
- `src/api/` - backend clients (`graph.js`, `simulation.js`, `report.js`, `index.js`).
- `src/components/` - pipeline step components:
  `Step1GraphBuild`, `Step2EnvSetup`, `Step3Simulation`, `Step4Report`, `Step5Interaction`, `GraphPanel`, `HistoryDatabase`.
- `src/views/` - page-level views: `Home`, `MainView`, `Process`, `SimulationView`, `SimulationRunView`, `ReportView`, `InteractionView`.
- `public/` - static assets.

## Run

```bash
npm install
npm run dev   # dev server on :3000, proxies to backend :5001
npm run build # emits dist/ served by Flask in production
```

Requires Node.js 18+.
