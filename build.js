#!/usr/bin/env node
// Genera un HTML unico y autocontenido a partir de src/index.html + los <link
// rel="stylesheet"> y <script src="..."> locales que referencia, para poder
// abrirlo con doble clic o mandarlo sin depender de varios archivos juntos.
const fs = require('fs');
const path = require('path');

const SRC_DIR = path.join(__dirname, 'src');
const OUT_DIR = path.join(__dirname, 'dist');
const OUT_FILE = path.join(OUT_DIR, 'Guia_Meituan_Chino_Interactiva.html');

let html = fs.readFileSync(path.join(SRC_DIR, 'index.html'), 'utf8');

// Inline every local stylesheet link.
html = html.replace(/<link rel="stylesheet" href="([^"]+)">/g, (tag, file) => {
  const css = fs.readFileSync(path.join(SRC_DIR, file), 'utf8');
  return `<style>\n${css}</style>`;
});

// Inline every local script tag, in document order.
html = html.replace(/<script src="([^"]+)"><\/script>/g, (tag, file) => {
  const js = fs.readFileSync(path.join(SRC_DIR, file), 'utf8');
  return `<script>\n${js}</script>`;
});

fs.mkdirSync(OUT_DIR, { recursive: true });
fs.writeFileSync(OUT_FILE, html, 'utf8');

const sizeMB = (Buffer.byteLength(html, 'utf8') / (1024 * 1024)).toFixed(2);
console.log(`Build OK -> ${path.relative(__dirname, OUT_FILE)} (${sizeMB} MB)`);
