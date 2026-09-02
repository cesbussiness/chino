# Guía Interactiva Meituan/JD — Contexto del proyecto

## Qué es esto

Guía interactiva HTML (offline, un solo archivo) para que Ramone aprenda mandarín
usando vocabulario **verificado directamente de capturas de pantalla reales** de
dos apps chinas: **Meituan** (美团, mainland) y **京东/JD** — específicamente su
canal HK超市 (Hong Kong, escritura tradicional). Uso: clase de chino con un
profesor, navegando las apps reales.

Principio rector de todo el proyecto (instrucción explícita del usuario desde el
día 1): **"no asumas nada, investiga"**. Nada de vocabulario se inventó — todo
viene de OCR/lectura directa de capturas, o de fuentes verificadas por herramienta
(CC-CEDICT, no memoria del modelo) cuando se trata de significados de caracteres,
agrupaciones de palabras o tonos.

## Estado actual

- **Separado en `src/`**: `src/index.html` + `src/style.css` + `src/app.js`
  (split hecho en Claude Code, verificado byte a byte contra el HTML
  monolítico original antes de borrarlo — reconstruir las 3 piezas da
  exactamente el archivo viejo, solo cambian `<style>`/`<script>` inline por
  `<link>`/`<script src>`). `index.html` sigue teniendo las imágenes e iconos
  embebidos como `data:` URIs directo en el HTML (por el bug de iOS Quick
  Look, ver más abajo), así que sigue pesando ~2.2 MB.
- **Build script**: `node build.js` (sin dependencias, Node nativo) lee
  `src/index.html` + `src/style.css` + `src/app.js` e injerta el CSS/JS
  inline de vuelta, generando `dist/Guia_Meituan_Chino_Interactiva.html` — el
  único archivo autocontenido para abrir con doble clic o mandar por
  WhatsApp/mail. Verificado byte a byte contra el HTML monolítico original
  (antes de que se borrara del repo). `dist/` está en `.gitignore` (es
  artefacto generado) — correr el build después de cualquier cambio en
  `src/` antes de distribuir.
- Antes de esto, todo el desarrollo fue **iterativo por chat**: cada cambio
  era un parche de texto (Python `str.replace`) directamente sobre el HTML
  monolítico. Eso se estaba poniendo frágil (bugs de cascada CSS por orden de
  reglas, dificultad para revisar diffs, archivo gigante) — de ahí la mudanza
  a Claude Code + git con archivos separados y diffs reales.

## Estructura de este export

```
repo_export/
├── PROJECT_CONTEXT.md          <- este archivo
├── Guia_Meituan_Chino_Interactiva.html   <- el archivo final actual (fuente de verdad)
├── data/
│   ├── VOCAB.json               <- 256 términos, 23 secciones (hanzi/pinyin/inglés/tipo de escritura)
│   ├── CHAR_DICT.json           <- 456 caracteres individuales (pinyin + significado)
│   ├── CHAR_OVERRIDES.json      <- excepciones de tono por palabra (polifónicos: 了, 乐)
│   ├── WORD_GROUPS.json         <- agrupaciones de 2+ caracteres verificadas en CC-CEDICT
│   ├── TONE_GAME_DATA.json      <- 217 preguntas del juego de tonos (correcta + 5 distractores)
│   └── icons/
│       ├── ICONS_HOME.json      <- iconos recortados de Meituan (páginas 1-3 del menú)
│       ├── ICONS_WAIMAI.json    <- iconos de categorías de 外卖
│       ├── ICONS_BNH.json       <- iconos nav inferior de Meituan
│       ├── ICONS_BNW.json       <- iconos nav inferior de 外卖
│       ├── ICONS_JD_MSG.json    <- iconos de 消息 (JD)
│       ├── ICONS_JD_PROFILE.json<- iconos de 我的 (JD)
│       └── ICONS_JD_BOTTOMNAV.json <- iconos nav inferior de JD
└── assets/
    └── screenshots/             <- 12 capturas de pantalla ya redimensionadas/comprimidas
                                     (las que se muestran junto al vocabulario en cada seccion)
```

