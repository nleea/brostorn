---
title: "Fixes de validaci\xF3n en APApllyCustomerPage y PaymentEntry, completar mapping\
  \ de tipos de pago, redise\xF1o UI con layout masonry siguiendo el design system\
  \ Finance del proyecto"
project: balfurd-frontend
type: session_summary
session_date: '2026-03-12'
tags:
- ar-payment
- balfurd-frontend
- design-system
- docs
- finance-module
- masonry
- payment-entry
- session-memory
- type-payments
- validaciones
context_pack: null
context_note_paths: []
---


# Fixes de validación en APApllyCustomerPage y PaymentEntry, completar mapping de tipos de pago, rediseño UI con layout masonry siguiendo el design system Finance del proyecto

## Task
Fixes de validación en APApllyCustomerPage y PaymentEntry, completar mapping de tipos de pago, rediseño UI con layout masonry siguiendo el design system Finance del proyecto

## Context Loaded
- No explicit context pack recorded.

## Findings
- Save button en applyHeader ahora usa disabled={unnaplied !== 0 || hasError}, hasError viene del padre como !validSequency(Seq)
- getPaymentEntryByType reemplazado por objeto mapping completo: CASH/CHECK/CREDITS→Payment/Ledger, ACH/EFT→EFT, CREDIT_CARD→Credit Card, DISCOUNT→Discounts, WRITE_OFF→WRITE_OFF, etc.
- isBalanced ahora usa rows.every() en lugar de sumar totales — cada fila debe balancear individualmente
- PaymentEntry rediseñado: layout masonry con CSS columns:3, cards por tipo de pago con estado balanced/unbalanced visual, panel derecho con 4 cards apiladas, bottom bar con totales
- Design tokens usados: --color-finance-1 (verde oscuro #093328) para primarios, --color-finance-3 (sage #aacec3) para bordes, --color-finance-8 (#f0fcf8) para fondo de página
- SelectReact con classNamePrefix='pe-select' para override completo del tema oscuro al tema Finance claro

## Files Modified
- `src/components/pages/FinancePages/ARAplicationPage/components/applyHeader.jsx`
- `src/components/pages/FinancePages/ARAplicationPage/APApllyCustomerPage.jsx`
- `src/components/pages/FinancePages/ARAplicationPage/components/PaymentEntry.jsx`
- `src/components/pages/FinancePages/ARAplicationPage/components/ARApayment.css`
- `src/components/util/configs/index.js`

## Validation
Not recorded.

## Follow Ups
- None recorded.
