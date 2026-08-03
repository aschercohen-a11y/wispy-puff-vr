// Verifie les 4 directions A L ECRAN : on projette la position du perso dans le
// repere camera. Appuyer a droite doit augmenter son X ecran, avancer doit le
// faire RECULER en profondeur (il s eloigne de la camera), etc.
// Aucun clic souris.
const puppeteer = require('puppeteer-core');
const wait = (ms) => new Promise(r => setTimeout(r, ms));

const CASES = [
  { key: 'd', label: 'DROITE ', axis: 'x', want: +1 },
  { key: 'q', label: 'GAUCHE ', axis: 'x', want: -1 },
  { key: 'z', label: 'AVANT  ', axis: 'depth', want: +1 },
  { key: 's', label: 'ARRIERE', axis: 'depth', want: -1 },
];

(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: 'new',
    args: ['--ignore-gpu-blocklist', '--enable-unsafe-swiftshader', '--use-gl=angle',
           '--use-angle=swiftshader', '--no-sandbox'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 900, height: 600 });
  await page.goto('http://127.0.0.1:8899/builder.html', { waitUntil: 'networkidle2', timeout: 90000 });
  await wait(12000);
  await page.evaluate(() => window.__builder.togglePlay(true));
  await wait(2500);

  // La camera suit le perso : sa position a l ecran est donc CONSTANTE et ne mesure
  // rien. On releve la position MONDE, et on projettera le deplacement sur les axes
  // de la camera (sa droite, et son avant horizontal).
  await page.evaluate(() => {
    window.__probe = () => {
      const h = window.__builder.getHero(), c = window.__builder.cam3;
      c.updateMatrixWorld(true);
      const e = c.matrixWorld.elements;
      return {
        p: [h.position.x, h.position.z],
        right: [e[0], e[2]],      // colonne 0 = axe droite de la camera
        fwd: [-e[8], -e[10]],     // -colonne 2 = axe de visee
      };
    };
  });

  let allOk = true;
  for (const t of CASES) {
    const before = await page.evaluate(() => window.__probe());
    await page.evaluate((k) => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key: k, bubbles: true }));
    }, t.key);
    await wait(4000);
    const after = await page.evaluate(() => window.__probe());
    await page.evaluate((k) => {
      window.dispatchEvent(new KeyboardEvent('keyup', { key: k, bubbles: true }));
    }, t.key);
    await wait(600);

    const dx = after.p[0] - before.p[0], dz = after.p[1] - before.p[1];
    const nr = Math.hypot(before.right[0], before.right[1]) || 1;
    const nf = Math.hypot(before.fwd[0], before.fwd[1]) || 1;
    let got, unit;
    if (t.axis === 'x') { got = (dx * before.right[0] + dz * before.right[1]) / nr; unit = 'vers la droite ecran'; }
    else { got = (dx * before.fwd[0] + dz * before.fwd[1]) / nf; unit = 'vers le fond ecran  '; }
    const ok = Math.sign(got) === t.want && Math.abs(got) > 0.01;
    if (!ok) allOk = false;
    console.log('%s  %s = %s   %s', t.label, unit, got.toFixed(3).padStart(7), ok ? 'OK' : 'FAUX');
  }
  console.log('');
  console.log(allOk ? '=> les 4 directions sont correctes' : '=> AU MOINS UNE DIRECTION EST FAUSSE');
  await browser.close();
})().catch(e => { console.error('ERREUR:', e.message); process.exit(1); });
