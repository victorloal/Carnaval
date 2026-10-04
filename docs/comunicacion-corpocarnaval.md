# Contact with Corpocarnaval — the permission request

- **Status:** **Drafted, not sent.** 2026-10-04
- **Required by:** brief §11 and §20; `docs/00-acta-proyecto.md` §6 (C6), §12.2 item 2;
  `docs/fuentes-y-atribucion.md` §9.5; `docs/02-diseno/despliegue.md` §10
- **Why it matters:** it is the mitigation for the missing terms of use (§9.5 of the source
  register) **and** the last chance to hear an objection before the site is public. It is
  the only protection of its kind that is actually within reach.

> **Sending this is a human act.** It is drafted here so that what will be said is reviewable
> before it is said, and so the answer can be recorded in the repository afterwards. Nothing
> in this file has been sent to anyone.

## 1. The recipient is still an open gap

The source spike of 2026-10-03 enumerated all 19 pages and 42 posts and found **no public
email address** anywhere on the official site (`docs/fuentes-y-atribucion.md` §9.5). What it
did find on the homepage:

| Found | Implication |
|---|---|
| Links to `corpocarnaval.com` | The most likely route to a real address — open that site and look for a contact form |
| Three `wa.me` WhatsApp links | A fallback. A WhatsApp message is weaker evidence than email: it is not a durable record, so anything binding should be confirmed in writing afterwards |
| Social network accounts | Another fallback, and the least appropriate channel for a permission request |

**Rule for this contact: ask for permission by email, not over WhatsApp.** If the only route
available is WhatsApp or a social network, send the same text and then ask for the reply by
email, so there is a written record. A permission that exists only in a chat log is not a
permission anyone can later prove.

## 2. What will actually be collected

Stated here so the letter makes no promise the project does not keep.

| Item | What is taken | What is **never** taken |
|---|---|---|
| **Programme** (`carnavaldepasto.org`, WordPress REST API) | Day names, event dates and times, venues, and the description text needed to identify each event. Read-only requests | The schedule **PDF** is never redistributed and never committed to the repository |
| **Editions** | Page titles and URLs identifying a carnival edition by year | — |
| **News** | Headline (verbatim is acceptable), canonical URL, outlet name, publication date, and a **short original summary** written for this site | Never the article body. Never the outlet's images |
| **Historical photographs** | **Only** where author, source, licence and citation are recorded and `rights_status` is known | Any photograph with unknown rights, including any photograph taken from the official site. Images where a minor is the focal subject are not published without guardian authorisation |
| **Anything else** | — | Full texts, PDFs, photographs, logos, video files. Videos are external links (YouTube / Vimeo embeds), never hosted or re-uploaded |

## 3. How the site will behave

| | |
|---|---|
| **`robots.txt`** | Verified 2026-10-03: `Disallow: /wp-admin/` only, no `Crawl-delay`. Re-checked before every collection run |
| **Rate limiting** | A fixed minimum interval between requests, configured conservatively and lowered only deliberately — roughly one request every few seconds, never in bursts |
| **`User-Agent`** | Identifiable, carrying a contact address that reaches a human. Exactly: `CarnavalPrograma/1.0 (+https://github.com/victorloal/Carnaval; victorloal513@gmail.com)` |
| **Authentication** | None. Read-only, no login, nothing submitted to the site |
| **Retries** | Backoff plus a circuit breaker that disables a source after repeated failures, so a broken site is not hammered |
| **Idempotency** | Every record is keyed by a content hash, so re-running collection never creates duplicates |
| **Availability** | The database is the source of truth. If the official site disappeared tomorrow, the site would keep serving what it already holds |
| **Affiliation** | **None.** The site is unofficial, states so on every page including error pages, and is not affiliated with, endorsed by, or official with Corpocarnaval or any parade organiser. The name is used descriptively to refer to the event, never as a brand |
| **Publication** | Every item is staged as `pending` and published only after a human reviews it. Nothing goes live automatically |
| **Takedown** | A published contact address, a documented removal procedure, and no deadline — a removal request is never refused for arriving late |
| **Nature of the project** | Personal, non-commercial. No advertising, no ticket sales, no user accounts, no monetisation of any kind. The source code is public under the MIT licence (code only, never content) |

## 4. The letter

Spanish, because the recipient is Colombian and this is correspondence rather than
repository content — the repository's English rule governs documents, not letters. The wording
matches §2 and §3 above.

**Subject:** Solicitud de permiso para publicar y citar información del Carnaval de Negros y
Blancos

