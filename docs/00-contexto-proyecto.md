# Contexto del proyecto: Carnaval de Negros y Blancos

> Documento de contexto. Resume qué se va a construir, por qué, qué se ha decidido y qué falta por definir.
> Última actualización: 3 de octubre de 2026 (v3: pila decidida, sin JWT, sitio bilingüe)

> **⚠ Estado: parcialmente superado.** Este es el brief original y se conserva como registro
> de la intención inicial. Los ADR en `docs/adr/` **prevaleecen** sobre cualquier frase de este
> documento. Donde discrepan, la lista completa de desviaciones está en
> `docs/00-acta-proyecto.md` §9. Los párrafos ya reconciliados citan su ADR.

---

## 1. Resumen

Proyecto personal de portafolio: una **plataforma web sobre el Carnaval de Negros y Blancos de Pasto (Nariño, Colombia)** con:

- Un **backend que recopila datos automáticamente** (web scraping) desde fuentes públicas, en lugar de servir JSON estáticos.
- Una **base de datos como fuente de verdad**, que también almacena contenido editorial: noticias e imágenes históricas con su citación.
- Un **panel de administración** con Django admin, protegido con sesiones de servidor, TOTP, roles y políticas de seguridad, desde el cual se configura el sitio y se **aprueba o rechaza** la información recolectada (ADR 0005).
- **Contribuciones públicas** (sin registro) de imágenes y enlaces de video, que quedan en estado pendiente hasta ser moderadas, con aceptación de términos y políticas.

El objetivo no es solo la página final, sino **demostrar el proceso completo de ingeniería de software**: requisitos, diseño, seguridad, implementación, pruebas, despliegue y documentación, todo versionado en un único repositorio.

> **Aviso:** proyecto personal sin fines comerciales. No está afiliado ni respaldado por Corpocarnaval ni por ninguna entidad organizadora del carnaval.

## 2. Problema

- No se encontró una **API pública oficial** ni un dataset abierto del carnaval (se revisó datos.gov.co y la página oficial).
- La información existe en el sitio oficial (**carnavaldepasto.org**) y en un PDF de programación, pero no está estructurada para ser consumida por otras aplicaciones.
- No existe un espacio que reúna de forma ordenada y con citación correcta el material histórico (noticias, fotografías antiguas) ni que permita a la comunidad aportar contenido de manera moderada.

## 3. Objetivos

**General:** construir un sistema que recopile, valide, modere y exponga la información del carnaval mediante una API propia, un panel de administración y una interfaz web.

**Específicos:**
1. Diseñar e implementar un pipeline de ingesta (extracción → validación → staging → carga) con detección de cambios y tolerancia a fallos.
2. Mantener una base de datos editorial con noticias e imágenes históricas con autor, fuente, licencia y citación.
3. Implementar un panel de administración con sesiones de servidor y TOTP, control de acceso por roles, auditoría y moderación (ADR 0005).
4. Permitir contribuciones públicas con cuarentena, aceptación de términos y revisión previa a publicar.
5. Exponer los datos mediante una API REST documentada con OpenAPI.
6. Construir un frontend accesible, rápido y pensado primero para móvil.
7. Documentar todo el ciclo de desarrollo (SRS, modelo de amenazas, diagramas, ADRs, plan de pruebas, retrospectivas).
8. Desplegar el sistema a costo cero.

## 4. Alcance por versiones

Se entrega de forma incremental para que siempre haya algo funcionando y desplegado.

| Versión | Contenido |
|---|---|
| **MVP** | Pipeline de programación, base de datos, API pública de lectura, frontend |
| **v1** | Django admin con sesiones y TOTP, roles, cola de revisión de lo recolectado, auditoría |
| **v2** | Noticias, galería histórica con citaciones, configuración del sitio y de las fuentes de scraping |
| **v3** | Contribuciones públicas (imágenes y enlaces de video), moderación, términos y privacidad |

