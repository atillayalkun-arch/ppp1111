// Kare kare render: index.html?render -> JPEG kareler -> ffmpeg -> MP4
// Kullanım: node render.mjs [çıktı.mp4]   |   node render.mjs --frames a,b,c  (önizleme kareleri)
import { createRequire } from "module";
import { spawn, execSync } from "child_process";
import http from "http";
import fs from "fs";
import path from "path";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "/opt/node22/lib/node_modules/playwright");

const dir = path.dirname(new URL(import.meta.url).pathname);
const args = process.argv.slice(2);
const fi = args.indexOf("--frames");
const onlyFrames = fi >= 0 ? args[fi + 1].split(",").map(Number) : null;
const outFile = (fi === 0 ? null : args[0]) || path.join(dir, "motion-edit.mp4");
const ffmpeg = process.env.FFMPEG || execSync(`python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"`).toString().trim();

const types = { ".html": "text/html", ".jpg": "image/jpeg", ".png": "image/png", ".json": "application/json", ".woff2": "font/woff2" };
const server = http.createServer((req, res) => {
  const p = path.join(dir, decodeURIComponent(req.url.split("?")[0]));
  fs.readFile(p, (e, d) => { if (e) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { "Content-Type": types[path.extname(p)] || "application/octet-stream" }); res.end(d); });
}).listen(0);
const port = server.address().port;

const browser = await chromium.launch({ args: (process.env.CHROME_ARGS || "--disable-gpu").split(" ").filter(Boolean) });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
page.on("console", m => console.log("[page]", m.text()));
page.on("pageerror", e => console.error("[pageerror]", e));
await page.goto(`http://127.0.0.1:${port}/index.html?render`);
await page.evaluate(() => window.ready);
const { frames, FPS } = await page.evaluate(() => window.META);

if (onlyFrames) {
  fs.mkdirSync(path.join(dir, "preview"), { recursive: true });
  for (const f of onlyFrames) {
    const url = await page.evaluate(f => window.renderFrame(f), f);
    fs.writeFileSync(path.join(dir, "preview", `${String(f).padStart(3, "0")}.jpg`), Buffer.from(url.split(",")[1], "base64"));
  }
} else {
  const ff = spawn(ffmpeg, ["-y", "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "mjpeg", "-i", "-",
    "-c:v", "libx264", "-preset", "slow", "-crf", "22", "-maxrate", "14M", "-bufsize", "28M", "-pix_fmt", "yuv420p", "-movflags", "+faststart", outFile],
    { stdio: ["pipe", "ignore", "inherit"] });
  const t0 = Date.now();
  for (let f = 0; f < frames; f++) {
    const url = await page.evaluate(f => window.renderFrame(f), f);
    if (!ff.stdin.write(Buffer.from(url.split(",")[1], "base64")))
      await new Promise(r => ff.stdin.once("drain", r));
    if (f % 30 === 0) console.log(`kare ${f}/${frames}  ${((Date.now() - t0) / 1000).toFixed(1)}s`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on("close", r));
  console.log("bitti:", outFile);
}
await browser.close();
server.close();
