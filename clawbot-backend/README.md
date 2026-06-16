# ClawBot Backend

Backend de recepción de reportes de auditoría de seguridad para el proyecto
**ClawBot** (basado en OpenClaw). Recibe reportes JSON estandarizados
generados por las Agent Skills (vía Report Sender), los valida, y en
etapas futuras los persistirá en Oracle Database para ser consumidos por
un dashboard en Oracle APEX.

## Etapa actual (1/3)

Esta entrega cubre:

- Estructura modular del proyecto FastAPI.
- Validación estricta del esquema de reportes mediante Pydantic.
- `POST /api/reports` para recibir reportes de cualquier skill presente o futura.
- `GET /api/reports` y `GET /api/reports/{id}` como utilidades temporales
  de desarrollo (almacenamiento en memoria, se perderá al reiniciar el proceso).
- Autenticación simple por API key (header `X-API-Key`), opcional en desarrollo.
- Configuración lista para desplegar en Render.

Lo que **todavía no incluye** (próximas etapas):

1. Conexión y persistencia real en Oracle Database.
2. Endpoints GET definitivos, optimizados para los widgets de Oracle APEX
   (Security Score global, histórico, hallazgos por severidad/skill/agente, etc.).

## Estructura del proyecto

```
clawbot-backend/
├── app/
│   ├── main.py                  # Punto de entrada FastAPI
│   ├── config.py                # Configuración vía variables de entorno
│   ├── api/
│   │   ├── deps.py               # Dependencias compartidas (auth)
│   │   └── routes/
│   │       └── reports.py        # Endpoints POST/GET de reportes
│   ├── core/
│   │   └── exceptions.py         # Excepciones y manejadores globales
│   ├── models/
│   │   ├── report.py             # Esquema Pydantic del reporte (entrada)
│   │   └── response.py           # Modelos de respuesta (salida)
│   ├── repositories/
│   │   ├── base.py               # Interfaz abstracta ReportRepository
│   │   ├── memory.py             # Implementación temporal en memoria
│   │   └── dependency.py         # Único punto de "wiring" del repositorio
│   └── services/
│       └── report_service.py     # Lógica de negocio
├── requirements.txt
├── render.yaml
├── Procfile
├── .env.example
└── .gitignore
```

### Por qué esta separación

- **`models/report.py`** no sabe nada de FastAPI ni de bases de datos: solo
  define qué es un reporte válido. Cualquier skill nueva que respete este
  esquema es aceptada automáticamente, sin tocar el backend.
- **`repositories/`** aísla la persistencia detrás de una interfaz
  (`ReportRepository`). Hoy existe `InMemoryReportRepository`; en la
  siguiente etapa se agregará `OracleReportRepository` implementando la
  misma interfaz, y el único archivo que cambiará es
  `repositories/dependency.py`. Ni los routers ni los servicios se modifican.
- **`services/`** contiene la lógica de negocio, independiente de HTTP.
  Esto facilita escribir tests y reutilizar lógica si en el futuro se
  agregan otras formas de ingesta (por ejemplo, un endpoint batch).
- **`api/`** es la única capa que conoce FastAPI: routers, dependencias de
  request (headers, auth) y wiring de servicios.

## Ejecución local

```bash
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload
```

La API quedará disponible en `http://127.0.0.1:8000`. Documentación
interactiva automática en `http://127.0.0.1:8000/docs`.

## Probar el endpoint

```bash
curl -X POST http://127.0.0.1:8000/api/reports \
  -H "Content-Type: application/json" \
  -H "X-API-Key: tu_api_key_si_la_configuraste" \
  -d @ejemplo_reporte.json
```

Si el JSON no cumple el esquema, la respuesta será `422` con el detalle
exacto de los campos inválidos. Si la API key es incorrecta o falta
(cuando `REPORT_API_KEY` está configurada), la respuesta será `401`.

## Despliegue en Render

1. Subir este repositorio a GitHub.
2. En Render: **New + → Blueprint**, apuntando al repo (usará `render.yaml`).
3. Configurar la variable de entorno `REPORT_API_KEY` desde el dashboard
   de Render (está marcada como `sync: false` para no versionarla).
4. Render usará automáticamente `healthCheckPath: /health`.

## Variables de entorno

| Variable          | Descripción                                              | Default |
|-------------------|-----------------------------------------------------------|---------|
| `APP_NAME`        | Nombre de la app                                          | ClawBot Backend |
| `ENVIRONMENT`     | `development` / `production`                              | development |
| `REPORT_API_KEY`  | API key exigida en `X-API-Key` para endpoints de reportes  | (vacío = sin auth) |
| `ALLOWED_ORIGINS` | Orígenes permitidos para CORS, separados por coma          | `*` |

## Próximos pasos

1. **Etapa 2 — Oracle Database**: diseño normalizado (`AGENTS`, `SKILLS`,
   `REPORTS`, `FINDINGS`, `RECOMMENDATIONS`, `REPORT_METADATA`),
   `OracleReportRepository` usando `python-oracledb`, manejo de pool de
   conexiones y transacciones al guardar un reporte completo (cabecera +
   findings + recomendaciones).
2. **Etapa 3 — Endpoints para Oracle APEX**: vistas/endpoints GET
   agregados y filtrables (por agente, skill, severidad, rango de fechas),
   pensados para alimentar los widgets del dashboard.