**Fuera del alcance (por ahora)**
- Venta de boletas o cualquier función transaccional.
- Cuentas públicas de usuario (las contribuciones se hacen sin registro).
- Alojar archivos de video propios (se aceptan enlaces a plataformas externas).
- Aceptar archivos arbitrarios (ejecutables, scripts, documentos).
- Mostrar publicidad en el sitio.
- Reproducir contenido protegido (fotos, textos completos, PDFs de terceros) sin permiso.
- Aplicación móvil nativa.

## 5. Hallazgos de la investigación inicial

- La página oficial es **carnavaldepasto.org**, construida con WordPress y Elementor.
- Publica la programación por día. Para el carnaval de enero, los hitos principales son: 2 de enero (Carnavalito), 3 (colectivos coreográficos), 4 (Desfile Familia Castañeda), **5 (Día de Negros)** y **6 (Día de Blancos / Desfile Magno)**.
- Ofrece la programación completa en PDF, además de secciones de historia, participación y galería.
- ~~**Por verificar:** si el sitio expone la WordPress REST API (`/wp-json/wp/v2/pages` y
  `/posts`)~~ → **Verificado 2026-10-03:** sí responde (HTTP 200, 368 rutas, sin
  autenticación para lectura), así que es la fuente preferida por encima del scraping de
  HTML (FR-B-15, ADR 0002). Registro completo en `docs/fuentes-y-atribucion.md` §9.
- La programación cambia **una vez al año**; la edición de enero de 2027 probablemente se publique cerca de diciembre de 2026. Se desarrollará primero con datos de la edición 2026.

## 6. Decisiones tomadas

| # | Decisión | Motivo | ADR |
|---|----------|--------|-----|
| 1 | Backend que recopila datos (sin JSON estáticos) | Demostrar ingeniería de datos y resiliencia | 0002 |
| 2 | La **base de datos es la fuente de verdad**; el scraper solo propone cambios | El sitio sigue funcionando si el scraping falla | 0002 |
| 3 | Metodología **Scrumban** (sprints de 1 semana + tablero Kanban) | Proyecto individual; fuentes inciertas | 0001 |
| 4 | **Monorepo** con documentación y código juntos | Mostrar todo el proceso en un solo lugar | 0003 |
| 5 | Licencia **MIT** para el código; los datos y contenidos no quedan cubiertos | Permisiva y conserva la autoría | 0004 |
| 6 | Despliegue en capas gratuitas (Vercel o Cloudflare, Postgres gratuito, GitHub Actions) | Costo cero | — (plataformas aún por confirmar) |
| 7 | Auth propio con **librerías probadas** (Argon2id, TOTP), no criptografía propia | Demostrar seguridad aplicada | 0005 |
| 8 | ~~JWT con refresh rotativo~~ → **Sesiones de servidor en cookie `httpOnly`**, nada en `localStorage` | La revocación central es más fuerte que la rotación de tokens, y no hay panel en React | **0005 (reemplaza la decisión original)** |
| 9 | Videos de la comunidad como **enlaces externos**, no archivos propios | Costo de almacenamiento y riesgo legal | 0007 |
| 10 | Contribuciones públicas en **v3**, tras tener moderación y documentos legales | Evitar contenido sin quien lo revise | 0008 |
| 11 | **Python 3.12 + Django 5 + DRF**; React solo para el sitio público | El admin es la pieza dominante, y Django la entrega con poco código propio | 0009 |
| 12 | El **sitio público es bilingüe** (es como idioma fuente, en secundario) | La audiencia local es hispanohablante; el portafolio necesita inglés | 0010 |
| 13 | `openapi.yaml` **se genera** y CI falla si hay *drift* | Un contrato escrito a mano se desincroniza sin avisar | 0011 |

> **Por qué cambió la decisión 8.** El brief pedía un access token de vida corta y un refresh
> rotativo. Se descartó porque con sesiones de servidor la revocación es central e inmediata
> (`delete` de la fila en `django_session`), mientras que la rotación de refresh exige
> mantener un almacén de tokens revocados — más superficie, sin ganancia. Como además **no hay
> panel en React** (el admin es Django admin), no existe cliente que deba portar un token: la
> cookie es el único artefacto. Ver ADR 0005.

