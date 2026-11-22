// Live New Year countdown as an SVG (Cloudflare Worker).
// Digits tick by themselves via CSS animation phase offsets - no JavaScript in the SVG,
// so it works inside a GitHub README.
//
// Query params:  ?theme=dark|light   ?to=2027   ?tz=5 (UTC offset in hours, default 5 = Tashkent)

const THEMES = {
  light: { bg1: "#FFFFFF", bg2: "#F8FAFC", bg3: "#EEF6FF", b1: "#2563EB", b2: "#06B6D4", b3: "#7C3AED",
           title: "#1D4ED8", text: "#0F172A", muted: "#475569", track: "#CBD5E1", panel: "#FFFFFF", panelOp: ".75",
           snowFill: "#FFFFFF", snowStroke: "#93C5FD", snowOp: .95 },
  dark:  { bg1: "#030712", bg2: "#07111F", bg3: "#0B1220", b1: "#7C3AED", b2: "#22D3EE", b3: "#10B981",
           title: "#22D3EE", text: "#F8FAFC", muted: "#94A3B8", track: "#334155", panel: "#0F172A", panelOp: ".55",
           snowFill: "#FFFFFF", snowStroke: null, snowOp: .8 },
};
const BULBS = ["#EF4444", "#F59E0B", "#10B981", "#22D3EE", "#A78BFA", "#F472B6"];
const CONFETTI = [...BULBS, "#FACC15"];
const W = 560, H = 290, ROW = 56;

