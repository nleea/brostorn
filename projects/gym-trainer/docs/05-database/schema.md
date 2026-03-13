---
project: fitness-app
tags:
  - fitness-app
  - docs
  - database
  - schema
---

# Schema

## Tablas principales
- `users`
- `clients`
- `training_plans`
- `nutrition_plans`
- `training_logs`
- `meal_logs`
- `metrics`
- `attendance`
- `progress_entries`
- `weekly_checkins`
- `exercises`
- `exercise_favorites`
- `exercise_evidences`
- `photos`
- `monthly_reports`
- `user_configs`
- `user_sessions`

## Relaciones clave
- `clients.user_id -> users.id`
- `clients.trainer_id -> users.id`
- planes asignados y templates se diferencian por `client_id`, `is_template`, `source_template_id`
- `user_sessions.user_id -> users.id`
- métricas, logs, attendance y reportes cuelgan de `clients`

## JSON relevantes
- `training_plans.weeks`
- `nutrition_plans.days`
- `training_logs.exercises`
- `metrics.photos`
- `exercise_evidences.photo_urls`
