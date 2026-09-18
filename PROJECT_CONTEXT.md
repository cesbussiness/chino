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
  monolítico original antes de borrarlo — reconstruir las 3 piezas daba
  exactamente el archivo viejo). `index.html` sigue teniendo las imágenes e
  iconos embebidos como `data:` URIs directo en el HTML (por el bug de iOS
  Quick Look, ver más abajo). También vive ahi `src/hanzi-writer.min.js`
  (libreria vendorizada) + `src/hanzi-data.js` (datos de trazos +
  `CHAR_RADICALS`, descomposicion en radicales/componentes), para Practicar
  escritura — ver "Qué hace la guía" arriba. Todo junto, el HTML final pesa
  ~3.6 MB.
- **Build script**: `node build.js` (sin dependencias, Node nativo) lee
  `src/index.html` e inyecta inline cualquier `<link rel="stylesheet">` y
  `<script src>` local que encuentre (hoy: `style.css`, `hanzi-writer.min.js`,
  `hanzi-data.js`, `app.js`, en ese orden), generando
  `dist/Guia_Meituan_Chino_Interactiva.html` — el único archivo autocontenido
  para abrir con doble clic o mandar por WhatsApp/mail. `dist/` está en
  `.gitignore` (es artefacto generado) — correr el build después de
  cualquier cambio en `src/` antes de distribuir.
  - **`node build.js --protect`** genera ademas
    `dist/Guia_Meituan_Chino_Interactiva.protegido.html`: identico, pero con
    `app.js` (solo la logica propia, no `hanzi-writer.min.js` ni
    `hanzi-data.js`) pasado por `javascript-obfuscator` — a pedido del
    usuario, para dificultar que alguien copie/reutilice el codigo como
    propio al entregar el archivo. Requiere `npm install` una vez
    (`javascript-obfuscator` queda como devDependency en `package.json`,
    nunca se entrega ni queda en el HTML final — es solo una herramienta de
    build). **Importante, aclarado explicitamente al usuario**: esto NO es
    cifrado real ni evita que alguien use el archivo sin pagar — un HTML que
    tiene que correr solo/offline en el navegador no se puede cifrar de
    verdad (el navegador necesita poder leerlo para ejecutarlo). Ofuscar
    solo hace el codigo dificil de leer/copiar con las herramientas de
    desarrollador; la app funciona exactamente igual para quien la abra. Se
    valido con Playwright que el build ofuscado se comporta identico al
    normal (los 7 modos de practica, busqueda del glosario, grabar voz) sin
    errores de consola. `selfDefending`/`debugProtection` del ofuscador se
    dejaron apagados a proposito por ser fragiles en distintos
    navegadores/entornos — no vale la pena el riesgo de romper la app por
    una capa extra de proteccion.
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

