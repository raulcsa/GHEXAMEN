# 🚀 GlobalFin Services — Plataforma CI/CD Monorepo Enterprise

Este repositorio contiene la solución completa y estandarizada para la plataforma CI/CD corporativa utilizando **GitHub Actions**.

---

## 📋 Estructura del Monorepo

El monorepo está estructurado para permitir el desarrollo paralelo de frontend, backend e infraestructura, manteniendo un aislamiento lógico de la documentación y los scripts de soporte:

*   **[frontend/](file:///home/raul/GHEXAMEN/frontend/)**: Componente frontend en Node.js (con linter, tests y build).
*   **[backend/](file:///home/raul/GHEXAMEN/backend/)**: Microservicio API backend en Node.js (con linter, tests y validaciones).
*   **[infrastructure/](file:///home/raul/GHEXAMEN/infrastructure/)**: Declaraciones de infraestructura en Terraform y script de validación [validate.sh](file:///home/raul/GHEXAMEN/infrastructure/validate.sh).
*   **[docs/](file:///home/raul/GHEXAMEN/docs/)**: Documentos globales de arquitectura y gobernanza.
    *   **[CI_CD_ENTERPRISE_GUIDE.md](file:///home/raul/GHEXAMEN/docs/CI_CD_ENTERPRISE_GUIDE.md)**: Guía teórica detallada sobre OIDC, estrategias de Self-hosted Runners, diagnóstico de Troubleshooting y respuestas teóricas.
*   **[scripts/](file:///home/raul/GHEXAMEN/scripts/)**: Scripts utilitarios del repositorio.
    *   **[simulate-ci.py](file:///home/raul/GHEXAMEN/scripts/simulate-ci.py)**: Herramienta interactiva para simular el comportamiento de la ejecución selectiva del pipeline de forma local.

---

## 🛠️ Arquitectura de Pipelines Reutilizables

Se han diseñado workflows con responsabilidades únicas que se parametrizan dinámicamente desde el orquestador principal:

1.  **[reusable-validate.yml](file:///home/raul/GHEXAMEN/.github/workflows/reusable-validate.yml)**: Centraliza la sintaxis y linter. Ejecuta validaciones de sintaxis y linter tanto para Node.js como para la infraestructura de Terraform.
2.  **[reusable-test.yml](file:///home/raul/GHEXAMEN/.github/workflows/reusable-test.yml)**: Abstrae y ejecuta pruebas unitarias. Se parametriza para soportar múltiples sistemas operativos y versiones de runtime de forma paralela.
3.  **[reusable-build.yml](file:///home/raul/GHEXAMEN/.github/workflows/reusable-build.yml)**: Centraliza la compilación del código y archiva el resultado empaquetado como artefacto seguro de GitHub Actions.

### El Orquestador Principal
*   **[ci-coordinator.yml](file:///home/raul/GHEXAMEN/.github/workflows/ci-coordinator.yml)**: Es el cerebro del pipeline. Realiza el análisis de cambios de ruta, ejecuta de manera condicional los pipelines de validación, pruebas matriciales y builds correspondientes, y coordina las fases de despliegue y generación de informes en Markdown.

---

## 🔒 Hardening de Seguridad Enterprise

Nuestra plataforma CI/CD implementa políticas de seguridad alineadas con estándares de gobernanza strictos:
*   **Privilegio Mínimo (Least Privilege):** El token `GITHUB_TOKEN` está restringido por defecto a nivel global con `permissions: { contents: read }`. Únicamente los jobs que requieren establecer federación OIDC elevan el permiso a `id-token: write` de forma aislada.
*   **Inmutabilidad de Dependencias (Supply Chain Hardening):** Todas las acciones externas de terceros utilizan version pinning con el **commit SHA de 40 caracteres** en lugar de etiquetas mutables (tags). Esto bloquea ataques de inyección de código de terceros.
*   **Aislamiento de Entornos (Staging vs Production):** El despliegue de producción está asociado a un environment de GitHub con reglas de protección configuradas, obligando a una aprobación manual y limitando ejecuciones únicamente desde la rama `main`.
*   **Federación de Identidades (OIDC):** Diseño conceptual de autenticación sin secretos persistentes en GitHub para la interacción con los proveedores de nube.

---

## ⚡ Estrategias de Optimización

*   **Ejecución Selectiva (Selective Execution):** Mediante `dorny/paths-filter`, se evalúa qué carpetas han cambiado. Si un cambio sólo ocurre en `/docs`, el pipeline completo de código se omite (`skipped`). Si sólo cambia frontend, el backend e infraestructura no se compilan ni testean, ahorrando cientos de minutos de cómputo.
*   **Control de Concurrencia:** Evitamos race conditions en despliegues concurrentes mediante la directiva `concurrency`, cancelando automáticamente ejecuciones redundantes anteriores en la misma rama.
*   **Caché de Dependencias:** El pipeline reusables de Node.js utiliza la caché nativa de `actions/setup-node` mapeada al archivo `package.json` de cada componente para restaurar `node_modules` al instante.
*   **Matriz Optimizada:** Exclusión explícita de combinaciones costosas (como ejecutar pruebas con Node 18 en macOS-latest).

---

## 💻 Validación y Simulación Local

Para verificar el comportamiento dinámico de la plataforma sin requerir un runner en la nube, utilice las siguientes herramientas integradas:

### 1. Ejecutar las pruebas manuales locales
Compruebe la funcionalidad y sintaxis de los tres componentes principales en su terminal:
```bash
# Probar Frontend
npm run test --prefix frontend

# Probar Backend
npm run test --prefix backend

# Validar Infraestructura
./infrastructure/validate.sh
```

### 2. Ejecutar el Simulador de CI
Ejecute la herramienta de simulación interactiva:
```bash
python3 scripts/simulate-ci.py
```

El script le presentará opciones para simular cambios específicos (por ejemplo, cambios exclusivos en frontend, combinados frontend/backend, o cambios reales en su Git local) y ejecutará los comandos locales simulando la lógica de decisión condicional del orquestador, generando el reporte markdown de salida en **`CI_REPORT_MOCK.md`**.
