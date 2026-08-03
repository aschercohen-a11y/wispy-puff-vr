// Capture builder.html en mode plat PUIS en mode éclairé, pour comparer.
//
// ⚠️ AUCUN clic souris : la carte de production (wispy_layout id=2) a déjà été
// écrasée deux fois par des tests headless qui déclenchaient scheduleSave().
// On passe exclusivement par window.__setLighting, qui ne sauvegarde rien.
const puppeteer = require('puppeteer-core');
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const OUT = process.argv[2] || 'C:\\Users\\asche\\Downloads\\claude\\Oculus\\dev';

(async () => {
  const errs = [];
  const browser = await puppeteer.launch({
    executablePath: CHROME, headless: 'new',
    args: ['--ignore-gpu-blocklist', '--enable-unsafe-swiftshader', '--use-gl=angle',
           '--use-angle=swiftshader', '--no-sandbox'],
  });
  const page = await browser.newPage();
  page.on('pageerror', e => errs.push('[PAGEERROR] ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errs.push('[CONSOLE] ' + m.text().slice(0, 200)); });
  await page.setViewport({ width: 1400, height: 800 });
  await page.goto('http://127.0.0.1:8899/builder.html', { waitUntil: 'networkidle2', timeout: 90000 });
  await new Promise(r => setTimeout(r, 12000));   // laisser charger les 30 GLB

  await page.evaluate(() => window.__setLighting(false));
  await new Promise(r => setTimeout(r, 1500));
  await page.screenshot({ path: OUT + '\\lit_avant.png' });

  await page.evaluate(() => window.__setLighting(true));
  await new Promise(r => setTimeout(r, 1500));
  await page.screenshot({ path: OUT + '\\lit_apres.png' });

  const info = await page.evaluate(() => {
    let basic = 0, lambert = 0;
    // eslint-disable-next-line no-undef
    return { ok: typeof window.__setLighting === 'function' };
  });
  console.log('captures -> ' + OUT);
  console.log('toggle expose : ' + info.ok);
  console.log('erreurs : ' + (errs.length ? errs.join(' | ') : 'aucune'));
  await browser.close();
})().catch(e => { console.error('FATAL', e); process.exit(1); });
