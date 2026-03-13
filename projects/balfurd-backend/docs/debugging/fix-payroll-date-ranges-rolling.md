---
title: Fix payroll date ranges to use rolling windows instead of calendar periods
project: balfurd-erp-backend
type: bug_fix
status: resolved
module: null
updated_at: '2026-03-13'
files_changed:
- apps/erp/utils/payroll_utils.py
follow_ups: []
tags:
- balfurd-erp-backend
- date-ranges
- debugging
- docs
- metrics
- payroll
- rolling-window
---


# Fix payroll date ranges to use rolling windows instead of calendar periods

## Summary


## Status
resolved

## Symptom
Payroll metrics (payroll-to-revenue, direct-labor-to-revenue, net-gain, pounds-per-operator-hour) used calendar-based date ranges (e.g., Monday-Sunday for week, 1st-last of month) instead of rolling ranges relative to today.

## Root Cause
get_period_dates() in payroll_utils.py calculated ranges based on calendar boundaries (weekday, month start/end, year start/end) instead of using simple timedelta rolling windows (today-7, today-30, today-90, today-365).

## Solution
Replaced both get_period_dates() and get_previous_period_dates() with simple timedelta-based rolling windows: week=7d, month=30d, 3months=90d, year=365d. Previous periods shift back by the same window size.

## Files Changed
- `apps/erp/utils/payroll_utils.py`
