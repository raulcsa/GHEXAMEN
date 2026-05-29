# 🌐 Guía de CI/CD Enterprise — GlobalFin Services
## Documento de Arquitectura, Hardening y Respuestas de Exámenes

Este documento contiene el diseño teórico y técnico detallado desarrollado para cumplir con las políticas estrictas de seguridad, reutilización, escalabilidad y optimización de **GlobalFin Services**.

---

## 🔐 Ejercicio 2 — Seguridad Enterprise & OIDC

### 1. ¿Qué problema resuelve OIDC (OpenID Connect)?
En los pipelines de CI/CD tradicionales, para desplegar aplicaciones en proveedores de nube (como AWS, GCP o Azure), era obligatorio almacenar credenciales de larga duración (ej: contraseñas de cuentas de servicio, claves de acceso AWS `AccessKeyID`/`SecretAccessKey`) directamente como secretos del repositorio de GitHub. 

Esto presentaba tres problemas críticos de seguridad:
* **Riesgo de Exposición permanente:** Si una clave de larga duración es robada, el atacante tiene acceso ilimitado a los recursos de la empresa hasta que la clave sea rotada manualmente.
* **Sobrecarga de gestión:** Mantener políticas de rotación de contraseñas de bases de datos y nubes en miles de repositorios es complejo y propenso a errores.
* **Ausencia de contexto granular:** Las credenciales de larga duración suelen ser genéricas y no permiten auditar si la llamada la hizo una rama en particular o un workflow específico.

### 2. ¿Cómo mejora la seguridad?
OIDC elimina las credenciales de larga duración en GitHub. En su lugar, establece una **relación de confianza federada** entre GitHub y el proveedor de nube:
1. Al iniciar el job, el runner de GitHub solicita un **token OIDC JWT** temporal firmado criptográficamente por GitHub.
2. El runner presenta este token al proveedor de nube.
3. El proveedor de nube valida la firma de GitHub y lee los campos del token (ej. `repository`, `ref`/rama, `environment`).
4. Si coincide con la política de confianza, el proveedor de nube genera un **token de acceso temporal de corta duración** (ej. dura 15 minutos) con un rol de IAM específico.
5. El runner utiliza este token efímero para el despliegue. No hay secretos persistentes que robar.

### 3. ¿Cuándo utilizarlo?
Se debe utilizar **siempre** que se realicen despliegues hacia plataformas en la nube o herramientas de infraestructura (AWS, GCP, Azure, HashiCorp Vault, Kubernetes) que soporten autenticación por federación de identidades OIDC.

---

## 🚀 Ejercicio 4 — Estrategia de Self-Hosted Runners Enterprise

### 1. ¿Cuándo usar Self-Hosted Runners?
Se deben utilizar en los siguientes escenarios:
* **Requisitos de Red Privada:** Cuando el pipeline necesita conectarse a recursos inaccesibles desde internet (ej. bases de datos internas, clústeres de Kubernetes en VPCs privadas, servidores on-premises).
* **Hardware Especializado:** Cuando el proceso de compilación requiere GPU, grandes cantidades de RAM/CPU, o sistemas operativos no soportados por GitHub.
* **Cumplimiento y Privacidad (Compliance):** Regulaciones estrictas que prohíben que el código fuente o los datos de prueba salgan de la red física o virtual de la empresa.
* **Optimización de Costos y Almacenamiento:** Para monorepos masivos donde la descarga de dependencias y el caching local en red de alta velocidad reduce costes de red y de minutos de ejecución de GitHub.

### 2. Riesgos de Seguridad
El principal riesgo es que **cualquier workflow ejecutado en el runner tiene acceso a la máquina física/virtual y a la red donde reside**.
* Si un desarrollador o un atacante ejecuta código malicioso a través de una Pull Request (de un fork o de un usuario no verificado), este script puede escanear la red corporativa, persistir software malicioso en el disco del runner, o robar credenciales guardadas en la memoria o disco de la máquina.
* **Persistencia de estado:** Si el runner no es limpio entre ejecuciones, un job A puede dejar código o secretos que un job B puede leer.

### 3. Segmentación y Aislamiento de Runners
Para mitigar los riesgos, la empresa debe aplicar las siguientes reglas:
* **Uso de Ephemeral Runners:** Configurar runners que se destruyen automáticamente al finalizar un único job (ej. usando **Actions Runner Controller - ARC** sobre Kubernetes). Cada ejecución inicia en un contenedor limpio.
* **Runner Groups a Nivel de Organización:** Separar los runners en grupos y limitar qué repositorios tienen acceso a ellos.
* **Segmentación por Entornos:** Tener runners específicos para producción colocados en subredes aisladas de los runners de desarrollo/staging.
* **Network Hardening:** Permitir únicamente tráfico de salida hacia las IPs de GitHub (`HTTPS`). Bloquear todo tráfico entrante y restringir el acceso lateral en la red privada.

### 4. Uso de Labels
Los jobs deben solicitar recursos de forma precisa para evitar ejecutar tareas en máquinas incorrectas.
```yaml
runs-on: [self-hosted, linux, x64, aws-eks, environment-production]
```

