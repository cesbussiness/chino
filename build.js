#!/usr/bin/env node
// Genera un HTML unico y autocontenido a partir de src/index.html + los <link
// rel="stylesheet"> y <script src="..."> locales que referencia, para poder
// abrirlo con doble clic o mandarlo sin depender de varios archivos juntos.
//
// `node build.js --protect` genera ademas una copia "para entregar" con
// app.js ofuscado (ver README/PROJECT_CONTEXT: no es cifrado real -- un
// HTML que corre standalone en el navegador no se puede cifrar de verdad,
// el navegador tiene que poder leerlo -- pero dificulta que alguien copie o
// reutilice la logica como si fuera propia). Requiere `npm install`
// (javascript-obfuscator, solo como devDependency de build, nunca se
// entrega ni queda en el HTML final).
const fs = require('fs');
const path = require('path');

const PROTECT = process.argv.includes('--protect');

const SRC_DIR = path.join(__dirname, 'src');
const OUT_DIR = path.join(__dirname, 'dist');
const OUT_FILE = path.join(OUT_DIR, PROTECT
  ? 'Guia_Meituan_Chino_Interactiva.protegido.html'
  : 'Guia_Meituan_Chino_Interactiva.html');

let html = fs.readFileSync(path.join(SRC_DIR, 'index.html'), 'utf8');

// Inline every local stylesheet link.
html = html.replace(/<link rel="stylesheet" href="([^"]+)">/g, (tag, file) => {
  const css = fs.readFileSync(path.join(SRC_DIR, file), 'utf8');
  return `<style>\n${css}</style>`;
});

// Inline every local script tag, in document order. Solo app.js (la logica
// propia) se ofusca con --protect: hanzi-writer.min.js es una libreria de
// terceros ya minificada (MIT, ver ARPHICPL.TXT/licencia del proyecto
// vendorizado) y hanzi-data.js es puro dato (pinyin/significados/trazos)
// que de todas formas se muestra tal cual en pantalla, asi que ofuscarlos
// no protege nada y solo agregaria riesgo de romper algo.
html = html.replace(/<script src="([^"]+)"><\/script>/g, (tag, file) => {
  let js = fs.readFileSync(path.join(SRC_DIR, file), 'utf8');
  if(PROTECT && file === 'app.js'){
    const JavaScriptObfuscator = require('javascript-obfuscator');
    js = JavaScriptObfuscator.obfuscate(js, {
      compact: true,
      controlFlowFlattening: true,
      controlFlowFlatteningThreshold: 0.75,
      deadCodeInjection: true,
      deadCodeInjectionThreshold: 0.3,
      stringArray: true,
      stringArrayEncoding: ['base64'],
      stringArrayThreshold: 0.75,
      identifierNamesGenerator: 'hexadecimal',
      renameGlobals: false,
      // selfDefending/debugProtection quedan apagados a proposito: son
      // fragiles cuando el codigo despues se re-empaqueta o corre en
      // entornos/navegadores variados (justo el caso de este archivo,
      // pensado para abrirse en cualquier equipo/navegador) y podrian
      // romper la app entera con un error dificil de diagnosticar -- no
      // vale la pena el riesgo por una capa extra de ofuscacion.
      selfDefending: false,
      debugProtection: false,
    }).getObfuscatedCode();
  }
  return `<script>\n${js}</script>`;
});

fs.mkdirSync(OUT_DIR, { recursive: true });
fs.writeFileSync(OUT_FILE, html, 'utf8');

const sizeMB = (Buffer.byteLength(html, 'utf8') / (1024 * 1024)).toFixed(2);
console.log(`Build OK -> ${path.relative(__dirname, OUT_FILE)} (${sizeMB} MB)${PROTECT ? ' [protegido/ofuscado]' : ''}`);
