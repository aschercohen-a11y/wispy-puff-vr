// Verifie que le perso NE COURT PLUS tout seul et qu il repond aux touches.
//
// ATTENTION : aucun clic souris. La carte de production (wispy_layout id=2) a deja
// ete ecrasee deux fois par des tests headless qui declenchaient scheduleSave().
// On passe par window.__builder.togglePlay et par des evenements clavier.
const puppeteer = require('puppeteer-core');
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';

const wait = (ms) => new Promise(r => setTimeout(r, ms));

(async () => {
  const errs = [];
  const browser = await puppeteer.launch({
    executablePath: CHROME, headless: 'new',
    args: ['--ignore-gpu-blocklist', '--enable-unsafe-swiftshader', '--use-gl=angle',
           '--use-angle=swiftshader', '--no-sandbox'],
  });
  const page = await browser.newPage();
  page.on('pageerror', e => errs.push('[PAGEERROR] ' + e.message));
  await page.setViewport({ width: 1200, height: 700 });
  await page.goto('http://127.0.0.1:8899/builder.html', { waitUntil: 'networkidle2', timeout: 90000 });
  await wait(12000);

  await page.evaluate(() => window.__builder.togglePlay(true));
  await wait(600);
  const start = await page.evaluate(() => window.__builder.heroPos());

  // 1) IMMOBILE : sans aucune touche, le perso ne doit pas bouger
  await wait(2000);
  const idle = await page.evaluate(() => window.__builder.heroPos());
  const drift = Math.hypot(idle[0] - start[0], idle[2] - start[2]);

  // 2) TOUCHE AVANT maintenue : le perso doit avancer
  await page.evaluate(() => {
    const ev = (t, k) => window.dispatchEvent(new KeyboardEvent(t, { key: k, bubbles: true }));
    ev('keydown', 'z');
    window.__stopWalk = () => ev('keyup', 'z');
  });
  await wait(6000);
  const moved = await page.evaluate(() => { const p = window.__builder.heroPos(); window.__stopWalk(); return p; });
  const dist = Math.hypot(moved[0] - idle[0], moved[2] - idle[2]);

  // 3) RELACHE : le perso doit s arreter
  await wait(300);
  const a = await page.evaluate(() => window.__builder.heroPos());
  await wait(1200);
  const b = await page.evaluate(() => window.__builder.heroPos());
  const after = Math.hypot(b[0] - a[0], b[2] - a[2]);

  console.log('depart          : ' + start.map(v => v.toFixed(1)).join(', '));
  console.log('1) immobile 2s  : derive = ' + drift.toFixed(3) + '  ' + (drift < 0.05 ? 'OK (ne court plus tout seul)' : 'ECHEC : ca bouge encore seul'));
  console.log('2) touche 6s    : distance = ' + dist.toFixed(2) + '  ' + (dist > 2 ? 'OK (il avance)' : 'ECHEC : il ne bouge pas'));
  console.log('3) relachee     : derive = ' + after.toFixed(3) + '  ' + (after < 0.05 ? 'OK (il s arrete)' : 'ECHEC : il continue'));
  console.log('   -> images rendues estimees : ' + (dist/0.375).toFixed(0) + ' (soit ~' + (dist/0.375/6).toFixed(1) + ' img/s en rendu logiciel)');
  console.log('erreurs page    : ' + (errs.length ? errs.join(' | ') : 'aucune'));
  await browser.close();
})().catch(e => { console.error('FATAL', e); process.exit(1); });