function rng(seed) {                       // deterministic PRNG (mulberry32)
  return () => { seed |= 0; seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
const f1 = (n) => n.toFixed(1);
const pad2 = (n) => String(n).padStart(2, "0");

function snow(t, n = 30, seed = 11) {
  const r = rng(seed), st = t.snowStroke ? ` stroke="${t.snowStroke}" stroke-width=".8"` : "";
  let o = "";
  for (let i = 0; i < n; i++) {
    const x = 8 + r() * (W - 16), rad = 1.4 + r() * 2, dur = (9 + r() * 9) * (1 + (3.4 - rad) / 6);
    o += `<g class="fall" style="animation-duration:${f1(dur)}s;animation-delay:-${f1(r() * dur)}s">` +
         `<g class="sway" style="animation-duration:${f1(2.5 + r() * 2.5)}s"><circle cx="${f1(x)}" cy="0" r="${f1(rad)}" ` +
         `fill="${t.snowFill}" fill-opacity="${t.snowOp}"${st}/></g></g>`;
  }
  return o;
}
function confetti(n = 34, seed = 7) {
  const r = rng(seed); let o = "";
  for (let i = 0; i < n; i++) {
    const x = 10 + r() * (W - 20), dur = 5 + r() * 5;
    o += `<g class="fall" style="animation-duration:${f1(dur)}s;animation-delay:-${f1(r() * dur)}s">` +
         `<g class="sway" style="animation-duration:${f1(1.5 + r() * 2)}s"><rect x="${f1(x)}" y="0" width="${f1(4 + r() * 4)}" ` +
         `height="${f1(7 + r() * 6)}" rx="1.5" fill="${CONFETTI[i % 7]}" fill-opacity=".9" ` +
         `transform="rotate(${Math.floor(r() * 80)} ${f1(x)} 0)"/></g></g>`;
  }
  return o;
}
function garland(wire) {
  const y0 = 6, sag = 11, segs = 5, margin = 40, segW = (W - 2 * margin) / segs; let o = "", k = 0;
  for (let s = 0; s < segs; s++) {
    const x0 = margin + s * segW, x1 = x0 + segW, cx = (x0 + x1) / 2, cy = y0 + 2 * sag;
    o += `<path d="M${f1(x0)} ${y0} Q${f1(cx)} ${cy} ${f1(x1)} ${y0}" fill="none" stroke="${wire}" stroke-opacity=".65" stroke-width="1.4"/>`;
    for (const tt of [.2, .4, .6, .8]) {
      const bx = (1 - tt) ** 2 * x0 + 2 * (1 - tt) * tt * cx + tt ** 2 * x1;
      const by = (1 - tt) ** 2 * y0 + 2 * (1 - tt) * tt * cy + tt ** 2 * y0;
      o += `<g class="bulb" style="animation-duration:${(1.6 + (k % 4) * .35).toFixed(2)}s;animation-delay:-${((k * .37) % 2).toFixed(2)}s">` +
           `<rect x="${f1(bx - 1.6)}" y="${f1(by)}" width="3.2" height="3" fill="${wire}"/>` +
           `<ellipse cx="${f1(bx)}" cy="${f1(by + 6)}" rx="3.3" ry="4.2" fill="${BULBS[k % 6]}"/>` +
           `<ellipse cx="${f1(bx + .9)}" cy="${f1(by + 4.7)}" rx=".9" ry="1.4" fill="#fff" fill-opacity=".7"/></g>`;
      k++;
    }
  }
  return o;
}

// One ticking unit: a vertical strip of rows (counting down) shown through a clip window.
// `tau0` is the animation phase at load time (seconds), `stepSec` how long each row stays.
function unit(i, x, w, t, label, rows, tau0, stepSec, loop) {
  const cx = x + w / 2, top = 100, win = top + 10;
  const texts = rows.map((v, k) => `<text x="${f1(cx)}" y="${win + 42 + k * ROW}" font-size="46" font-weight="700" ` +
                                  `text-anchor="middle" fill="${t.text}">${pad2(v)}</text>`).join("");
  let anim = "";
  if (rows.length > 1) {
    const total = rows.length * stepSec;
    anim = `animation:k${i} ${total}s steps(${rows.length},end) ${loop ? "infinite" : "1 forwards"};animation-delay:-${tau0}s`;
  }
  return `<g class="fade"><rect x="${x}" y="${top}" width="${w}" height="104" rx="14" fill="${t.panel}" fill-opacity="${t.panelOp}" stroke="${t.track}"/>` +
         `<clipPath id="c${i}"><rect x="${x + 6}" y="${win}" width="${w - 12}" height="${ROW}"/></clipPath>` +
         `<g clip-path="url(#c${i})"><g style="${anim}">${texts}</g></g>` +
         `<text x="${f1(cx)}" y="${top + 92}" font-size="12" letter-spacing="2" text-anchor="middle" fill="${t.muted}">${label}</text></g>` +
         (rows.length > 1 ? `@@K${i}:${-rows.length * ROW}@@` : "");
}

export function render({ now = new Date(), theme = "dark", to, tz = 5 } = {}) {
  const t = THEMES[theme] || THEMES.dark;
  const local = new Date(now.getTime() + tz * 3600e3);            // "wall clock" in target tz (read via UTC getters)
  const yr = local.getUTCFullYear();
  const newYearWindow = local.getUTCMonth() === 0 && local.getUTCDate() <= 15 && !to;
  const ny = to ? Number(to) : (newYearWindow ? yr : yr + 1);
  const targetMs = Date.UTC(ny, 0, 1) - tz * 3600e3;
  const R = Math.max(0, Math.floor((targetMs - now.getTime()) / 1000));   // seconds remaining
  const done = R === 0 || newYearWindow;

  let body = "";
  const yStart = Date.UTC(done ? ny : ny - 1, 0, 1) - tz * 3600e3, yEnd = Date.UTC(done ? ny + 1 : ny, 0, 1) - tz * 3600e3;
  const pct = done ? 100 : Math.floor((now.getTime() - yStart) / (yEnd - yStart) * 100);
  let kf = "";

  if (!done) {
    const s = R % 60, m = Math.floor(R / 60) % 60, h = Math.floor(R / 3600) % 24, d = Math.floor(R / 86400);
    const down = (from) => Array.from({ length: from + 1 }, (_, i) => from - i);        // [from..0]
    const dRows = down(d);
    const cw = 115, gap = 12, x0 = 32;
    const units = [
      unit(0, x0, cw, t, "DAYS", dRows, 86400 - (R % 86400) - 1, 86400, false),
      unit(1, x0 + (cw + gap), cw, t, "HOURS", down(23), (24 - h) * 3600 - (R % 3600) - 1, 3600, true),
      unit(2, x0 + 2 * (cw + gap), cw, t, "MINUTES", down(59), (60 - m) * 60 - s - 1, 60, true),
      unit(3, x0 + 3 * (cw + gap), cw, t, "SECONDS", down(59), 59 - s, 1, true),
    ];
    // unit() leaves keyframe markers after each unit's markup; collect them into <style>
    for (const u of units) {
      const mm = u.match(/@@K(\d):(-?\d+)@@/);
      if (mm) kf += `@keyframes k${mm[1]}{to{transform:translateY(${mm[2]}px)}}`;
      body += u.replace(/@@K\d:-?\d+@@/, "");
    }
  } else {
    body = `<text x="${W / 2}" y="152" font-size="64" font-weight="700" text-anchor="middle" fill="${t.text}">${ny}</text>` +
           `<text x="${W / 2}" y="190" font-size="17" letter-spacing="5" text-anchor="middle" fill="${t.title}">HAPPY NEW YEAR!</text>`;
  }
  const barW = W - 64, label = done ? `${ny}.status: online` : `${ny - 1}.loading... ${pct}%`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="New Year countdown">` +
    `<style>text{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}` +
    `.cur{animation:b 1.1s steps(1) infinite}@keyframes b{50%{opacity:0}}` +
    `.fade{opacity:0;animation:f .6s ease forwards}@keyframes f{to{opacity:1}}` +
    `.pg{transform-origin:0 0;transform:scaleX(0);animation:g 1.6s cubic-bezier(.2,.8,.2,1) forwards}@keyframes g{to{transform:scaleX(1)}}` +
    `@keyframes fall{from{transform:translateY(-24px)}to{transform:translateY(${H + 24}px)}}` +
    `@keyframes sway{from{transform:translateX(-9px)}to{transform:translateX(9px)}}` +
    `@keyframes blink{0%,100%{opacity:1}50%{opacity:.25}}` +
    `.fall{animation:fall linear infinite}.sway{animation:sway ease-in-out infinite alternate}.bulb{animation:blink ease-in-out infinite}` +
    `${kf}@media (prefers-reduced-motion:reduce){.fall,.sway,.bulb{animation:none}}</style>` +
    `<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${t.bg1}"/><stop offset=".55" stop-color="${t.bg2}"/><stop offset="1" stop-color="${t.bg3}"/></linearGradient>` +
    `<linearGradient id="bd" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="${W}" y2="${H}"><stop offset="0" stop-color="${t.b1}"/><stop offset=".5" stop-color="${t.b2}"/><stop offset="1" stop-color="${t.b3}"/></linearGradient>` +
    `<linearGradient id="pgf" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="${t.b1}"/><stop offset=".5" stop-color="${t.b2}"/><stop offset="1" stop-color="${t.b3}"/></linearGradient></defs>` +
    `<rect x="1" y="1" width="${W - 2}" height="${H - 2}" rx="28" fill="url(#bg)"/>` +
    `<rect x="1.5" y="1.5" width="${W - 3}" height="${H - 3}" rx="28" fill="none" stroke="url(#bd)" stroke-opacity=".6" stroke-width="1.5"/>` +
    snow(t) + garland(t.muted) +
    `<text x="32" y="68" font-size="14" fill="${t.muted}">$ ./countdown --to ${ny}<tspan class="cur" fill="${t.title}"> ▌</tspan></text>` +
    body +
    `<rect x="32" y="234" width="${barW}" height="8" rx="4" fill="${t.track}" fill-opacity=".6"/>` +
    `<rect class="pg" x="32" y="234" width="${Math.max(barW * pct / 100, 8).toFixed(1)}" height="8" rx="4" fill="url(#pgf)"/>` +
    `<text x="32" y="270" font-size="13" fill="${t.muted}">${label}</text>` +
    (done ? confetti() : "") + `</svg>`;
}

export default {
  async fetch(request) {
    const u = new URL(request.url);
    const svg = render({
      theme: u.searchParams.get("theme") === "light" ? "light" : "dark",
      to: /^\d{4}$/.test(u.searchParams.get("to") || "") ? u.searchParams.get("to") : undefined,
      tz: Number.isFinite(Number(u.searchParams.get("tz"))) && u.searchParams.get("tz") !== null ? Number(u.searchParams.get("tz")) : 5,
    });
    return new Response(svg, { headers: {
      "Content-Type": "image/svg+xml; charset=utf-8",
      // The countdown phase is baked in at request time, so it must never be cached.
      "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
      "Pragma": "no-cache", "Expires": "0",
      "Access-Control-Allow-Origin": "*",
    }});
  },
};