Los JSON de `data/` y las imágenes de `assets/` son exactamente los mismos datos
que están embebidos dentro del HTML — los extraje frescos del archivo final para
que Code no tenga que hacer regex sobre un archivo de 2.4MB para editarlos.

**Importante**: las 456 entradas de `CHAR_DICT.json` y las 217 de
`TONE_GAME_DATA.json` fueron auditadas y corregidas contra **CC-CEDICT real**
(librería `pycccedict`, no memoria del modelo) — ver sección de bugs corregidos
abajo antes de tocar esos archivos.

## Qué hace la guía (features)

Pestañas: Introducción · Pantalla Principal (Meituan 首页, 3 páginas de iconos) ·
外卖 Delivery · 京东 JD/HK超市 · 🔗 En común · Glosario completo · Práctica.

**Práctica** tiene 4 modos, todos comparten nivel/sección + filtro de escritura:
1. **📇 Tarjetas de repaso** — flashcard clásica, se voltea para ver pinyin+inglés
   + desglose de caracteres.
2. **🎮 Juego: Adivina** — 4 opciones de traducción al inglés, con puntaje/racha.
3. **🔗 Juego: Emparejar** — memorama hanzi↔inglés.
4. **🎵 Juego: Tonos** — 6 opciones de pinyin con las mismas letras, solo cambian
   los tonos (para practicar oído tonal).

Filtros globales, aplican a los 4 modos por igual: nivel (① comunes / ②
pantallas principales / ③ submenús / 🔀 todo), sección específica (dropdown
con las 23 secciones reales — si se elige una, anula el nivel; elegir un
nivel la resetea a "todas"), **"Solo chino simplificado"** (excluye 36
términos tradicionales que vienen del canal HK超市 de JD, marcados con badge
繁), y **"📌 Repasar falladas"** (cola de palabras falladas, compartida entre
los 3 juegos, se vacía cuando las aciertas).

Cada palabra de 2-8 caracteres muestra, al voltear/responder:
- Desglose de significado por carácter individual (`CHAR_DICT`, con excepciones
  contextuales via `CHAR_OVERRIDES` para polifónicos).
- Si 2+ caracteres consecutivos forman una palabra real de diccionario, también
  se muestra esa agrupación (`WORD_GROUPS`), ej. 地图找店 → además de los 4
  caracteres sueltos, muestra "地图 (dìtú) = map".

**Audio**: Web Speech API del navegador (no hay audio pregrabado — se investigó
generar audio real vía gTTS/edge-tts pero los endpoints están bloqueados en el
entorno de la sesión que lo construyó). Control de velocidad 1/8x a 1x, y
selector de voz si el sistema tiene más de una voz china instalada.

## Metodología de verificación de datos (importante para mantener el estándar)

- **Vocabulario de las apps** (`VOCAB.json`): leído directamente (OCR humano/manual)
  de las capturas de pantalla, nunca inventado. Cada término tiene su sección de
  origen y se puede rastrear a una captura específica en `assets/screenshots/`.
- **Iconos**: recortados con Python/PIL de las capturas originales usando
  coordenadas calibradas por proporción (no genéricos de internet) — son los
  iconos reales de la app.
- **Significados de caracteres** (`CHAR_DICT.json`): conocimiento de diccionario
  estándar, verificado contra CC-CEDICT vía `pycccedict` en la auditoría final.
- **Agrupaciones de palabras** (`WORD_GROUPS.json`): generadas con matching
  greedy contra CC-CEDICT (no jieba solo, porque jieba fallaba en casos como
  "神券商家" → "券商"), con lista de exclusión manual para falsos positivos
  encontrados en revisión humana.
