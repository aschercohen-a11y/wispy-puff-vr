const puppeteer = require('puppeteer-core');
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';

(async () => {
  const logs = [];
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: 'new',
    args: ['--ignore-gpu-blocklist', '--enable-webgl', '--use-gl=angle', '--use-angle=swiftshader', '--no-sandbox']
  });
  const page = await browser.newPage();
  page.on('console', m => logs.push('[' + m.type() + '] ' + m.text()));
  page.on('pageerror', e => logs.push('[PAGEERROR] ' + e.message));
  page.on('requestfailed', r => logs.push('[REQFAIL] ' + r.url() + ' ' + (r.failure() && r.failure().errorText)));

  await page.goto('https://wispyvr.swipego.app/', { waitUntil: 'networkidle2', timeout: 40000 });
  await new Promise(r => setTimeout(r, 5000)); // laisser tourner quelques secondes

  const info = await page.evaluate(() => {
    const out = {};
    try {
      const c = document.getElementById('game');
      out.canvasW = c.width; out.canvasH = c.height;
      const g = c.getContext('2d');
      const d = g.getImageData(0, 0, c.width, c.height).data;
      let min = [255,255,255], max = [0,0,0];
      const colors = new Set();
      for (let i = 0; i < d.length; i += 997 * 4) {
        for (let k = 0; k < 3; k++) { min[k] = Math.min(min[k], d[i+k]); max[k] = Math.max(max[k], d[i+k]); }
        colors.add(d[i] + ',' + d[i+1] + ',' + d[i+2]);
      }
      out.pixelMin = min; out.pixelMax = max; out.distinctColors = colors.size;
    } catch (e) { out.canvasErr = String(e); }
    try { out.state = (typeof state !== 'undefined') ? state : 'undef'; } catch(e){ out.state='ref:'+e.message; }
    try { out.gameCBset = !!window.__gameCB; } catch(e){}
    try { out.ghost = (typeof ghost !== 'undefined') ? {x: Math.round(ghost.x), y: Math.round(ghost.y)} : 'undef'; } catch(e){ out.ghost='ref:'+e.message; }
    try { out.level1Ready = (typeof imgReady !== 'undefined') ? imgReady('assets/level1.png') : 'no-fn'; } catch(e){ out.level1Ready='ref:'+e.message; }
    try { out.THREE = (typeof window.__three_ok !== 'undefined'); } catch(e){}
    return out;
  });

  console.log('=== INFO ===');
  console.log(JSON.stringify(info, null, 2));
  console.log('=== LOGS (' + logs.length + ') ===');
  console.log(logs.slice(0, 40).join('\n'));
  await browser.close();
})().catch(e => { console.error('FATAL', e); process.exit(1); });