```text
Estimados señores de Corpocarnaval:

Mi nombre es Victor Lopez y les escribo desde Colombia. Estoy desarrollando un sitio web
personal y sin fines comerciales dedicado a la información del Carnaval de Negros y Blancos
de Pasto: su programación, su historia y, más adelante, fotografías históricas aportadas por
la comunidad. No es un negocio: no tiene publicidad, no vende tiquetes, no pide registro a
ningún visitante y no busca lucro de ninguna forma.

Antes de publicar nada quería solicitarles su permiso y, sobre todo, courtinglesmente su
opinión. Este proyecto no está afiliado, ni respaldado, ni cuenta con el aval de Corpocarnaval
ni de ninguna organización del Carnaval, y el sitio lo dirá de forma visible en todas sus
páginas. Si creen que esto no es apropiado, con gusto lo retiro.

QUÉ RECOPILARÍA

- La programación del Carnaval publicada en carnavaldepasto.org: los nombres de los días, las
  fechas, las horas y los lugares de cada evento, y las descripciones necesarias para
  identificar cada actividad. Serían únicamente lecturas.
- Los datos que identifican cada edición del Carnaval, es decir, el año y la página
  correspondiente.
- Noticias de prensa: sólo el titular, el enlace original, el medio, la fecha y un resumen
  breve y propio, escrito para este sitio. Nunca el texto completo del artículo ni sus
  imágenes.

QUÉ NO RECOPILARÍA NUNCA

- El PDF de la programación: no se redistribuye ni se publica en el repositorio del proyecto.
- Fotografías, salvo aquellas cuya autoría, fuente, licencia y cita queden registradas y sean
  de derechos conocidos. No publicaría ninguna imagen de derechos desconocidos, ni
  fotografías tomadas del sitio oficial, ni imágenes donde un menor sea el sujeto principal
  sin autorización de su tutor.
- Textos completos, archivos, logotipos ni archivos de video. Los videos se enlazan a su
  plataforma original; nunca se alojan ni se vuelven a subir.

CÓMO LO HARÍA

- Respetaría el robots.txt del sitio, que ya verifiqué: sólo prohíbe /wp-admin/. Lo volvería
  a comprobar antes de cada recolección.
- Haría las peticiones con una pausa fija entre una y otra, sin ráfagas, y con un
  identificador User-Agent que incluye mi nombre, el enlace al proyecto y mi correo para que
  puedan contactarme en cualquier momento.
- No usaría usuario ni contraseña: sólo lecturas.
- Cada dato se guardaría como pendiente de revisión humana. Nada se publica de forma
  automática.
- Cada elemento publicado llevaría su atribución: fuente, medio y fecha.

QUÉ LE PIDO

1. Su autorización para publicar y citar esa información, en los términos descritos arriba.
2. Su opinión sobre el proyecto, aunque no autoricen nada: si algo les parece equivocado o
   fuera de lugar, preferiría saberlo antes de publicar y no después.
3. Que cualquier respuesta o objeción me llegue por correo, para poder actuar sobre ella y
   dejarla registrada.

Quedo atento. El proyecto es de código abierto y pueden revisar el repositorio completo,
incluidas las reglas de atribución y el procedimiento de retiro de contenido:
https://github.com/victorloal/Carnaval

Muchas gracias por su tiempo y su atención.

Atentamente,
Victor Lopez
Pasto, Nariño, Colombia
victorloal513@gmail.com
```

## 5. Before sending

- [ ] **Choose the channel** (§1) — email if at all possible.
- [ ] **Add the address of the site itself.** The letter deliberately cites only the code
      repository, because the public site does not exist yet. Once there is an address, add
      it to the last paragraph; sending a request that cites a URL nobody can open wastes the
      one good first impression this contact gets.
- [ ] **Re-read §2 and §3 against the letter.** If the implementation later starts
      collecting something not listed in §2, this letter becomes inaccurate and must be
      corrected — the letter's value depends entirely on it being true.
- [ ] **Record the outcome** in §6 on the day it arrives.

## 6. Outcome register

Empty until the letter is sent. Fill it in with what actually happened, not with what was
hoped for — including if there is no answer.

| Field | Value |
|---|---|
| Date sent | — |
| Channel used | — |
| Recipient (name, role) | — |
| Exact reply received | — |
| Date of reply | — |
| Permission granted? | — |
| Conditions or restrictions imposed | — |
| Changes made as a result | — |
| Recorded in `fuentes-y-atribucion.md` §9 | — |

## 7. If the answer is no

This is the outcome the request exists to make possible, so it is decided now rather than in
the moment it arrives.

- **A refusal ends collection from that source immediately.** `scrape_sources.is_active`
  goes to `false` and stays there — the circuit breaker's permanent-disable path, used as
  intended.
- **Already-published items derived from that source are withdrawn**, not archived. Their
  status returns to `pending` and the change is recorded in `audit_logs` with a reason.
- **The programme stays available.** The database is the source of truth (ADR 0002), so
  disabling a source stops future collection; it does not empty the site.
- **The not-affiliated disclaimer does not overrule an explicit objection.** If Corpocarnaval
  asks the site to stop, it stops.
- **Silence is not permission.** No reply leaves the risk state exactly as §9.5 of the source
  register records it: accepted, unresolved, and reversible.