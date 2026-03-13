---
project: fitness-app
tags:
  - fitness-app
  - docs
  - frontend
  - vue-architecture
---

# Vue Architecture

## Estructura
- `vue/views/`: pantallas por rol y dominio.
- `vue/components/`: componentes reutilizables.
- `vue/stores/`: Pinia stores.
- `vue/repo/`: capa de acceso a API.
- `vue/composables/`: helpers.
- `vue/layouts/`: layouts por contexto.

## Organización
- `AuthLayout`, `TrainerLayout`, `ClientLayout`.
- Stores por dominio: auth, clients, plan, logs, metrics, trainer, evidences.
- Los repos encapsulan fetch, headers y mapeos.