**Práctica** tiene 7 modos, todos comparten nivel/sección + filtro de escritura:
1. **📇 Tarjetas de repaso** — flashcard clásica, se voltea para ver pinyin+inglés
   + desglose de caracteres. Recall activo tipo Anki: 🔴 **Repasar** manda la
   tarjeta al final de la cola de la ronda actual (y a la cola global de
   falladas); 🟢 **Avanzar** la saca de la ronda (y la saca de falladas si
   estaba ahi). Sigue hasta vaciar la cola — "0 de N dominadas" en el pie —
   y ahi muestra un resumen con "🔁 Repasar de nuevo". Sin boton "siguiente"
   pasivo: a pedido del usuario, la logica es autoevaluarse hasta dominar
   todas las tarjetas del filtro activo, no simplemente hojearlas.
   **Tarjeta grande por palabra/caracter (a pedido del usuario)**: cada chip
   del desglose de caracteres (`renderCharBreakdown`, tanto en Tarjetas como
   en el feedback de Adivina) es clickeable — abre un modal (`#wordDetailModal`)
   con los mismos campos que la tarjeta de repaso (hanzi grande, pinyin,
   ingles, boton de escuchar) para esa palabra/caracter suelto, mas su propio
   detalle: si es un caracter individual, su desglose de radical/componentes
   (`CHAR_RADICALS`, reutilizando `renderRadicalBreakdown` — la misma funcion
   que ya usaba Practicar escritura, extraida para no duplicarla); si es una
   combinacion de `WORD_GROUPS` (2+ caracteres), su propio desglose recursivo
   (los chips de ADENTRO del modal tambien son clickeables, permite "bajar"
   un nivel mas). Siempre muestra "Aparece en: <palabra que lo mostro>" como
   contexto/ejemplo de uso real (no se inventa ninguna oracion de ejemplo —
   el contexto es la palabra real de donde salio el chip). Es **puramente
   informativo**: no cuenta como "la sabia"/"no la sabia", no toca
   `fcQueue` ni `missedIndices` ni ningun puntaje — se cierra (X o tocando
   afuera) y se sigue exactamente donde se estaba en la tarjeta original.
   Los clicks se escuchan en fase de **captura** en `document` para poder
   frenar la propagacion antes de que llegue al listener de "voltear" de
   `#flashcard` (los chips viven dentro de la cara de atras de la tarjeta,
   que es un hijo de `#flashcard`).
   **"🎙️ Grabar mi voz" (a pedido del usuario)**: junto a cada boton
   "🔊 Escuchar" de TODA la guia — las 6 secciones activas de practica
   (Tarjetas, Adivina, Tonos, Practicar escritura, Examen, la tarjeta
   grande de palabra/caracter) **y tambien** cada tarjeta de vocabulario de
   Pantalla Principal/外卖/京东/En comun y cada fila del Glosario completo
   (a pedido explicito del usuario, que en un principio se habian dejado
   afuera) — hay un boton para grabar tu propia pronunciacion con el
   microfono (`MediaRecorder`, 100% local — nunca se sube a ningun lado ni
   se guarda en disco) y reproducirla para compararla con la voz del
   sistema. Elige el primer `mimeType` soportado entre `audio/mp4`,
   `audio/webm;codecs=opus`, `audio/webm` y `audio/ogg` via
   `MediaRecorder.isTypeSupported` (Safari solo soporta mp4, Chrome/Edge
   soportan webm — de ahi la lista de candidatos en ese orden). Si el
   navegador no tiene `getUserMedia`/`MediaRecorder`, o el usuario niega el
   permiso del microfono, se muestra un aviso (`showMicToast`, mismo
   componente visual que el aviso de voz no disponible, bajo la clase
   compartida `.info-toast` en vez de un id fijo) explicando por que y que
   el resto de la guia sigue funcionando igual.
   Con potencialmente cientos de estos botones en la pagina (uno por cada
   una de las 256 palabras del Glosario + otro tanto en las tarjetas de
   vocabulario), el mecanismo es **completamente delegado** en vez de
   inicializar una instancia por boton: un solo listener de `click` en
   `document` para `.record-btn`, que lee/crea el estado
   (mediaRecorder/blob url) directo en el elemento `.recorder` mas
   cercano (`el._recState`) — así cientos de tarjetas no cuestan cientos de
   listeners individuales. Solo puede haber **una grabacion activa/guardada
   a la vez en toda la pagina**: empezar una nueva (`startRecorderRecording`)
   descarta automaticamente cualquier otra que estuviera grabada o
   grabandose (`activeRecorderEl`), para no dejar recordings "olvidadas" en
   tarjetas que ya no se estan mirando.
   **El microfono en si (`sharedMicStream`) es UN SOLO stream compartido por
   toda la pagina**, pedido una sola vez (perezosamente, al primer click en
   cualquier "Grabar mi voz") y reutilizado por todas las tarjetas durante
   el resto de la sesion — ver bug #12 mas abajo, este diseño es la
   correccion a un problema real que reporto el usuario (Chrome volvia a
   pedir permiso de microfono en cada grabacion). El stream NO se cierra al
   resetear una tarjeta ni al re-renderizar el Glosario; solo se cierra solo
   si el usuario revoca el permiso o el hardware se desconecta a mitad de
   sesion (evento `ended` del track), y se vuelve a pedir automaticamente la
   proxima vez que haga falta.
   **La grabacion (el audio ya grabado, no el permiso del microfono) se
   pierde siempre** (`resetRecorder(el)`) al: cambiar de tarjeta/pregunta en
   cualquier modo de practica (`nextCard`, `showGameQuestion`,
   `showTonesQuestion`, `showWriteAtPosition`, `showExamMc`/`showExamTone`),
   cerrar la tarjeta grande de palabra/caracter (X o tocando afuera), o —
   caso nuevo al agregarlo al Glosario — cada vez que se re-renderiza la
   lista completa (cada tecla en el buscador del Glosario llama
   `renderGlossary()`, que reemplaza el `innerHTML` entero): antes de pisar
   el HTML viejo se llama `resetAllRecordersIn(glossaryList)`, que recorre
   las filas viejas y corta cualquier grabacion en curso en ellas (no el
   microfono compartido, que sigue vivo para las filas nuevas).
