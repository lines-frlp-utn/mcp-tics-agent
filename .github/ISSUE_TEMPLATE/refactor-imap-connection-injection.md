---
name: "Refactor: inyectar la conexión IMAP en vez de crearla por función"
about: Alinear utils/imap_folders.py y utils/imap_reader.py con la regla de mocking del CLAUDE.md
title: "refactor(outlook): inyectar la conexión IMAP en imap_folders.py e imap_reader.py"
labels: refactor, tech-debt, mcp-server-outlook
assignees: ''
---

## Contexto

Actualmente, cada utilidad crea el cliente que representa la conexión mediante IMAP con la casilla de correo en Outlook. `utils/imap_connection.py` debería ser el **único** módulo que abre conexiones IMAP, y que `imap_folders.py` e `imap_reader.py` reciben la conexión ya construida (inyectada), sin crearla por su cuenta.

Esto no refleja el código actual:

- `create_folder()` y `move_email()` en [`mcp-server-outlook/utils/imap_folders.py`](../../mcp-server-outlook/utils/imap_folders.py) llaman `client = connect()` internamente (líneas 27 y 57).
- `read()` en [`mcp-server-outlook/utils/imap_reader.py`](../../mcp-server-outlook/utils/imap_reader.py) también llama `client = connect()` internamente (línea ~130).

Ninguna función pública de estos dos módulos recibe la conexión por parámetro hoy.

## Impacto

- **Testabilidad:** para mockear la conexión hay que parchear `connect` en el namespace de cada módulo que la importa (`utils.imap_folders.connect`, `utils.imap_reader.connect`), en vez de mockear un único punto de inyección. Es más frágil ante renombres/movimientos de imports.
- **Costo de autenticación repetido:** cada `connect()` dispara una llamada real a Azure AD vía MSAL (`ConfidentialClientApplication.acquire_token_for_client`). Si un mismo tool necesitara encadenar más de una operación IMAP, hoy pagaría el costo de reautenticación en cada llamada.
- **Manejo de errores inconsistente:** `imap_reader.read()` cierra la conexión en un `try/finally`, pero `create_folder()` y `move_email()` en `imap_folders.py` llaman `client.logout()` sin `try/finally` — si `client.create()` o las operaciones `MOVE`/`COPY` lanzan una excepción, la conexión queda sin cerrar.

## Propuesta

1. Cambiar las firmas de `create_folder`, `move_email`, `read`, `read_unread_items` y `read_all` para que reciban el cliente IMAP ya conectado como parámetro (`client: imaplib.IMAP4_SSL`), en vez de llamar `connect()` internamente.
2. Mover la responsabilidad de abrir/cerrar la conexión al punto de entrada (wrapper de la tool en `server.py`, o un context manager dedicado en `imap_connection.py` que garantice el `logout()` incluso ante excepción).
3. De paso, unificar el manejo de cierre de conexión con `try/finally` (o context manager) en las tres funciones, resolviendo la inconsistencia mencionada arriba.

## Alcance

`mcp-server-outlook`: `utils/imap_connection.py`, `utils/imap_folders.py`, `utils/imap_reader.py`, `server.py` (los wrappers de las tools que hoy llaman a estas funciones).

## Criterios de aceptación

- [ ] `create_folder`, `move_email`, `read`, `read_unread_items`, `read_all` reciben el cliente IMAP por parámetro; ninguna llama a `connect()` internamente.
- [ ] El cierre de la conexión (`logout()`) ocurre siempre, incluso si la operación IMAP lanza una excepción.
