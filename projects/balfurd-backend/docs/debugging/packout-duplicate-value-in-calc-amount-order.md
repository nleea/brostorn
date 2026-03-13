---
title: Packout duplicate value in calc_amount_order
project: balfurd-erp
type: bug_fix
status: closed
module: null
updated_at: '2026-03-13'
files_changed:
- apps/erp/utils/routes_util.py
follow_ups: []
tags:
- balfurd-erp
- billing
- debugging
- docs
- duplicate-value
- erp
- packout
- routes
---


# Packout duplicate value in calc_amount_order

## Summary


## Status
closed

## Symptom
El valor de packout se duplicaba para órdenes con frecuencias simples (SIMPLE_FREQS) en la función calc_amount_order.

## Root Cause
Dos problemas en apps/erp/utils/routes_util.py: 1) req_pct se limitaba incorrectamente con min(..., billing_value), 2) to_pack_out se multiplicaba por 2 antes de retornarse para frecuencias simples.

## Solution
1) Se quitó el min() al calcular req_pct, usando directamente get_requirement_percentage(). 2) Se eliminó la multiplicación por 2 en el return de to_pack_out para SIMPLE_FREQS.

## Files Changed
- `apps/erp/utils/routes_util.py`
