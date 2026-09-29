// Tek bir anın çizim maliyetini parça parça ölçer: node tools/profile.mjs 10.0
import { createRequire } from "module";
import http from "http";
import fs from "fs";
import path from "path";
const require = createRequire(import.meta.url);
const { chromium } = require("/opt/node22/lib/node_modules/playwright");
const dir = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const server = http.createServer((req, res) => {
  const p = path.join(dir, decodeURIComponent(req.url.split("?")[0]));
  fs.readFile(p, (e, d) => { if (e) { res.writeHead(404); res.end(); return; } res.writeHead(200); res.end(d); });
}).listen(0);
const browser = await chromium.launch({ args: ["--disable-gpu"] });
const page = await browser.newPage();
await page.goto(`http://127.0.0.1:${server.address().port}/index.html?render`);
await page.evaluate(() => window.ready);
const t = Number(process.argv[2] || 10);
const r = await page.evaluate(t => {
  const g = document.createElement("canvas"); g.width = 1920; g.height = 1080; const x = g.getContext("2d");
  const cam = camera(t), res = {};
  const time = (k, fn) => { const a = performance.now(); for (let i = 0; i < 5; i++) fn(); x.getImageData(0, 0, 1, 1); res[k] = ((performance.now() - a) / 5).toFixed(1); };
  time("background", () => drawBackground(x, t, cam));
  time("bed", () => drawBed(x, t, cam));
  time("character", () => drawCharacter(x, t, cam));
  time("line", () => drawLine(x, t, cam));
  time("bubbles", () => drawBubbles(x, t, cam));
  time("motes", () => drawMotes(x, t, cam));
  time("post", () => post(document.getElementById("c").getContext("2d"), t, 1));
  const a = performance.now(); window.renderFrame(Math.round(t * 30)); res.fullFrame = (performance.now() - a).toFixed(0);
  return res;
}, t);
console.log(t, r);
await browser.close(); server.close();
