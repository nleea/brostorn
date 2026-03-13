---
project: memory-system
tags:
  - memory-system
  - debugging
  - mcp
  - codex
  - claude
  - poetry
---

# MCP Registration Uses System Python

## Sintoma
- Los registros de MCP para Codex y Claude quedaban creados, pero el servidor fallaba al arrancar.
- El proceso registrado ejecutaba `python -m apps.mcp_server.main` con el Python del sistema.
- El arranque fallaba con `ModuleNotFoundError: No module named 'mcp'`.

## Causa raiz
- Los scripts `scripts/register_codex_mcp.sh` y `scripts/register_claude_mcp.sh` resolvian el interprete con `poetry env info -p`.
- En entornos donde ese comando no devolvia una ruta util, el script caia silenciosamente a `python`.
- Ese fallback usaba un interprete fuera del virtualenv de Poetry y sin las dependencias del proyecto.

## Archivos cambiados
- `scripts/register_codex_mcp.sh`
- `scripts/register_claude_mcp.sh`

## Solucion
- Se agrego una resolucion de interprete mas robusta.
- Primero se intenta `poetry env info --executable`.
- Si eso falla, se usa `poetry run python -c 'import sys; print(sys.executable)'`.
- Solo si ninguna opcion entrega un ejecutable valido se mantiene el fallback a `python`.

## Validacion
- `bash -n scripts/register_codex_mcp.sh`
- `bash -n scripts/register_claude_mcp.sh`
- Prueba con stubs para verificar que ambos scripts imprimen y registran la ruta del ejecutable devuelta por Poetry.
- Verificacion manual en Codex: el registro final quedo apuntando al virtualenv de Poetry y ese interprete pudo importar `mcp`.

## Follow-ups
- Considerar extraer la logica de resolucion de Python a un script comun para evitar drift entre Codex y Claude.
- Considerar fallar explicitamente si Poetry esta disponible pero no se puede resolver un ejecutable valido, en lugar de caer a `python`.
