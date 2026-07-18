# 🛠️ MCP & Support Agent for TICS

Este proyecto implementa la arquitectura de un **Agente de Inteligencia Artificial Autónomo** diseñado para la administración automatizada y soporte técnico de infraestructura de TI. El agente procesa solicitudes de usuarios finales recibidas a través de correos electrónicos corporativos (Outlook) y ejecuta operaciones de administración lógica —como creación de usuarios, reseteo de contraseñas y asignación de licencias de software (ej. AutoCAD)— de manera segura utilizando el estándar **Model Context Protocol (MCP)**.

---

## 🏗️ Arquitectura del Sistema

El sistema se basa en un desacoplamiento completo de responsabilidades mediante microservicios encapsulados en contenedores independientes que se comunican utilizando **SSE (Server-Sent Events)** sobre HTTP.

<img width="1243" height="553" alt="MCP Arquitecture" src="https://github.com/lines-frlp-utn/mcp-tics-agent/blob/main/docs/mcp-tics-agent.jpg?raw=true" />

### Componentes Clave:
1. **Model & Agent Host (Contenedor Core):** El cerebro del sistema. Orquesta el bucle de razonamiento de la IA. El **MCP Client** vive embebido dentro de este proceso y actúa como el traductor de protocolo universal.
2. **MCP Outlook Server (Contenedor Satélite):** Expone herramientas específicas al modelo para buscar, leer y responder correos electrónicos de soporte de forma segura a través de la API Graph de Microsoft.
3. **MCP LINES Server (Este Repositorio):** Desarrollado en Python con **FastMCP** y **FastAPI**. Provee acceso controlado a la base de datos transaccional SQL y servicios de aprovisionamiento de IT.

---

## 🔄 Flujo de Trabajo Operativo

1. **Lectura y Monitoreo:** El Agente Host le ordena al servidor MCP de Outlook buscar correos no leídos con intenciones de soporte técnico.
2. **Análisis de Intención:** El LLM local analiza la consulta (Ej: *"Hola, necesito dar de alta una licencia de AutoCAD para el nuevo diseñador"*).
3. **Selección de Herramienta:** El LLM determina mediante capacidades funcionales que requiere ejecutar la herramienta expuesta por el servidor LINES.
4. **Validación y Ejecución:** El Host intercepta la llamada, aplica políticas de seguridad y ejecuta la acción sobre la base de datos SQL / API externa.
5. **Notificación de Cierre:** El LLM procesa el resultado exitoso de la operación y comanda al servidor de Outlook responder formalmente al solicitante con sus credenciales o confirmación.

---

## 🔒 Seguridad de Entorno Crítico

Debido a que el agente cuenta con privilegios de escritura en sistemas centrales, se implementan tres capas estrictas de seguridad:
* **Human-in-the-Loop (Mitigación de Inyecciones de Prompt Indirectas):** Para operaciones destructivas o críticas (como el reseteo de contraseñas de admin o asignación de licencias costosas), el Host congela de forma mandatoria la ejecución y solicita la firma/aprobación de un operador humano a través de un Dashboard antes de transferir la orden al servidor MCP.
* **Aislamiento de Red:** El servidor de administración de IT opera en una red privada virtualizada en Docker sin exposición directa a Internet, comunicándose estrictamente con el Host local.
* **Principio de Menor Privilegio:** Los tokens de autenticación están estrictamente restringidos al contexto operacional de la casilla asignada y esquemas específicos.

---

## 🛠️ Tecnologías Utilizadas

* **Python 3.12**
* **FastMCP / MCP SDK** (Abstracción de protocolo de alto nivel)
* **FastAPI** (Framework web asíncrono para el manejo de ciclo de vida e inyección de middleware de CORS)
* **Uvicorn** (Servidor web compatible con la especificación ASGI de pre-vuelo)
* **Docker & Docker Compose** (Contenedorización y aislamiento de microservicios)

---

## 🚀 Despliegue y Testing Local

### Requisitos Previos
Tener instalado Docker, Docker Compose y Node.js (para la suite de testing).

### 1. Iniciar el Servidor en Docker
Clonar el repositorio y ejecutar el entorno de microservicios:
```bash
docker compose up --build
```
El servidor LINES pasará a escuchar peticiones **Streamable HTTP** (el transporte MCP recomendado para clientes remotos) en `http://localhost:8000/mcp`.

### 2. Testear el Protocolo con MCP Inspector
El **MCP Inspector** es la herramienta oficial de desarrollo recomendada para validar la integridad de las herramientas expuestas de forma aislada, previniendo alucinaciones de modelos durante pruebas de infraestructura.

Desde una terminal en tu máquina local, usá el modo `--cli` del Inspector apuntando al endpoint Streamable HTTP del servidor para listar las tools disponibles:
```bash
npx @modelcontextprotocol/inspector --cli http://localhost:8000/mcp --transport http --method tools/list
```

Este comando ejecuta el handshake MCP completo y devuelve el catálogo de `Tools` (`add`) sin necesidad de intervención del LLM ni de abrir la interfaz web.

Con el mismo formato podés auditar el resto del protocolo variando `--method`:
```bash
# Listar resources disponibles
npx @modelcontextprotocol/inspector --cli http://localhost:8000/mcp --transport http --method resources/list

# Invocar la tool `add`
npx @modelcontextprotocol/inspector --cli http://localhost:8000/mcp --transport http --method tools/call --tool-name add --tool-arg a=2 --tool-arg b=3

# Leer el resource `greeting`
npx @modelcontextprotocol/inspector --cli http://localhost:8000/mcp --transport http --method resources/read --uri "greeting://Juan"
```

#### Alternativa: interfaz web interactiva
Si preferís explorar el servidor de forma interactiva en vez de por CLI, ejecutá el Inspector sin `--cli`:
```bash
npx @modelcontextprotocol/inspector
```
Y en la UI configurá **Transport Type** en `Streamable HTTP` y la URL en `http://localhost:8000/mcp`, luego presioná **Connect** para auditar en tiempo real el catálogo de `Tools` y `Resources`, ejecutar payloads JSON simulados y comprobar los registros de auditoría HTTP.