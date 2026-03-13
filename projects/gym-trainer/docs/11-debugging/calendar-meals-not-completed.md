---
title: Calendar Meals Not Completed
project: fitness-app
type: bug_fix
tags:
  - docs
  - debugging
  - fitness-app
  - calendar
  - nutrition
  - meal-completion
---

# Calendar Meals Not Completed

## Estado
- Cerrado.
- Validado en codigo y build local el 2026-03-11.

## Sintoma
- En el calendario del cliente, los exercises aparecian como completados pero las comidas no, aunque ya existieran `meal_logs`.

## Related Notes
- [[02-architecture/data-flow]]
- [[04-frontend/vue-architecture]]
- [[07-patterns/frontend-patterns]]

## Root Cause
- `TrainingView.vue` pasaba a `TaskCalendar` el flujo de workouts (`dayStatusFor`, `logForDate`) pero no la senal equivalente para meals.
- `TaskCalendar.vue` dependia de `mealLogForDate(day)` para marcar comidas como completadas, y esa prop nunca se enviaba desde `TrainingView`.
- Ademas, exercises usaban historial completo (`loadAllClientLogs`) mientras meals solo usaban cache semanal, asi que el calendario de 2 o 4 semanas no tenia una fuente consistente para nutricion.
- En el panel de detalle, el registro de comidas se comparaba por `type`, lo que no es robusto cuando hay mas de una comida del mismo tipo en un mismo dia. El identificador correcto es `meal_key`.

## Fix
- Se agrego carga de historial completo de `meal_logs` en `logs.store.ts` mediante `loadAllClientMealLogs`.
- `TrainingView.vue` ahora calcula `mealStatusFor(date)` usando:
  - comidas planificadas para ese dia
  - `meal_key` deterministico por dia/tipo/indice
  - logs reales de comidas para esa fecha
- `TaskCalendar.vue` acepta `mealStatusForDate` y marca `done` cuando el estado de nutricion del dia es `completed`.
- El panel de nutricion en `TrainingView.vue` ahora compara `meal_key` en vez de `type`.

## Files Modified
- `gym-trainer-client/vue/views/client/TrainingView.vue`
- `gym-trainer-client/vue/components/taskCalendar.vue`
- `gym-trainer-client/vue/stores/logs.store.ts`
- `gym-trainer-client/vue/repo/mealsRepo.ts`

## Validation
- Se verifico que el codigo implementa el fix documentado en los archivos listados arriba.
- `npm run build` en `gym-trainer-client` compilo sin errores el 2026-03-11.
- El flujo esperado queda alineado entre workouts y meals: ambos usan historial completo para calcular completion en el calendario.

## Follow-ups
- Mantener la comparacion de completitud de meals basada en `meal_key`, no en `type`.
- Si se vuelve a optimizar carga de logs, no degradar meals a cache semanal cuando la UI muestra ventanas de 2 o 4 semanas.
- `npm run lint` no es senal valida de este fix hasta migrar la configuracion de ESLint 9 (`eslint.config.js`).