## 7. Arquitectura propuesta

```
Fuentes externas ──► Scrapers ──► Staging (pending) ──┐
                                                       │
Admin (carga manual: noticias, imágenes) ─────────────►│
                                                       ▼
Visitantes (contribuciones) ─► Cuarentena ─► Cola de revisión ─► Aprobar / Rechazar
                                                       │
                                                       ▼
                                            PostgreSQL (published)
                                                       │
                              API pública (lectura) + Django admin (sesión + TOTP + roles)
                                                       │
                                        Frontend público (React) + /admin (misma aplicación)
```

**Pipeline de ingesta**

```
Fuentes (carnavaldepasto.org, PDF, WP REST API)
   → EXTRACT → RAW STORE (documento crudo + hash) → TRANSFORM (validación con esquema)
   → STAGING (pending) → revisión → LOAD (upsert en PostgreSQL, published)
```

**Principios**
- **Idempotente:** ejecutarlo dos veces no duplica datos.
- **Detección de cambios por hash:** no se reprocesa lo que no cambió.
- **Trazabilidad:** cada registro guarda su origen (`scraped`, `manual` o `community`) y la ejecución o el usuario que lo generó.
- **Nada se publica sin revisión**, salvo reglas explícitas definidas por el administrador.

**Si el scraping falla**
- Lo ya publicado no se borra ni se degrada.
- El administrador puede crear y editar todo manualmente; el scraper es una comodidad, no una dependencia.
- Reintentos con espera creciente y *circuit breaker*: tras N fallos seguidos la fuente se marca como deshabilitada y se genera una alerta.
- El panel muestra el estado de cada fuente y la última ejecución exitosa.

## 8. Modelo de datos (inicial)

**Programación y pipeline:** `editions`, `days`, `events`, `venues`, `sources`, `raw_documents`, `ingestion_runs`, `scrape_sources` (fuentes configurables desde el admin: URL, tipo, frecuencia, activa).

**Contenido editorial:**
- `news_items`: título, URL original, medio, fecha, resumen propio, origen, estado.
- `media_assets`: archivo, año aproximado, descripción, autor, fuente, **licencia**, **texto de citación**, estado de derechos, estado de publicación.
- `site_settings`: configuración editable (clave/valor).

**Seguridad y administración:** `auth_user`, `auth_group`, `django_session`, `otp_totpdevice`, `audit_logs`. No hay tabla `refresh_tokens`: con sesiones de servidor la revocación es un borrado de fila (ADR 0005).

**Contribuciones públicas:** `submissions`, `submission_files`, `consent_records`, `takedown_requests`, `moderation_actions`, `legal_documents` (versionado de términos y políticas).

**Campos comunes de moderación** (en `events`, `news_items`, `media_assets`, `submissions`): `status` (`pending` / `published` / `rejected`), `reviewed_by`, `reviewed_at`, `rejection_reason`, `origin`.

## 9. Seguridad del panel de administración

> **Reconciliado por ADR 0005.** El brief pedía access token + refresh rotativo; se sustituyó por
> sesiones de servidor. Todo lo demás de esta sección se mantiene.

- Contraseñas con **Argon2id** (vía `django-argon2`; no se escribe criptografía propia).
- **Sesiones de servidor** en PostgreSQL. El navegador solo guarda una clave opaca en una cookie
  `httpOnly`, `Secure`, `SameSite=Lax`. **No hay JWT ni token de bearer en ninguna parte**, y
  nada se escribe en `localStorage` (ADR 0005).
- **Revocación central e inmediata:** cerrar sesión o revocarla borra la fila en
  `django_session`. Es la razón principal para descartar la rotación de refresh tokens.
