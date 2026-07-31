# 🛠️ MCP & Support Agent for TICS

Este proyecto implementa la arquitectura de un **Agente de Inteligencia Artificial Autónomo** diseñado para la administración automatizada y soporte técnico de infraestructura de TI. El agente procesa solicitudes de usuarios finales recibidas a través de correos electrónicos corporativos (Outlook) y ejecuta operaciones de administración lógica —como creación de usuarios, reseteo de contraseñas y asignación de licencias de software (ej. AutoCAD)— de manera segura utilizando el estándar **Model Context Protocol (MCP)**.

---

## 🏗️ Arquitectura del Sistema

El sistema se basa en un desacoplamiento completo de responsabilidades mediante microservicios encapsulados en contenedores independientes que se comunican entre sí utilizando **Streamable HTTP** (el transporte MCP recomendado para clientes remotos) sobre una red privada de Docker.

<img width="1243" height="553" alt="MCP Arquitecture" src="https://github.com/lines-frlp-utn/mcp-tics-agent/blob/main/docs/mcp-tics-agent.jpg?raw=true" />

### Componentes Clave:
1. **Model & Agent Host (`mcp-host`):** El cerebro del sistema. Es un servicio **FastAPI** que embebe el **MCP Client** y actúa como traductor de protocolo hacia los distintos MCP Servers. Actualmente expone un endpoint de verificación de conectividad (`/demo/lines/add`) contra el server LINES; ya declara configuración para conectarse también al server de Outlook (`MCP_SERVER_OUTLOOK_URL`), pero todavía no la usa en código. El bucle de razonamiento contra el LLM (orquestación de intención, selección de herramientas, etc.) está pendiente de implementación.
2. **MCP Outlook Server (`mcp-server-outlook`):** Desarrollado en Python con **FastMCP** (montado sobre **FastAPI**). Expone sus herramientas vía Streamable HTTP en `/mcp` y provee acceso a una casilla de Exchange Online mediante **IMAP** (`imaplib`), autenticado con **OAuth2** (flujo client-credentials vía **MSAL**), sin depender de la API Graph de Microsoft. Actualmente expone 8 tools: `create_folder`, `move_email_to_folder`, `read`, `read_unread_items`, `read_all`, `decodificate_header`, `extract_body` y `parse_message`.
3. **MCP LINES Server (`mcp-server-lines`):** Desarrollado en Python con **FastMCP** (montado sobre **FastAPI**). Expone sus herramientas vía Streamable HTTP en `/mcp` y provee acceso controlado a la base de datos transaccional SQL y servicios de aprovisionamiento de IT. Actualmente expone una tool de ejemplo (`add`) y un resource de ejemplo (`greeting://{name}`) mientras se desarrollan las herramientas de negocio reales.
4. **LLM Local (`phi-4-mini-instruct`):** Se serviría vía **vLLM** con OpenAI-compatible API, consumido por el Host para el razonamiento del agente. **Pendiente de implementación:** hoy no existe servicio en `compose.yaml` ni código que lo invoque; solo hay variables de entorno de referencia (`LLM_URL`, `HUGGING_FACE_HUB_TOKEN`). Requeriría GPU (NVIDIA) para correr.

---

## 🔄 Flujo de Trabajo Operativo (Diseño objetivo)

> Este flujo describe el comportamiento objetivo del agente una vez completada la integración de los tres componentes. Hoy está validada la conectividad `mcp-host` ↔ `mcp-server-lines`, y el `mcp-server-outlook` ya expone de forma standalone sus 8 tools de lectura/gestión de correo. Lo que falta para completar este flujo es que el Host invoque esas tools de Outlook (paso 1) y que exista razonamiento contra un LLM (pasos 2, 3 y 5) — hoy ambas piezas están pendientes de implementación.

1. **Lectura y Monitoreo:** El Agente Host le ordena al servidor MCP de Outlook buscar correos no leídos con intenciones de soporte técnico.
2. **Análisis de Intención:** El LLM local analiza la consulta (Ej: *"Hola, necesito dar de alta una licencia de AutoCAD para el nuevo diseñador"*).
3. **Selección de Herramienta:** El LLM determina mediante capacidades funcionales que requiere ejecutar la herramienta expuesta por el servidor LINES.
4. **Validación y Ejecución:** El Host intercepta la llamada, aplica políticas de seguridad y ejecuta la acción sobre la base de datos SQL / API externa.
5. **Notificación de Cierre:** El LLM procesa el resultado exitoso de la operación y comanda al servidor de Outlook responder formalmente al solicitante con sus credenciales o confirmación.

---

## 🔒 Seguridad de Entorno Crítico (Diseño objetivo)

> Estas capas de seguridad son parte del diseño del sistema; el Human-in-the-Loop y el Dashboard de aprobación todavía no están implementados.

Debido a que el agente cuenta con privilegios de escritura en sistemas centrales, se implementan tres capas estrictas de seguridad:
* **Human-in-the-Loop (Mitigación de Inyecciones de Prompt Indirectas):** Para operaciones destructivas o críticas (como el reseteo de contraseñas de admin o asignación de licencias costosas), el Host congela de forma mandatoria la ejecución y solicita la firma/aprobación de un operador humano a través de un Dashboard antes de transferir la orden al servidor MCP.
* **Aislamiento de Red:** El servidor de administración de IT opera en una red privada virtualizada en Docker sin exposición directa a Internet, comunicándose estrictamente con el Host local.
* **Principio de Menor Privilegio:** Los tokens de autenticación están estrictamente restringidos al contexto operacional de la casilla asignada y esquemas específicos.

---

## 🛠️ Tecnologías Utilizadas

