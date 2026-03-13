---
project: fitness-app
tags:
  - fitness-app
  - docs
  - architecture
  - data-flow
---

# Data Flow

## Training log
1. El cliente completa `LogWorkoutView.vue`.
2. `logs.store.ts` arma el payload.
3. `trainingLogsrepo.ts` envía `POST /training-logs`.
4. `TrainingLogsService` hace upsert por `client_id + date`.
5. El store invalida o mezcla cache semanal.

## Nutrition
1. La UI consume `nutrition.store.ts`.
2. El repo usa `POST /meal-logs/upsert` y `GET /meal-logs/nutrition-summary`.
3. El backend consolida adherencia y macros.
4. En calendario, el completion diario debe resolverse desde `meal_logs` reales comparando `meal_key` planificado vs `meal_key` registrado, no solo por `type`.
5. Para vistas de calendario multi-semana, el frontend usa historial de comidas suficientemente amplio para no depender solo del cache semanal visible.

## Metrics
1. El cliente registra métricas o sube fotos.
2. El backend persiste `metrics` y opcionalmente genera URL firmada para R2.
3. Los resúmenes se exponen desde `/clients/{id}/metrics-summary`.