- La clave de sesión **rota al iniciar sesión**, lo que neutraliza la fijación de sesión.
- Protección **CSRF** en toda petición que modifica estado.
- **MFA con TOTP** para administradores, con códigos de recuperación de un solo uso.
- **RBAC** con mínimo privilegio, verificado siempre en el servidor: `admin`, `editor` (aprueba contenido), `viewer`.
- **Sin registro público de administradores**; el primer admin se crea con un script de siembra.
- Límite de intentos de login, bloqueo temporal y **sin enumeración de usuarios** (mismo
  mensaje y misma forma de respuesta para contraseña incorrecta, cuenta inactiva o segundo
  factor incorrecto).
- **Registro de auditoría** de cada aprobación, rechazo y cambio de configuración, de solo
  adición e imutable incluso para `admin`.
- Validación estricta de entradas, CORS restringido, cabeceras de seguridad (CSP, HSTS), HTTPS siempre, secretos solo en variables de entorno.
- Escaneo de dependencias (Dependabot). Referencias: **OWASP Top 10 y ASVS**.
- **Modelo de amenazas (STRIDE)** documentado en `docs/02-diseno/`.

## 10. Contribuciones públicas (v3)

**Flujo**

```
Visitante → formulario → CAPTCHA + límite de envíos → aceptación de términos
 → validación del archivo → CUARENTENA (almacenamiento privado)
 → estado "pending" → revisión del admin
 → aprobado: pasa a almacenamiento público
 → rechazado: se elimina o conserva según la política, con motivo registrado
```

**Aceptación de términos**
- Casilla no premarcada y bloqueante.
- Registro en `consent_records`: versión del texto aceptado, fecha y hora, hash de la IP (no la IP en claro).
- Declaración del autor: es el autor o tiene permiso; se piden autor, año, lugar y descripción.
- Autorización no exclusiva para mostrar el contenido en el sitio, con crédito; licencia Creative Commons opcional.
- Declaración de consentimiento de las personas identificables. **No se publican imágenes donde un menor sea el foco sin autorización de sus responsables.**
- Correo de contacto para avisos y solicitudes de retiro.

**Seguridad de los archivos**
- Lista blanca estricta (imágenes JPG, PNG, WebP), verificada por el contenido real (*magic bytes*), no por la extensión.
- Límites de tamaño y de cantidad por envío y por visitante.
- Reprocesamiento de imágenes para eliminar código incrustado y **borrado de metadatos EXIF** (incluida la ubicación GPS).
- **Cuarentena** en almacenamiento privado; solo al aprobarse pasan al público.
- Archivos servidos desde un dominio o bucket distinto al de la aplicación, con `X-Content-Type-Options: nosniff` y `Content-Disposition` adecuado.
- Subida directa con URLs firmadas de corta duración.
- Detección de duplicados por hash.
- **Videos:** solo enlaces a YouTube o Vimeo mostrados con *embed*, en la primera versión.

**Protección contra abuso:** CAPTCHA (por ejemplo Cloudflare Turnstile), *honeypot*, límite de envíos por IP, cuota global diaria de pendientes, verificación de correo opcional.

**Contenido ilegal grave:** no se publica ni se redistribuye, y se denuncia a las autoridades competentes o a líneas como Te Protejo. Debe existir un procedimiento escrito para moderadores.

## 11. Consideraciones legales y éticas

> Orientación general, no asesoría legal. Los textos legales finales conviene revisarlos con un profesional.

- La licencia MIT cubre **solo el código**, no los datos recopilados ni el contenido de terceros.
- Citar siempre la fuente y declarar que no es un sitio oficial.
- Respetar `robots.txt` y los términos de uso de las fuentes; identificarse con un *User-Agent* con datos de contacto y limitar la frecuencia de peticiones.
- **Imágenes antiguas no significan libres de derechos.** Una imagen no puede publicarse sin autor, fuente, licencia y citación; si el estado de derechos es `desconocido`, no se publica.
- **Noticias:** se guarda titular, enlace, medio, fecha y un **resumen propio breve**; nunca el artículo ni sus imágenes completos.
- No publicar en el repositorio copias de PDFs, fotos ni textos completos de terceros (`data/raw/` y `*.pdf` van en `.gitignore`).
- **Documentos legales a redactar:** términos y condiciones de uso; política de contenido y publicación (incluye publicidad comercial no autorizada); política de privacidad y tratamiento de datos (Ley 1581 de 2012, habeas data); procedimiento de notificación y retiro (*takedown*).
- Se recomienda contactar a Corpocarnaval para informarles del proyecto y consultar el uso de contenidos.

