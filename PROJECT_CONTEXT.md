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

- **Un solo archivo**: `Guia_Meituan_Chino_Interactiva.html`, ~2.4 MB, 100%
  autocontenido (imágenes e iconos en base64, cero dependencias externas, cero
  llamadas de red). Pensado para abrir con doble clic en cualquier navegador,
  Windows/Mac/iOS/Android.
- Todo el desarrollo hasta ahora fue **iterativo por chat**: cada cambio fue un
  parche de texto (Python `str.replace`) directamente sobre el HTML monolítico.
  Esto ya se está poniendo frágil (bugs de cascada CSS por orden de reglas,
  dificultad para revisar diffs, archivo gigante). **Por eso se está moviendo a
  Claude Code + git** — para poder trabajar con archivos separados y ver diffs
  reales.

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
   los tonos (para practicar oído tonal). Organizado por las 23 secciones reales
   (no por los niveles 1/2/3).

Filtros globales: nivel (① comunes / ② pantallas principales / ③ submenús / 🔀
todo), sección específica (solo en Tonos), **"Solo chino simplificado"**
(excluye 36 términos tradicionales que vienen del canal HK超市 de JD, marcados
con badge 繁), y **"📌 Repasar falladas"** (cola de palabras falladas, compartida
entre los 3 juegos, se vacía cuando las aciertas).

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

1. `git init`, commit inicial con este export tal cual (HTML + data + assets +
   este README) para tener un punto de partida versionado.
2. Separar el HTML monolítico en `src/index.html` (esqueleto) + `src/style.css`
   + `src/app.js`, y un script de build simple (`build.py` o `build.js`) que
   inyecte los JSON de `data/` y las imágenes de `assets/` como los `<script>`
   y `<img>` embebidos, generando el HTML final distribuible. Esto haría los
   diffs de git legibles y evitaría el bug de orden-de-cascada de nuevo.
3. A partir de ahí, cualquier cambio futuro (nuevo juego, nueva app, fix de
   dato) se hace en los archivos fuente + se corre el build, no con parches de
   texto sobre un HTML gigante.

## Preferencias del usuario a mantener

- Español para la conversación; contenido de la guía en español con inglés
  para las traducciones (pedido explícito).
- Pinyin siempre junto a cualquier palabra/frase en chino.
- **Nunca asumir/inventar** — cualquier dato nuevo debe venir de una fuente
  verificable (captura de pantalla real, o herramienta de diccionario), y
  decirlo explícitamente si algo no se pudo verificar.
- El usuario es exigente con la exactitud porque **da clases con esto** — los
  errores de tono no son cosméticos, son pedagógicamente serios.