### 5. Tabla Comparativa: Ventajas y Desventajas

| Característica | GitHub-Hosted Runners | Self-Hosted Runners |
| --- | --- | --- |
| **Mantenimiento** | Cero. GitHub se encarga de todo. | Alto. La empresa gestiona parches, OS y hardware. |
| **Seguridad de Red** | Ejecutado en la nube pública de GitHub. | Integrado en la red interna (VPC corporativa). |
| **Aislamiento** | Total. Máquinas virtuales limpias y dedicadas. | Requiere configuración propia (Docker/Kubernetes). |
| **Costes** | Pago por minuto de uso. | Coste de infraestructura fija + coste de administración. |
| **Performance** | Estándar. | Altamente personalizable y optimizable. |

---

## 🛠️ Ejercicio 5 — Guía de Troubleshooting Enterprise

### Caso A — El pipeline no ejecuta el deploy aunque los tests son correctos
* **Posibles causas:**
  1. **Restricción de Rama (Branch protection):** La condicional `if:` del job de despliegue limita la ejecución a `refs/heads/main` y el pipeline se está corriendo en una rama de feature (`feature/xyz`).
  2. **Dependencias del Grafo (`needs`):** Si el job de deploy depende de un job de compilación que fue omitido (`skipped`) debido a la ejecución selectiva (paths-filter), GitHub Actions omitirá automáticamente el deploy a menos que se use la función `always()` con validaciones lógicas del estado anterior.
  3. **Aprobación de Entorno Pendiente:** El environment de Staging o Production tiene configurada una regla de aprobación manual (Required Reviewers) y el pipeline está pausado a la espera del click del aprobador.
  4. **Fallo de Permisos OIDC:** El token de GitHub no tiene permiso de escritura (`id-token: write`), impidiendo que OIDC obtenga credenciales temporales de despliegue.
* **Diagnóstico:**
  1. Comprobar en el UI gráfico de GitHub el estado del job: ¿Aparece como `skipped` (omitido), `waiting` (esperando aprobación) o `failed`?
  2. Inspeccionar la expresión condicional del job `deploy` en el archivo YAML.
  3. Comprobar la pestaña de auditoría del Environment en `Settings -> Environments` para ver si hay bloqueos o aprobaciones pendientes.
* **Solución:**
  1. Si es por omisión selectiva de dependencias, ajustar la lógica condicional usando `always()` combinada con los estados de las dependencias (`success` / `skipped`), tal como se implementó en `staging-deploy`.
  2. Si es por permisos, asegurar que el job de deploy declara explícitamente:
     ```yaml
     permissions:
       contents: read
       id-token: write
     ```
  3. Si es por aprobación de entorno, instruir al equipo de operaciones a validar el run y presionar "Approve and deploy".

---

### Caso B — Una matrix genera más jobs de los esperados
* **Por qué ocurre / Identificación de errores:**
  Por defecto, la directiva `matrix` genera el producto cartesiano de todas las llaves y valores proporcionados. Si tenemos 3 plataformas y 3 versiones de runtime, GitHub generará 9 combinaciones ($3 \times 3$). Si agregamos variables adicionales como entornos o arquitecturas, el crecimiento es exponencial.
  Un error común ocurre al usar `include` de manera incorrecta: si definimos una matriz base y añadimos un `include` con llaves que no coinciden exactamente con la combinación de llaves existentes, GitHub interpretará que debe crear un nuevo job independiente con esas variables, aumentando el número de jobs en lugar de agregar propiedades a los existentes.
* **Solución:**
  1. Utilizar de forma explícita el bloque `exclude` para descartar combinaciones no válidas o redundantes en la infraestructura enterprise (como excluir versiones antiguas en macOS):
     ```yaml
     strategy:
       matrix:
         runs-on: [ubuntu-latest, macos-latest]
         node-version: [18, 20, 22]
         exclude:
           - runs-on: macos-latest
             node-version: 18
     ```
  2. Para pipelines donde solo se requieren combinaciones específicas fijas, prescindir del producto cartesiano y declarar directamente la lista completa en `include`:
     ```yaml
     strategy:
       matrix:
         include:
           - runs-on: ubuntu-latest
             node-version: 20
           - runs-on: macos-latest
             node-version: 22
     ```

---

### Caso C — Un reusable workflow no recibe correctamente outputs
* **Posibles causas y problemas de scope:**
  Los outputs en GitHub Actions tienen un alcance (`scope`) muy estricto. Un reusable workflow se ejecuta como un contenedor aislado. Para que el workflow llamador (`caller`) acceda a un valor del reusable, este valor debe pasar por 3 niveles de definición:
  1. **Nivel Step (dentro del Reusable):** El comando debe escribir en `$GITHUB_OUTPUT`.
  2. **Nivel Job (dentro del Reusable):** El job debe recoger ese output del step y declararlo bajo su sección `outputs`.
  3. **Nivel Trigger (en el Reusable):** La directiva de disparo `on.workflow_call.outputs` debe mapear el output del job del reusable.
  Si falla cualquiera de estas conexiones (por errores tipográficos o por omitir la declaración a nivel de job/trigger), el output llegará vacío al llamador.