## 12. Pila tecnológica

| Capa | Tecnología | Estado |
|------|-----------|--------|
| Backend (pipeline + API + admin) | **Python 3.12, Django 5, DRF**, `psycopg` 3, ORM y migraciones propias | **Decidido** (0009) |
| Base de datos | **PostgreSQL 16** | **Decidido** (0009); proveedor por confirmar |
| Almacenamiento de archivos | Dos capas: **cuarentena privada y público**, en dominios separados | **Decidido** (0006); proveedor por confirmar, R2 favorece por no cobrar salida |
| Programación de tareas | GitHub Actions (`cron`) → comando de gestión | **Decidido** (0009). Sin worker residente |
| Frontend | **React + TypeScript + Vite**, solo el sitio público | **Decidido** (0009) |
| Panel de administración | **Django admin** — no hay panel en React | **Decidido** (0005, 0009) |
| Autenticación | **Sesiones de servidor + TOTP** (`django-otp`), `httpOnly`/`Secure`/`SameSite` | **Decidido** (0005). Sin JWT |
| API | REST + OpenAPI **generado** con drf-spectacular; CI falla si hay *drift* | **Decidido** (0011) |
| Idiomas | **es** (fuente) y **en**, con *fallback* a `es`; una clave `en` ausente rompe la compilación | **Decidido** (0010) |
| Calidad | Ruff, mypy | Decidido (0009) |
| Anti-abuso | Cloudflare Turnstile u otro CAPTCHA | Tentativo |
| Pruebas | **pytest** + pytest-django, Playwright, axe, Lighthouse | **Decidido** (0009) |
| Diagramas | Mermaid (versionado en el repo) y draw.io | Decidido |
| Diseño UI | Figma (plan gratuito) | Tentativo |

> Los límites de los planes gratuitos cambian con frecuencia. Verificarlos en la documentación oficial antes de publicar.

## 13. Restricciones

- **Costo cero** en infraestructura.
- Desarrollo por **una sola persona**, a tiempo parcial.
- Dependencia de **fuentes externas** que pueden cambiar de estructura o dejar de estar disponibles.
- Los **derechos de autor** de los contenidos pertenecen a sus titulares.
- Almacenamiento y ancho de banda limitados por las capas gratuitas.

## 14. Riesgos iniciales

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| El sitio cambia su estructura y rompe el scraper | Alto | Fixtures de prueba, alertas, preferir la WP API, carga manual desde el admin |
| Errores al extraer datos del PDF | Medio | Staging con revisión antes de publicar |
| Bloqueo por parte de la fuente | Medio | Peticiones limitadas, caché por hash, contacto previo |
| Reclamo por derechos de autor | Alto | Atribución obligatoria, estado de derechos, procedimiento de retiro, no copiar contenido protegido |
| Compromiso de cuentas de administrador | Alto | MFA, tokens de vida corta, auditoría, mínimo privilegio |
| Archivos maliciosos en contribuciones | Alto | Lista blanca, reprocesado, cuarentena, dominio separado |
| Contenido ilegal o inapropiado enviado por el público | Alto | Cuarentena, moderación previa, procedimiento de denuncia |
| Spam y agotamiento del almacenamiento gratuito | Medio | CAPTCHA, límites por IP, cuota diaria |
| Datos personales y menores en imágenes | Alto | Declaración de consentimiento, política de privacidad, hash de IP, regla sobre menores |
| Cambio en los límites de los planes gratuitos | Bajo | Arquitectura portable |
| Alcance excesivo para una persona | Alto | Entrega por versiones, priorización MoSCoW, sprints cortos |

## 15. Nota de honestidad técnica

