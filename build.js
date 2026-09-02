#!/usr/bin/env node
// Genera un HTML unico y autocontenido a partir de src/index.html + src/style.css + src/app.js,
// para poder abrirlo con doble clic o mandarlo sin depender de los 3 archivos juntos.
const fs = require('fs');
const path = require('path');

const SRC_DIR = path.join(__dirname, 'src');
const OUT_DIR = path.join(__dirname, 'dist');
const OUT_FILE = path.join(OUT_DIR, 'Guia_Meituan_Chino_Interactiva.html');

const LINK_TAG = '<link rel="stylesheet" href="style.css">';
const SCRIPT_TAG = '<script src="app.js"></script>';

const html = fs.readFileSync(path.join(SRC_DIR, 'index.html'), 'utf8');
const css = fs.readFileSync(path.join(SRC_DIR, 'style.css'), 'utf8');
const js = fs.readFileSync(path.join(SRC_DIR, 'app.js'), 'utf8');

if (!html.includes(LINK_TAG)) {
  throw new Error(`No se encontro "${LINK_TAG}" en src/index.html`);
}
if (!html.includes(SCRIPT_TAG)) {
  throw new Error(`No se encontro "${SCRIPT_TAG}" en src/index.html`);
}

const out = html
  .replace(LINK_TAG, `<style>\n${css}</style>`)
  .replace(SCRIPT_TAG, `<script>\n${js}</script>`);

fs.mkdirSync(OUT_DIR, { recursive: true });
fs.writeFileSync(OUT_FILE, out, 'utf8');

const sizeMB = (Buffer.byteLength(out, 'utf8') / (1024 * 1024)).toFixed(2);
console.log(`Build OK -> ${path.relative(__dirname, OUT_FILE)} (${sizeMB} MB)`);