* **Solución:**
  Configurar la tubería de outputs de la siguiente manera:
  
  *En el workflow Reusable (`reusable-build.yml`):*
  ```yaml
  on:
    workflow_call:
      outputs:
        # Nivel 3: Expone el output al Caller
        artifact-name:
          value: ${{ jobs.build.outputs.artifact-name }}

  jobs:
    build:
      # Nivel 2: Mapea el output del step al job
      outputs:
        artifact-name: ${{ steps.set-output.outputs.artifact-name }}
      runs-on: ubuntu-latest
      steps:
        - id: set-output
          # Nivel 1: Guarda el valor en el step
          run: echo "artifact-name=build-v1" >> $GITHUB_OUTPUT
  ```

  *En el workflow Caller (`ci-coordinator.yml`):*
  ```yaml
  jobs:
    build-job:
      uses: ./.github/workflows/reusable-build.yml

    deploy-job:
      needs: build-job
      runs-on: ubuntu-latest
      steps:
        - name: Use Output
          run: echo "Deploying: ${{ needs.build-job.outputs.artifact-name }}"
  ```

---

## ❓ Preguntas Teóricas Cortas

### 1. Diferencia entre hosted y self-hosted runners.
Los **hosted runners** son máquinas virtuales efímeras mantenidas por GitHub, que se destruyen por completo al finalizar cada job, garantizando un entorno limpio y seguro sin esfuerzo administrativo. Los **self-hosted runners** son servidores administrados por la propia organización, que ofrecen control de red local, personalización de hardware/software, pero conllevan el coste de mantenimiento, parches y control de seguridad.

### 2. Diferencia entre vars y secrets.
* **vars**: Almacenan configuraciones no confidenciales (URLs, nombres de proyectos). Son editables en texto claro y legibles en los logs.
* **secrets**: Almacenan datos confidenciales (tokens, contraseñas). GitHub los encripta en reposo y en tránsito, y enmascara activamente su salida (`***`) en los logs de ejecución si un script intenta imprimirlos.

### 3. Cuándo usar reusable workflow frente a composite action.
* **Reusable Workflow**: Se utiliza para estandarizar e integrar **jobs completos**. Permite definir condicionales, matrices, boundings a entornos (`environments`), secretos dedicados y múltiples jobs paralelos en el mismo archivo.
* **Composite Action**: Se utiliza para reutilizar una **secuencia lógica de pasos (steps)** dentro de un único job. Se ejecuta en el mismo runner del job llamador, compartiendo su sistema de archivos directamente y no soporta configuraciones de job individuales (como `runs-on` o `concurrency`).

### 4. Qué riesgos tiene usar actions externas sin pinning.
El principal riesgo es el **secuestro de la cadena de suministro (Supply Chain Attack)**. Si una Action externa se referencia usando un tag mutable (ej: `@v4` o `@main`), un atacante que logre acceder al repositorio original de la action puede inyectar código malicioso en ese tag. Al ejecutarse el pipeline de GlobalFin Services, dicho código obtendría acceso de lectura/escritura a nuestro repositorio y variables de entorno. Al utilizar version pinning con el **hash SHA de 40 caracteres**, nos aseguramos de ejecutar exactamente el commit auditado y validado, inmune a modificaciones posteriores.

### 5. Qué ventajas aporta OIDC.
Aporta tres grandes ventajas:
1. Elimina las credenciales de larga duración en GitHub (reduciendo el vector de ataque por robo de secretos).
2. Otorga credenciales de acceso dinámicas y efímeras automáticas que expiran en pocos minutos.
3. Permite aplicar políticas de mínimos privilegios en la nube basadas en metadatos del workflow (sólo permite despliegues desde la rama `main` y desde un repositorio específico).

### 6. Qué contexts suelen provocar más errores.
Los contextos **`secrets`** (por estar vacíos en PRs de forks o no mapearse en workflows reusables), **`steps`** (por errores tipográficos en el ID del step al intentar leer outputs), y **`needs`** (por intentar leer salidas de jobs que no fueron declarados explícitamente en el bloque `needs:` del job actual).

### 7. Qué diferencia existe entre parse-time y runtime.
* **Parse-time:** Es la fase previa a la ejecución donde GitHub valida y compila la estructura del workflow YAML (evalúa condicionales `if` del job, la generación de matrices, las dependencias y la sintaxis básica).
* **Runtime:** Es la fase de ejecución real en el runner, donde se ejecutan los comandos del bloque `run` y se evalúan las variables de entorno locales del sistema operativo.

### 8. Qué ventajas aporta concurrency.
Aporta optimización de recursos y consistencia de estado:
1. Evita condiciones de carrera (`race conditions`) impidiendo que múltiples deploys sobreescriban el mismo entorno a la vez.
2. Ahorra tiempo y recursos al cancelar ejecuciones anteriores que aún no han terminado en una misma rama cuando llega un nuevo cambio (`cancel-in-progress: true`).