La programación del carnaval cambia una vez al año, por lo que un pipeline continuo con moderación y contribuciones públicas es más de lo que el problema estrictamente exige. Se construye **de forma deliberada** para demostrar ingeniería de datos, seguridad y gestión de riesgos, y así debe declararse en el README.

## 16. Metodología

**Scrumban adaptado a un proyecto individual:**
- Fase 0 corta (2-3 días): acta, requisitos de alto nivel y arquitectura base.
- Sprints de 1 semana con objetivo claro; notas de planificación y retrospectiva en `docs/sprints/`.
- Tablero en GitHub Projects: `Backlog → Listo → En curso → Revisión → Hecho`, con límite de 2 tareas en curso.
- Primer sprint técnico dedicado a un *spike* para explorar las fuentes (WP API, HTML, PDF).
- **Definición de "hecho":** código con pruebas, documentación actualizada, CI en verde y requisito enlazado en la matriz de trazabilidad.

## 17. Estructura del repositorio

```
carnaval-negros-blancos/
├── docs/
│   ├── 00-contexto-proyecto.md
│   ├── 00-acta-proyecto.md
│   ├── 01-requisitos/        (srs, historias de usuario, matriz de trazabilidad)
│   ├── 02-diseno/            (C4, modelo de datos, flujo de datos, modelo de amenazas, roles y permisos, openapi.yaml)
│   ├── 03-pruebas/           (plan de pruebas, casos de seguridad)
│   ├── legal/                (términos, política de contenido, privacidad, procedimiento de retiro)
│   ├── adr/                  (decisiones de arquitectura)
│   ├── sprints/              (planificación y retrospectivas)
│   └── fuentes-y-atribucion.md
├── backend/                  (reservado; vacío en Fase 0)
├── frontend/                 (reservado; vacío en Fase 0)
├── tests/                    (reservado; vacío en Fase 0)
├── .github/                  (workflows, plantillas de issues y PR) — todavía no existe
├── AGENTS.md                 (reglas para agentes que trabajan en el repo)
├── MEMORY.md                 (estado de sesión, 50 líneas máximo)
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md               — pendiente, se escribe con el código
├── LICENSE
└── README.md
```

> `backend/`, `frontend/`, `tests/` y `.github/` están reservados y vacíos: la Fase 0 es solo
> documentación. El árbol completo está en `docs/02-diseno/despliegue.md` y el estado real en
> `MEMORY.md`.

**Convenciones:** rama `main` siempre estable y protegida; ramas cortas (`docs/...`, `feat/...`, `fix/...`); commits en formato Conventional Commits (`docs:`, `feat:`, `fix:`, `chore:`, `test:`).

## 18. Hoja de ruta

1. **Inicio:** acta del proyecto y análisis de interesados.
2. **Requisitos:** SRS (RF/RNF numerados, MoSCoW por versión, requisitos de seguridad, privacidad y moderación), historias de usuario y matriz de trazabilidad.
3. **Diseño:** diagramas (casos de uso, C4, flujo de datos, entidad-relación, secuencia, despliegue, roles y permisos, máquina de estados `pending → published/rejected`, secuencia de autenticación con sesión y TOTP), modelo de amenazas, contrato OpenAPI y ADRs.
4. **Spike de fuentes:** probar la WP API, analizar el HTML y el PDF.
5. **MVP:** pipeline, base de datos, API pública y frontend.
6. **v1:** Django admin, sesiones y TOTP, roles, cola de revisión y auditoría.
7. **v2:** noticias, galería con citaciones, configuración del sitio y de las fuentes.
8. **v3:** contribuciones públicas, cuarentena, moderación y documentos legales.
9. **CI/CD y observabilidad (continuo):** GitHub Actions, `ingestion_runs`, endpoint `/health`, pruebas de seguridad.
10. **Cierre:** README final, documentación de la API y retrospectiva.

Opcional: 3 o 4 videos cortos (demo, arquitectura, pipeline en acción, retrospectiva), grabados al final de cada fase.

## 19. ADRs