2. **🎮 Juego: Adivina** — 4 opciones de traducción al inglés, con puntaje/racha.
3. **🔗 Emparejar: Significado** — memorama hanzi↔inglés (antes se llamaba
   solo "Juego: Emparejar"; se renombró al agregar la variante de pinyin
   para que ambas queden claras en la barra de modos).
4. **🔗 Emparejar: Pinyin** — mismo memorama, pero hanzi↔pinyin (a pedido
   del usuario) en vez de hanzi↔inglés — util para practicar lectura de
   pinyin con tonos en vez de vocabulario. Comparte motor con el anterior
   via `createMatchGame(opts)` (parametrizado por que campo del termino usa
   la ficha "otra": `t.e` o `t.p`) en vez de duplicar la logica del juego.
   Ambos memoramas recorren **todo** el filtro activo en tandas de 6 (no
   solo 6 al azar y listo) — "Tanda X de Y" en las stats, boton "Siguiente
   tanda" al completar una, hasta cubrir las N palabras del filtro. Si la
   ultima tanda queda con menos de 6 palabras nuevas, se completa hasta 6
   con palabras de la cola de falladas de esa sesion y, si todavia falta,
   con palabras ya cubiertas en tandas anteriores — asi nunca termina en
   una ronda rara de 1-2 fichas. El resumen final usa el tamaño real del
   filtro (ej. "14/14"), no la cantidad de fichas mostradas con relleno.
5. **🎵 Juego: Tonos** — 6 opciones de pinyin con las mismas letras, solo cambian
   los tonos (para practicar oído tonal).
