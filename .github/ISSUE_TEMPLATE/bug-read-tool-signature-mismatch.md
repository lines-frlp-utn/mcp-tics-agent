---
name: "Bug: la tool `read` no coincide con la firma de imap_reader.read"
about: La tool MCP `read` expuesta en server.py falla en runtime por desajuste de parámetros
title: "fix(outlook): la tool `read` en server.py no coincide con la firma de utils/imap_reader.read"
labels: bug, mcp-server-outlook
assignees: ''
---

## Contexto

[`mcp-server-outlook/server.py`](../../mcp-server-outlook/server.py) expone la tool `read` así:

```python
@mcp.tool()
def read(folder: str, uid: str) -> dict:
    """Read an email message by folder and UID."""
    return read_util(folder=folder, uid=uid)
```

Pero la función real importada, [`utils/imap_reader.read`](../../mcp-server-outlook/utils/imap_reader.py), tiene esta firma:

```python
def read(folder: str, criterion: str, limit: int) -> list[dict]:
```

No existe parámetro `uid` en `imap_reader.read`, y `criterion`/`limit` son obligatorios (sin default).

## Impacto

La tool `read` está rota: cualquier invocación vía MCP falla en runtime con un `TypeError` (`read() got an unexpected keyword argument 'uid'`, y además faltarían los argumentos obligatorios `criterion` y `limit`).

## Reproducción

```bash
npx @modelcontextprotocol/inspector --cli http://localhost:8002/mcp \
  --transport http --method tools/call \
  --tool-name read --tool-arg folder=INBOX --tool-arg uid=123
```

Resultado esperado: el email solicitado. Resultado actual: error de la tool por `TypeError` en `read_util`.

## Propuesta

Decidir qué contrato se quiere exponer y ajustar en consecuencia:

- **Opción A — leer un mail puntual por UID:** agregar una función a `imap_reader.py` que busque un mensaje específico por UID (no existe hoy; `read()` solo soporta criterios de búsqueda tipo `UNSEEN`/`ALL` con límite), y que la tool `read` la use.
- **Opción B — exponer `read` tal como está definida:** cambiar la firma de la tool en `server.py` para que reciba `folder`, `criterion` y `limit`, igual que la función utilitaria, en vez de `uid`.

## Alcance

`mcp-server-outlook`: `server.py`, y `utils/imap_reader.py` si se opta por la Opción A.

## Criterios de aceptación

- [ ] La tool `read` invocada vía MCP Inspector devuelve resultados sin error.
- [ ] La firma de la tool en `server.py` coincide exactamente con la de la función utilitaria que envuelve.