Quince en total. **0001 a 0014 ya están escritos** en `docs/adr/`; falta 0015 (coste de
salida de red).

- 0001: Metodología Scrumban — *escrito*
- 0002: Backend de ingesta con base de datos como fuente de verdad — *escrito*
- 0003: Monorepo — *escrito*
- 0004: Licencia MIT para el código — *escrito*
- 0005: Autenticación por sesión de Django con TOTP, **sin JWT** — *escrito* (sustituye el JWT del brief)
- 0006: Almacenamiento de imágenes y cuarentena — *escrito*
- 0007: Videos como enlaces externos — *escrito*
- 0008: Entrega incremental por versiones — *escrito*
- 0009: Pila Python/Django/DRF + PostgreSQL — *escrito*
- 0010: Sitio público bilingüe es/en — *escrito*
- 0011: OpenAPI generado con comprobación de *drift* — *escrito*
- 0012: Traducciones como columnas `*_es`/`*_en`, sin tabla genérica — *escrito*
- 0013: Defaults de las decisiones abiertas del SRS §9 (timeouts, retención, búsqueda) — *escrito*
- 0014: Herramienta de diagramas (Mermaid, C4 aproximado) — *escrito*
- 0015: Coste de salida de red (R2 frente a Supabase Storage) — *pendiente*

## 20. Pendientes

Los puntos ya resueltos se sacaron de esta lista; quedan los que dependen de una acción
externa o de una decisión aún abierta. Ver `MEMORY.md` para el estado vigente.

- [x] Verificar si `carnavaldepasto.org/wp-json/wp/v2/pages` responde. → **Sí, verificado
      2026-10-03**: HTTP 200, 368 rutas, sin autenticación para lectura. Ver
      `docs/fuentes-y-atribucion.md` §9.2.
- [ ] Revisar los términos de uso del sitio y registrarlo en `docs/fuentes-y-atribucion.md`.
      El `robots.txt` **ya se revisó** (2026-10-03: permite todo salvo `/wp-admin/`, sin
      `Crawl-delay`), pero los términos de uso **no se encontraron** en las 19 páginas ni
      en los 42 artículos. Ver §9.5.
- [ ] Crear el tablero de GitHub Projects.
- [ ] **Escribir a Corpocarnaval** para informarles del proyecto. Es cortesía y la última
      oportunidad de saber de una objeción antes de que el sitio sea público.
- [ ] Confirmar los límites vigentes de los planes gratuitos elegidos, y re-verificarlos antes
      de cada publicación (los límites cambian).
- [ ] Elegir los proveedores concretos de hosting, base de datos y almacenamiento (ADR 0015
      cubriría el criterio de coste de salida).
- [ ] Cerrar los borradores de `docs/legal/` con **revisión profesional** antes de iniciar la v3.
- [ ] Cerrar las decisiones abiertas del SRS §9: estrategia de traducciones, tiempos de sesión,
      retención de documentos crudos y buscador.
- [ ] Definir y publicar una dirección de contacto para quejas y retiradas.

## 21. Glosario

- **Ingesta:** proceso de obtener datos de fuentes externas y cargarlos en el sistema.
- **Staging:** zona intermedia donde los datos esperan validación antes de publicarse.
- **Cuarentena:** almacenamiento privado donde quedan los archivos enviados hasta ser revisados.
- **Idempotencia:** propiedad por la cual repetir una operación produce el mismo resultado.
- **Edición:** carnaval de un año específico.
- **RBAC:** control de acceso basado en roles.
- **JWT (*Json Web Token*):** token firmado para autenticación. **Este proyecto NO lo usa**; se
  descartó a favor de sesiones de servidor (ADR 0005).
- **EXIF:** metadatos de una imagen, que pueden incluir ubicación.
- **Takedown:** solicitud de retiro de contenido.
- **ADR:** registro de decisión de arquitectura.
- **MoSCoW:** priorización de requisitos (Must, Should, Could, Won't).
- **SRS:** especificación de requisitos de software.
- **STRIDE:** método de modelado de amenazas.