6. **✍️ Practicar escritura** — orden de trazos real por carácter (via
   [Hanzi Writer](https://chanind.github.io/hanzi-writer), vendorizado offline
   en `src/hanzi-writer.min.js` + `src/hanzi-data.js`). Arma una ronda de 12
   palabras del filtro activo y las aplana en una secuencia unica de
   caracteres (`writeSequence`); navegacion 100% manual con "◀ Atras" /
   "Adelante ▶" debajo del dibujo (nada de auto-avance al completar un
   caracter — el usuario decide cuando pasar al siguiente, incluso cruzando
   de una palabra a otra). "💡 Ver como se escribe" reproduce la animacion de
   trazos y vuelve al quiz; "↺ Repetir" reinicia el caracter actual. Al salir
   de una palabra hacia adelante se decide si va a la cola de "falladas"
   segun si tuvo algun error mientras se practicaba. Cubre 455 de los 456
   caracteres de `CHAR_DICT` (falta 咁, prestamo
   cantones sin caracter Han estandar — se salta esa palabra si no queda
   ningun otro caracter practicable). Datos: proyecto Make Me a Hanzi via
   `hanzi-writer-data`, licencia Arphic Public License (ver `ARPHICPL.TXT`
   en ese repo) — libre para redistribuir/modificar reteniendo la licencia.
   Junto a cada caracter se muestra su propio pinyin+significado (de
   `CHAR_DICT`) y, cuando hay dato, su descomposicion en radical+componentes
   (`CHAR_RADICALS` en `hanzi-data.js`, 446/456 caracteres — a pedido del
   usuario, que mostro una app de referencia con ese formato). Se construyo
   parseando el campo `decomposition` (IDS) + `radical` del diccionario
   completo de Make Me a Hanzi (`dictionary.txt`, mismo proyecto/licencia);
   el pinyin/significado de cada componente sale primero de `CHAR_DICT` (si
   ese componente ya es una de nuestras 456 palabras, para consistencia),
   despues de CC-CEDICT (prefiriendo la lectura comun sobre apellidos —
   ej. 戈 → "dagger-axe" no "surname Ge" — y con fallback al glosario de
   Make Me a Hanzi cuando CC-CEDICT solo tiene una entrada de apellido, ej.
   娄), y por ultimo el glosario de Make Me a Hanzi para radicales puros que
   no son palabras (纟, 亻, 氵...). El script quedo en
   `tools/audit/build_char_radicals.py` (mismo requisito que el audit de
   tonos: `pip install pycccedict`) — baja y cachea solo
   `dictionary.txt` de Make Me a Hanzi (no versionado, ~2.5MB) la primera
   vez que se corre, e imprime el `CHAR_RADICALS` actualizado por stdout
   para pegar en `src/hanzi-data.js` si hace falta regenerarlo.
   **Layout**: en mobile todo apilado (igual que el resto de la practica);
   en desktop (`min-width:901px`) la info (palabra + caracter + radicales)
   va en una columna a la izquierda del recuadro de escritura en vez de
   arriba — a pedido del usuario, para que la vista completa entre sin
   scroll (`.write-practice-area` con `flex-direction:row` en desktop,
   ver bug/mejora de layout de Adivina/Tonos mas arriba, mismo criterio
   general de "evitar scroll en las vistas de pc").
7. **📝 Examen** — a pedido del usuario ("una especie de examen ... que no
   permita avanzar hacia atras sino solamente hacia adelante y al final me
   deje una puntuacion"): combina en una sola secuencia, para el filtro
   activo (nivel/sección + "solo simplificado"), 4 tipos de pregunta en
   orden fijo — autoevaluación con tarjetas, selección múltiple de
   significado, una ronda de emparejar (en tandas de 6, igual que el modo
   Emparejar) y selección múltiple de tono (solo para las palabras que
   tienen `TONE_GAME_DATA`). Recorre **toda** la sección elegida (no una
   muestra al azar como Adivina/Tonos), salvo que el filtro combinado
   supere 24 palabras (ej. "🔀 Todo mezclado"), en cuyo caso se toma una
   muestra de 24 al azar para que un examen no se vuelva interminable.
   **100% hacia adelante**: no hay ningún botón "Atrás" en ningún punto del
   examen — la tarjeta se autocalifica con "✅ La sabía"/"❌ No la sabía"
   (ambos avanzan), y cada pregunta de opción múltiple/emparejar se bloquea
   apenas se responde. Al terminar, un resumen muestra el % total y el
   desglose de aciertos por tipo de pregunta (tarjetas/significado/
   emparejar/tonos, cada fila solo si esa sección tuvo preguntas), con
   "🔁 Repetir examen" para una ronda nueva. No usa la cola global de
   "Repasar falladas" (es una evaluación puntual, no una práctica
   recurrente) y reutiliza los constructores de opciones ya existentes
   (`buildMeaningOptions`/`buildToneOptions`, extraídos de Adivina/Tonos a
   funciones compartidas para no duplicar la lógica de distractores).
   **Layout**: en desktop, la pregunta de opción múltiple usa el mismo
   patrón de 2 columnas (palabra a la izquierda, opciones a la derecha)
   que Adivina/Tonos, mismo criterio de "evitar scroll en las vistas de pc".
9. **"Repetir" rompia el dibujo tras completar una palabra**: el diseño
   original tenia, por palabra, un indice `writeCharIndex` + auto-avance al
   completar cada caracter (`setTimeout`) y un boton "Siguiente palabra" que
   aparecia recien al terminar todos los caracteres. Una vez ahi,
   `writeCharIndex` quedaba apuntando **fuera** de la lista de caracteres de
   esa palabra (ya se habian recorrido todos) pero "Repetir"/"Ver como se
   escribe" seguian visibles y clickeables — al tocarlos se llamaba
   `HanziWriter.create(..., undefined, ...)`, lo que limpiaba el lienzo
   (`innerHTML=''`) y fallaba, dejando el recuadro en blanco (bug reportado
   por el usuario). Se rediseño la navegacion entera: en vez de indices
   por-palabra + auto-avance, toda la ronda se aplana a una sola secuencia
   de caracteres (`writeSequence`) recorrida con "Atras"/"Adelante"
   manuales — no existe mas un estado "completo pero fuera de rango", asi
   que la clase entera de bug desaparece (`writeSeqPos` siempre apunta a un
   caracter valido). De paso, a pedido del usuario: el audio ahora esta
   entre "Atras" y "Adelante" debajo del dibujo, y los textos de pinyin/
   significado/radicales del panel izquierdo se agrandaron notablemente
   (antes eran chicos y dificiles de leer).
10. **Investigado, no era bug**: el usuario reporto una ronda de Emparejar
    con "Errores: 2" pero solo 1 palabra quedo en "Repasar falladas" al
    terminar. Revisando `createMatchGame`: cuando una ronda termina
    (`correctCount === pairs.length`), TODAS las palabras de esa ronda
    pasaron por un match correcto en algun momento (si no, la ronda no
    podria haber terminado), y cada match correcto llama `removeMissed`
    sobre esa palabra — asi que al terminar una ronda completa, el aporte
    neto a `missedIndices` de esa ronda especifica siempre deberia ser 0,
    sin importar cuantos intentos fallidos hubo en el camino. Confirmado
    con Playwright (2 errores deliberados, ronda completa, `missedIndices`
    termina en 0). El "1" que vio el usuario casi seguro era un resto de
    antes de que existiera el reset-al-cambiar-de-juego (bug/mejora #8) —
    estaba probando un archivo descargado viejo (de antes del reset de
    "Repasar falladas" al cambiar de juego, ver "Filtros globales" mas
    abajo) — patron que se repitio varias veces en esta sesion.

Filtros globales, aplican a los 7 modos por igual: nivel (① comunes / ②
pantallas principales / ③ submenús / 🔀 todo), sección específica (dropdown
con las 23 secciones reales — si se elige una, anula el nivel; elegir un
nivel la resetea a "todas"), **"Solo chino simplificado"** (excluye 36
términos tradicionales que vienen del canal HK超市 de JD, marcados con badge
繁), y **"📌 Repasar falladas"** (cola de palabras falladas, se vacía cuando
las aciertas — y tambien se reinicia por completo cada vez que se cambia
de modo/juego en `#modeSwitch`, a pedido del usuario: es una cuenta por
sesión de juego, no algo que se arrastre de Adivina a Tarjetas, etc.). El
modo Examen respeta nivel/sección/"solo simplificado" igual que los demás,
pero no lee ni escribe la cola de "Repasar falladas" — su propio puntaje
final cumple ese rol para esa sección en particular.

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
8. **`speak(null)` tiraba excepcion**: los botones "🔁 Jugar de nuevo" (match/
   adivina/tonos, y ahora escritura) reusan la clase `.speak-btn` solo por el
   estilo (pildora gris), pero no tienen `data-hz` — el listener global
   delegado en `document` (`.speak-btn` click → `speak(btn.dataset.hz)`) los
   agarra igual y crasheaba en `text.replace(...)` con `text === null`. No
   rompia el reinicio de la ronda (son listeners independientes) pero tiraba
   un error en consola en cada "Jugar de nuevo". Encontrado al probar el
   replay de Practicar escritura. Fix: `speak()` ahora hace `if(!text) return;`
   al inicio.
9. **Resumen del Examen: el botón "Repetir examen" quedaba en la misma línea
   que la última fila del desglose de puntaje** (en vez de debajo, separado),
   en desktop y mobile por igual. Causa: `.exam-score-breakdown` era
   `display:inline-block` para poder centrarse con `margin:auto` dentro del
   `.game-summary` (que tiene `text-align:center`), pero eso también hace que
   el botón siguiente (otro elemento en flujo inline) se acomode a su lado en
   vez de bajar de línea — a diferencia de los demás resúmenes (Adivina,
   Tonos, Emparejar, Escritura), donde el elemento anterior al botón de
   replay es un `<p>` (bloque, fuerza el salto de línea). Encontrado con
   Playwright al probar el examen completo antes de darlo por terminado. Fix:
   `.exam-score-breakdown` pasó a `display:block; width:fit-content; margin:12px
   auto 0;` — sigue centrado pero como bloque, así el botón cae debajo.
10. **CRÍTICO — el audio no sonaba en iPhone/iPad (reportado por el usuario:
    "en el Apple no funcionan los botones audios ni comandos")**. Causa raíz:
    `speak()` llamaba `speechSynthesis.cancel()` y despues, dentro de un
    `setTimeout(..., 60)`, `speechSynthesis.speak()` (ese delay se agregó en
    el bug #2 para esquivar una condición de carrera de Chrome/Edge). iOS
    Safari exige que `speechSynthesis.speak()` se llame de forma **sincrónica**,
    dentro del mismo tick del evento de click/touch iniciado por el usuario —
    cualquier `setTimeout`/`Promise` de por medio hace que iOS pierda el
    "user activation" y descarte la llamada **en silencio** (sin
    `onerror`, sin excepción, sin nada) — coincide exacto con "no funciona,
    sin ningun aviso". No se pudo probar en un iPhone/Safari real en este
    entorno (herramientas de dev remoto solo tienen Chromium instalado), asi
    que el fix se basa en el comportamiento documentado de iOS Safari, no en
    una prueba en dispositivo — recomendado que el usuario confirme en un
    iPhone real. Fix: se saco el `setTimeout` por completo. Ahora solo se
    llama `cancel()` si `speechSynthesis.speaking||.pending` es verdadero (el
    caso comun — nada sonando — ni siquiera llama a `cancel()`), y `speak()`
    se llama siempre en el mismo tick sincronico que disparo el boton.
    Verificado con Playwright que `speechSynthesis.speak()` ahora se invoca
    sincronicamente (ver commit de esta auditoria).
11. **iOS Safari: los `<select>`/`<input>` con letra chica hacian zoom
    automatico de toda la pagina al tocarlos** (`#sectionSelect`,
    `#voiceSelect`, `#searchInput` — `font-size` entre .75rem y .9rem, todos
    por debajo de 16px). Es un comportamiento estandar de iOS Safari: si un
    campo enfocable tiene `font-size < 16px`, Safari asume que el usuario
    necesita zoom para leerlo y lo aplica solo, lo que se siente como que "el
    control no responde" (la pagina salta/hace zoom en vez de abrir el
    dropdown con normalidad). Fix: los 3 pasaron a `font-size:16px` fijo (no
    `rem`, para que no dependa de si el elemento raiz cambia de tamaño).
12. **Glosario completo: scroll horizontal fijo (~777px de ancho minimo) en
    CUALQUIER pantalla angosta** (320/375/414/768px probados, todos con el
    mismo overflow). Causa: `.glossary-row` era una sola fila `flex` con
    columnas de ancho fijo (`.hz` 120px, `.py` 150px) mas un `.tag` con
    `white-space:nowrap` que en varias secciones es un titulo largo (ej.
    "Pagina 1 del menu de iconos (首页)", "Barra de navegacion inferior
    (global)") — esos anchos fijos sumados nunca entraban en un telefono,
    sin importar cuan angosto fuera el viewport. Encontrado con una
    auditoria automatizada de Playwright que mide `scrollWidth` vs
    `clientWidth` en 7 anchos (320 a 1440px) x las 7 pestañas x los 7 modos
    de Practica. Fix: en <901px cada fila pasa a un grid de 3 lineas (icono+
    hanzi+audio arriba, seccion+pinyin en medio, significado en ingles
    abajo, todo el texto envolviendo libremente); desde 901px vuelve a la
    fila compacta original de una sola linea (via `display:contents` en un
    `<span class="glossary-meta">` que agrupa tag+pinyin, para que puedan
    volver a ser columnas independientes en el layout de escritorio).
13. **Practica (tarjetas): ~3-4px de scroll horizontal en pantallas de
    320px de ancho** (iPhone SE 1a gen y similares angostos). Los 3 botones
    de `.practice-controls` ("🔴 Repasar" / "🔊 Escuchar" / "Avanzar ▶") con
    su padding no entraban en una sola linea en el viewport mas angosto
    probado. Encontrado en la misma auditoria automatizada que el bug #12.
    Fix: `.practice-controls` ahora tiene `flex-wrap:wrap` (red de
    seguridad — desde ~340px de ancho los 3 botones entran igual en una
    linea, asi que no cambia nada visualmente ahi).
14. **"Grabar mi voz" volvia a pedir permiso de microfono en CADA grabacion**
    (reportado por el usuario: "cada vez que quiero grabar se me abre una
    ventana de permisos... igual me vuelve a salir la proxima vez"). Causa:
    cada tarjeta pedia su propio `getUserMedia()` al empezar a grabar y
    cerraba ese stream (`track.stop()`) al resetear (cambiar de
    tarjeta/pregunta) — asi que la SIGUIENTE grabacion, aunque fuera unos
    segundos despues en la misma pestaña, era una peticion de permiso
    nueva. Chrome no siempre recuerda el "permitir mientras se visita el
    sitio" entre peticiones sueltas de `getUserMedia()` sobre `file://`
    (un archivo local no tiene el mismo origen estable/persistente que un
    sitio `https://`), asi que terminaba re-preguntando en cada tarjeta.
    Fix: un solo `sharedMicStream` pedido UNA vez (perezosamente, en el
    primer click de "Grabar mi voz" de toda la sesion) y reutilizado por
    todas las tarjetas de ahi en adelante — resetear una tarjeta ya NO
    cierra el microfono, solo descarta el audio grabado en esa tarjeta.
    Verificado con Playwright (instrumentando `getUserMedia` para contar
    llamadas): 3 grabaciones en 3 tarjetas/modos distintos → 1 sola llamada
    a `getUserMedia`. **Limite real que este cambio NO puede arreglar**: si
    a pesar de esto el navegador sigue pidiendo permiso cada vez que se
    **recarga la pagina o se reabre el archivo**, es una restriccion de
    Chrome para `file://` que ninguna pagina puede forzar a cambiar desde
    JavaScript — el permiso vuelve a pedirse una vez por cada carga de
    pagina nueva (no por cada grabacion dentro de la misma carga, que es lo
    que este fix soluciona). Si el usuario prueba con un archivo descargado
    de nuevo cada vez con un nombre distinto (`Guia...(1).html`,
    `Guia...(2).html`, patron ya visto varias veces en esta sesion), Chrome
    puede tratar cada archivo como un origen distinto y pedir permiso de
    nuevo aunque sea "la misma" guia — guardar el archivo siempre con el
    mismo nombre/ubicacion deberia ayudar a que el permiso persista entre
    sesiones tambien.

## Auditoria QA/responsive + compatibilidad iOS (esta sesion)

A pedido del usuario ("prueba de qa y auditoria grafica... 100% responsiva
offline... funcione en Android y Apple"), se corrio una auditoria
automatizada con Playwright (Chromium headless, no hay WebKit real
instalado en este entorno — ver limitacion mas abajo) que:

- Midio `document.documentElement.scrollWidth` vs `clientWidth` en 7 anchos
  de viewport (320, 375, 414, 768, 900, 1024, 1440px) x las 7 pestañas x los
  7 modos de Practica (49 combinaciones x 7 anchos = 343 checks) buscando
  scroll horizontal — encontro y corrigio los bugs #12 y #13 de arriba.
  Resultado final: **cero overflow horizontal en cualquier combinacion**.
- Reviso visualmente (capturas de pantalla) cada pestaña y cada modo en
  mobile/tablet/desktop para consistencia grafica (mismos colores, radios de
  borde, tipografia, espaciado) — no aparecieron mas inconsistencias
  ademas de las corregidas arriba.
- Reviso el codigo fuente buscando patrones especificos que rompen en iOS
  Safari (no solo "se ve distinto" sino "no funciona"): uso de
  `speechSynthesis` fuera del tick sincronico del click (bug #10 arriba),
  `font-size` chico en campos enfocables (bug #11), sintaxis JS moderna que
  Safari viejo no soporte (no se encontro ninguna — no hay `?.`, `??`,
  `.at()`, `structuredClone`, etc.), y soporte de eventos touch en la
  libreria de escritura vendorizada (`hanzi-writer.min.js` ya maneja
  `touchstart`/`touchmove`/`touchend` nativamente, sin cambios necesarios).
- Se agrego un bloque `<noscript>` al principio del `<body>` con un aviso
  grande explicando el escenario de "Vista rapida" de iOS (ver seccion de
  abajo) — antes esa explicacion solo vivia en la pestaña Introduccion, que
  en teoria ya es visible sin JS (tiene `class="panel active"` fijo en el
  HTML) pero el `<noscript>` la hace imposible de pasar por alto apenas se
  abre el archivo.

**Orden ratificado de los controles en la vista movil de Practica** (de
arriba a abajo, el mismo para los 7 modos): (1) caja colapsable "como
funciona" (`<details>`, cerrada por defecto para no ocupar espacio), (2)
sección específica (dropdown, filtro mas especifico), (3) nivel (chips con
scroll horizontal propio), (4) modo/juego (chips con scroll horizontal
propio), (5) "Solo chino simplificado" (checkbox), (6) "📌 Repasar
falladas" (solo visible si hay algo que repasar), (7) el contenido del modo
activo. Logica: de lo mas general (que seccion/nivel) a lo mas especifico
(que actividad), despues un filtro de alcance adicional, y al final el
contenido — se mantuvo asi porque ya funcionaba bien de sesiones
anteriores, no hizo falta reordenar nada, solo se ratifica por escrito aca
para que futuros cambios no lo rompan sin querer.

**Limitacion de esta auditoria**: el entorno de desarrollo remoto solo
tiene el motor Chromium instalado para pruebas automatizadas (no hay Safari
ni WebKit real disponibles aca), asi que los bugs de iOS (#10 y #11) se
diagnosticaron y corrigieron en base al comportamiento **documentado y bien
conocido** de iOS Safari (no en base a una reproduccion en un iPhone real
desde esta sesion). Se recomienda que el usuario (o alguien con un iPhone a
mano) confirme que el audio y los selectores ya funcionan bien en un
dispositivo real despues de este cambio, y que avise si algo especifico de
iOS sigue fallando — con mas detalle (que exactamente no responde, en que
pantalla, si el archivo se abrio directo en Safari o via Compartir/Airdrop)
se puede diagnosticar mas preciso.

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
- **"Grabar mi voz" no se pudo probar en un iPhone/Safari real** (mismo motivo
  que los bugs de iOS de mas arriba: este entorno solo tiene Chromium). Se
  verifico con Chromium + flags de dispositivo de audio falso que
  `getUserMedia`/`MediaRecorder` funcionan sobre `file://` (se reporta como
  contexto seguro) y que el fallback de "no se pudo grabar" se dispara bien
  si el permiso se niega. Lo que NO se pudo confirmar en un dispositivo real:
  si Safari en iOS pide permiso de microfono normalmente para un archivo
  local, y si el codec `audio/mp4` que elige `MediaRecorder` ahi se graba y
  reproduce sin problemas. Recomendado confirmar en un iPhone real.

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