- **Datos del juego de tonos** (`TONE_GAME_DATA.json`): pinyin reconstruido
  carácter por carácter desde `CHAR_DICT`, luego **auditado exhaustivamente**
  comparando cada subcadena de 2+ caracteres contra el pinyin de palabra
  completa en CC-CEDICT (968 subcadenas revisadas). Si vas a regenerar o tocar
  este archivo, hay que volver a correr esa auditoría — no confíes en la
  reconstrucción carácter-por-carácter a ciegas para palabras con caracteres
  polifónicos.

## Bugs reales encontrados y corregidos (historial, por si reaparecen)

1. **Cascada CSS**: reglas "compactas" quedaron ANTES en el `<style>` que las
   reglas originales del mismo selector → las originales (más grandes) ganaban
   por orden de aparición. Se movieron al final del stylesheet. **Lección**: si
   se separa CSS en archivos, cuidado con el orden de `@import`/concatenación.
   **Actualización (ver bug #5)**: ese bloque "compacto" movido al final
   (`FINAL OVERRIDES`) se pasó de rosca y terminó achicando el texto de
   Práctica en todas las pantallas, no solo donde hacía falta — se eliminó y
   se reemplazó por tamaños responsivos (`clamp()`) directo en las reglas
   base, sin necesidad de un segundo bloque compitiendo por especificidad.
2. **Race condition en `speak()`**: `speechSynthesis.cancel()` seguido
   inmediatamente de `.speak()` en el mismo tick a veces no aplicaba bien el
   nuevo `rate` en Chrome/Edge. Se agregó `setTimeout(..., 60)` entre ambos.
3. **13 errores de tono verificados** en `TONE_GAME_DATA` — todos por
   caracteres polifónicos que no toman el mismo tono en toda palabra:
   `消息(xi neutro)`, `直播(bō, era typo bò)`, `度假(jià)`, `美发(fà)`,
   `排行榜(háng)`, `了解(liǎo)`, `香港行貨(háng)`, `逛逛/看看(2da sílaba neutra)`,
   `乐器(yuè)`. Ver `CHAR_OVERRIDES.json` para los casos donde el mismo
   carácter necesita dos lecturas distintas dentro del propio vocabulario
   (了: le vs liǎo: 乐: lè vs yuè).
4. **iOS Quick Look**: las imágenes se cargaban originalmente vía JS
   (`placeholder` + swap), lo que fallaba si iOS abría el archivo en vista
   previa (sin JS). Se cambió a `<img src="data:...">` directo en el HTML.
5. **Practica: texto diminuto + demasiado scroll (reportado por el usuario)**.
   Dos causas independientes, ambas en `src/style.css`:
   - El bloque `FINAL OVERRIDES` al final del stylesheet (ver bug #1)
     forzaba fuentes chiquitas (`.font-size:.72rem`–`1.6rem` fijos) en
     tarjetas, juegos y emparejar **en todas las pantallas** (no estaba
     dentro de ningún `@media`), de ahí que hiciera falta hacer zoom incluso
     en desktop. Se borró el bloque entero y se pasaron los tamaños "buenos"
     directo a las reglas base con `clamp()` para que escalen con el ancho de
     pantalla en vez de estar fijos.
   - `.menu-panel{display:block}` mantenía el menú de navegación (con las 7
     pestañas + control de velocidad de audio) siempre expandido en mobile —
     en desktop ya era colapsable con el botón ☰. Se unificó: colapsado por
     defecto en cualquier tamaño de pantalla, el JS del botón ☰ ya tenía toda
     la lógica de toggle lista y sin usar en mobile.
   - Extra: `.level-switch`/`.mode-switch` (los botones de nivel y modo de
     practica) pasaron de `flex-wrap:wrap` (se apilaban en 2-3 filas) a
     scroll horizontal de una sola fila (`overflow-x:auto` + `white-space:
     nowrap`), para no gastar alto de pantalla en eso.
   Verificado con Playwright en viewport de celular (390×844): antes hacía
   falta scroll incluso con fuente 27px; después el modo tarjetas entra
   completo sin scroll con fuente ~39px.
6. **`.tones-wrap` sin estilos propios**: a diferencia de `.game-wrap`
   (Adivina), el contenedor del juego de Tonos nunca tuvo la regla de
   flex/centrado — en pantallas anchas eso hacía que las opciones quedaran
   pegadas al margen izquierdo mientras la palabra arriba sí se veía
   centrada (bug reportado por el usuario junto con el pedido de mejorar el
   layout). Se agregó `.tones-wrap` a la regla compartida con `.game-wrap`.
   De paso, a pedido del usuario, en desktop (`min-width:901px`) Adivina y
   Tonos pasan a un layout de 2 columnas via CSS Grid (`grid-template-areas`):
   la palabra/icono a la izquierda, opciones+feedback+boton siguiente a la
   derecha, en vez de todo apilado en una columna angosta con espacio vacio
   a los costados. Mobile no cambia (sigue apilado en una sola columna).
7. **Auditoria completa de datos (VOCAB/CHAR_DICT/WORD_GROUPS/TONE_GAME_DATA),
   pedida por el usuario tras notar inconsistencias**. Metodologia: se
   extrajeron los 4 objetos embebidos en `app.js` a JSON y se cruzaron,
   programa por programa (no a ojo), contra **CC-CEDICT real** via
   `pycccedict` (mismo criterio que ya describe este documento), mas
   reconstruccion caracter-por-caracter desde `CHAR_DICT`+`CHAR_OVERRIDES`
   para las ~170 palabras/frases que no son entradas de diccionario (botones
   de UI, frases de banner). Chequeos corridos: consistencia interna de
   `VOCAB` (mismo hanzi, misma pinyin en todas las secciones donde aparece),
   `VOCAB` vs `TONE_GAME_DATA` para el mismo hanzi, `VOCAB`/`TONE_GAME_DATA`
   vs CC-CEDICT y vs reconstruccion por caracter, distractores de
   `TONE_GAME_DATA` (sin duplicados, ninguno igual a la respuesta correcta),
   que todo termino de `TONE_GAME_DATA` provenga de un termino real de
   `VOCAB` (nada inventado), pinyin+significado de `WORD_GROUPS` contra
   CC-CEDICT, y las 456 entradas de `CHAR_DICT` contra CC-CEDICT.
   **Resultado de la primera pasada**: un solo error encontrado —
   `VOCAB` tenia `"香港行貨": "Xiānggǎng xínghuò"` (leyendo 行 como xíng =
   "caminar"), pero `TONE_GAME_DATA` y `WORD_GROUPS` ya tenian la lectura
   correcta `háng huò` (行貨 = "mercancia autorizada", confirmado en
   CC-CEDICT) desde el fix del bug #3 — nunca se habia propagado a `VOCAB`.
   Corregido.

   **El usuario reviso el resultado el mismo y encontro un segundo caso del
   mismo patron** que mi primera pasada habia descartado mal: `VOCAB` tenia
   `"直播中": "zhíbò zhōng"` (播 en 4to tono), un typo viejo — el propio bug
   #3 ya documentaba "直播(bō, era typo bò)" corregido en `TONE_GAME_DATA`
   (`"zhí bō zhōng"`) y en el otro termino de `VOCAB` que tambien usa 直播
   (`"美团直播": "Měituán zhíbō"`), pero **nunca se propago a este segundo
   termino con el mismo caracter**. Confirmado contra CC-CEDICT (直播 =
   "zhi2 bo1") y corregido.

   **Segunda pasada, mas estricta** (a pedido del usuario: "revisa todas"):
   en vez de comparar strings completos (que generaba falsos descartes por
   digitos/texto en latin mezclados en el hanzi, como en la primera pasada),
   se validó **caracter por caracter** — para cada hanzi de las 231 palabras
   unicas de `VOCAB` y las 217 de `TONE_GAME_DATA` se busca su silaba
   esperada (`CHAR_OVERRIDES` > `CHAR_DICT`) dentro del pinyin guardado, en
   orden, tomando siempre la coincidencia mas cercana (evita que una silaba
   igual mas adelante en la palabra tape una diferencia real, que es
   exactamente el tipo de bug que causo el falso descarte del caso de 直播
   en la primera pasada). Se corrio tambien sobre los 243 pares de
   `WORD_GROUPS`, se verifico que **todos** los distractores de
   `TONE_GAME_DATA` comparten exactamente las mismas letras y cantidad de
   silabas que la respuesta correcta (solo cambian los tonos, como pide el
   diseño del juego), y se buscaron claves JS duplicadas (que se
   sobrescriben en silencio) en los 4 objetos — 0 encontradas. Resultado:
   **0 problemas restantes** en las 456+256+243+217 entradas. Los casos de
   tono neutro documentados (友/息/了/乐/欢-en-喜欢/分-en-部分, ver bug #3 y
   `CHAR_OVERRIDES` arriba) se re-verificaron contra CC-CEDICT y son
   correctos como estan — no son bugs, son el tono neutro real de esas
   palabras.

   **Leccion para el futuro**: cuando se corrige el tono de un caracter en
   una palabra, buscar TODAS las apariciones de ese caracter en `VOCAB`,
   `WORD_GROUPS` y `TONE_GAME_DATA` (no solo donde se detecto el error) —
   los dos bugs de esta auditoria fueron exactamente eso: un fix aplicado en
   un lugar que no se propago al resto.

   El script quedo en `tools/audit/audit_vocab.py` (necesita
   `pip install pycccedict`) — correrlo (`python3 tools/audit/audit_vocab.py`)
   despues de cualquier cambio a pinyin/tonos en `src/app.js`, antes de
   distribuir una nueva version.

## Limitaciones conocidas (no resueltas, decisión consciente)

- **Audio**: depende 100% de la voz del sistema operativo del usuario vía Web
  Speech API. No hay audio pregrabado embebido. Se intentó gTTS/edge-tts y los
  endpoints estaban bloqueados en el entorno sandbox que construyó esto — si
  Code SÍ tiene acceso a internet más amplio, esto sería la mejora #1 a evaluar
  (generar audio real por palabra y embeberlo, o servirlo aparte).
- El archivo sigue siendo ~2.4MB de un solo golpe — no hay lazy-loading de
  imágenes ni de datos.
- No hay tests automatizados formales (se validó todo con jsdom + pruebas ad
  hoc de Node durante el desarrollo, pero no quedó un test suite persistente).

## Sugerencia para el repo en Code (no ejecutado aún, es una propuesta)

Dado que todo el trabajo pesado (verificación de datos, recorte de iconos,
generación de preguntas de tonos) ya está hecho y exportado en `data/` y
`assets/`, un primer paso razonable en Code sería:

1. ~~`git init`, commit inicial con este export tal cual~~ — hecho.
2. ~~Separar el HTML monolítico en `src/index.html` + `src/style.css` +
   `src/app.js`, y un script de build~~ — hecho (`build.js`, ver "Estado
   actual" arriba). Los JSON de `data/` y las imágenes de `assets/`
   mencionados en la estructura original de este export nunca llegaron a
   subirse al repo — de encontrarse, tendría sentido que `build.js` también
   los inyecte en vez de mantenerlos embebidos a mano dentro de
   `app.js`/`index.html`.
3. A partir de ahí, cualquier cambio futuro (nuevo juego, nueva app, fix de
   dato) se hace en los archivos fuente (`src/`) + se corre `node build.js`,
   no con parches de texto sobre un HTML gigante.

## Preferencias del usuario a mantener

- Español para la conversación; contenido de la guía en español con inglés
  para las traducciones (pedido explícito).
- Pinyin siempre junto a cualquier palabra/frase en chino.
- **Nunca asumir/inventar** — cualquier dato nuevo debe venir de una fuente
  verificable (captura de pantalla real, o herramienta de diccionario), y
  decirlo explícitamente si algo no se pudo verificar.
- El usuario es exigente con la exactitud porque **da clases con esto** — los
  errores de tono no son cosméticos, son pedagógicamente serios.