* **Python 3.12**
* **FastMCP / MCP SDK** (Abstracción de protocolo de alto nivel, transporte Streamable HTTP)
* **FastAPI** (Framework web asíncrono para el manejo de ciclo de vida e inyección de middleware de CORS)
* **Uvicorn** (Servidor web compatible con la especificación ASGI)
* **Pydantic Settings** (Carga y validación de configuración vía variables de entorno)
* **imaplib + MSAL** (Conexión IMAP a Exchange Online con autenticación OAuth2 client-credentials, usado por `mcp-server-outlook`)
* **uv** (Gestor de dependencias y entornos virtuales de Python)
* **vLLM** (Planeado para servir el LLM local `Phi-4-mini-instruct` con API compatible OpenAI — **aún no implementado**, ver sección de arquitectura)
* **Docker & Docker Compose** (Contenedorización y aislamiento de microservicios)

---

## 🚀 Despliegue y Testing Local

### Requisitos Previos
Tener instalado Docker, Docker Compose y Node.js (para la suite de testing con MCP Inspector). El LLM local (`phi-4-mini-instruct` vía vLLM) todavía no está implementado ni declarado en `compose.yaml`, así que no hace falta GPU para correr el proyecto hoy.

### 1. Configurar variables de entorno
Copiá el archivo de ejemplo y ajustá los valores según tu entorno:
```bash
cp .env.example .env
```
Los tres servicios (`mcp-host`, `mcp-server-lines` y `mcp-server-outlook`) leen su configuración desde variables de entorno (ver el `.env.example` de cada uno para el detalle). El servidor de Outlook además necesita credenciales de una app registrada en Azure AD con permisos IMAP sobre la casilla (`TENANT_ID`, `CLIENT_ID`, `CLIENT_SECRET`, `EMAIL_ACCOUNT`).

### 2. Iniciar los servicios en Docker
Para levantar los tres servicios declarados en `compose.yaml`:
```bash
docker compose up --build mcp-host mcp-server-lines mcp-server-outlook
```
- El **MCP LINES Server** queda escuchando en `http://localhost:8001/mcp` (transporte Streamable HTTP).
- El **MCP Outlook Server** queda escuchando en `http://localhost:8002/mcp` (transporte Streamable HTTP).
- El **MCP Host** queda escuchando en `http://localhost:8000` (FastAPI), con su cliente MCP embebido apuntando al server LINES vía la red interna de Docker.

Si solo querés probar la comunicación `mcp-host` ↔ `mcp-server-lines`, podés levantar únicamente esos dos:
```bash
docker compose up --build mcp-server-lines mcp-host
```

### 3. Testear el MCP LINES Server con MCP Inspector
El **MCP Inspector** es la herramienta oficial de desarrollo recomendada para validar la integridad de las herramientas expuestas de forma aislada, previniendo alucinaciones de modelos durante pruebas de infraestructura.

Desde una terminal en tu máquina local, usá el modo `--cli` del Inspector apuntando al endpoint Streamable HTTP del servidor para listar las tools disponibles:
```bash
npx @modelcontextprotocol/inspector --cli http://localhost:8001/mcp --transport http --method tools/list
```

Este comando ejecuta el handshake MCP completo y devuelve el catálogo de `Tools` (`add`) sin necesidad de intervención del LLM ni de abrir la interfaz web.

Con el mismo formato podés auditar el resto del protocolo variando `--method`:
```bash
# Listar resources disponibles
npx @modelcontextprotocol/inspector --cli http://localhost:8001/mcp --transport http --method resources/list

# Invocar la tool `add`
npx @modelcontextprotocol/inspector --cli http://localhost:8001/mcp --transport http --method tools/call --tool-name add --tool-arg a=2 --tool-arg b=3

# Leer el resource `greeting`
npx @modelcontextprotocol/inspector --cli http://localhost:8001/mcp --transport http --method resources/read --uri "greeting://Juan"
```

#### Alternativa: interfaz web interactiva
Si preferís explorar el servidor de forma interactiva en vez de por CLI, ejecutá el Inspector sin `--cli`:
```bash
npx @modelcontextprotocol/inspector
```
Y en la UI configurá **Transport Type** en `Streamable HTTP` y la URL en `http://localhost:8001/mcp`, luego presioná **Connect** para auditar en tiempo real el catálogo de `Tools` y `Resources`, ejecutar payloads JSON simulados y comprobar los registros de auditoría HTTP.

### 4. Testear el MCP Outlook Server con MCP Inspector
El servidor de Outlook queda expuesto en `http://localhost:8002/mcp` y requiere que las credenciales de Azure AD (`TENANT_ID`, `CLIENT_ID`, `CLIENT_SECRET`, `EMAIL_ACCOUNT`) estén correctamente configuradas en el `.env`, ya que sus tools se conectan de verdad a la casilla de Exchange Online vía IMAP.

```bash
# Listar las 8 tools disponibles (create_folder, move_email_to_folder, read, read_unread_items, read_all, decodificate_header, extract_body, parse_message)
npx @modelcontextprotocol/inspector --cli http://localhost:8002/mcp --transport http --method tools/list

# Leer los últimos 5 correos no leídos de INBOX
npx @modelcontextprotocol/inspector --cli http://localhost:8002/mcp --transport http --method tools/call --tool-name read_unread_items --tool-arg folder=INBOX
```

### 5. Testear la comunicación mcp-host ↔ mcp-server-lines
Con ambos contenedores levantados (paso 2), verificá que el Host pueda invocar herramientas del server LINES a través de su cliente MCP embebido:
```bash
curl "http://localhost:8000/demo/lines/add?a=2&b=3"
# esperado: {"result": 5}
```
