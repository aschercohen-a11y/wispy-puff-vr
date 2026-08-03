// Verifie que le perso joue le BON clip selon son etat, et qu il a les pieds au sol.
// Aucun clic souris (cf. incidents d ecrasement de la carte de prod).
const puppeteer = require('puppeteer-core');
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const wait = (ms) => new Promise(r => setTimeout(r, ms));
const top = (w) => Object.entries(w).sort((a, b) => b[1] - a[1])[0];

(async () => {
  const errs = [];
  const browser = await puppeteer.launch({
    executablePath: CHROME, headless: 'new',
    args: ['--ignore-gpu-blocklist', '--enable-unsafe-swiftshader', '--use-gl=angle',
           '--use-angle=swiftshader', '--no-sandbox'],
  });
  const page = await browser.newPage();
  page.on('pageerror', e => errs.push('[PAGEERROR] ' + e.message));
  await page.setViewport({ width: 1000, height: 600 });
  await page.goto('http://127.0.0.1:8899/builder.html', { waitUntil: 'networkidle2', timeout: 90000 });
  await wait(12000);

  await page.evaluate(() => window.__builder.togglePlay(true));
  await wait(4000);

  const idleW = await page.evaluate(() => window.__builder.animWeights());
  const footIdle = await page.evaluate(() => window.__builder.heroFootY());

  await page.evaluate(() => {
    const ev = (t, k) => window.dispatchEvent(new KeyboardEvent(t, { key: k, bubbles: true }));
    ev('keydown', 'z');
    window.__stop = () => ev('keyup', 'z');
  });
  await wait(5000);
  const walkW = await page.evaluate(() => window.__builder.animWeights());
  const footWalk = await page.evaluate(() => window.__builder.heroFootY());
  await page.evaluate(() => window.__stop());

  const ti = top(idleW), tw = top(walkW);
  console.log('AU REPOS    clip dominant : ' + ti[0] + ' (' + ti[1] + ')  ' + (ti[0] === 'Lower_Weapon_Look_Raise' ? 'OK' : 'ECHEC'));
  console.log('            poids : ' + JSON.stringify(idleW));
  console.log('EN MARCHE   clip dominant : ' + tw[0] + ' (' + tw[1] + ')  ' + (tw[0] === 'Walking' ? 'OK' : 'ECHEC'));
  console.log('            poids : ' + JSON.stringify(walkW));
  console.log('');
  console.log('PIEDS (y le plus bas du perso, 0 = sol) : repos ' + footIdle + ' / marche ' + footWalk);
  console.log('   ' + (Math.abs(footIdle) < 0.25 ? 'OK, pose au sol' : 'PROBLEME : enfonce de ' + (-footIdle).toFixed(2)));
  console.log('erreurs page : ' + (errs.length ? errs.join(' | ') : 'aucune'));
  await browser.close();
})().catch(e => { console.error('FATAL', e); process.exit(1); });
