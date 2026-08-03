// Capture rapprochee du perso en mode Jeu, pour verifier a l oeil qu il est bien
// pose au sol (Box3.setFromObject mesure la pose de repos du squelette, pas la
// pose animee : seule une image permet de trancher).
// Aucun clic souris.
const puppeteer = require('puppeteer-core');
const wait = (ms) => new Promise(r => setTimeout(r, ms));

(async () => {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: 'new',
    args: ['--ignore-gpu-blocklist', '--enable-unsafe-swiftshader', '--use-gl=angle',
           '--use-angle=swiftshader', '--no-sandbox'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1100, height: 700 });
  await page.goto('http://127.0.0.1:8899/builder.html', { waitUntil: 'networkidle2', timeout: 90000 });
  await wait(12000);

  await page.evaluate(() => window.__builder.togglePlay(true));
  await wait(3000);

  // On rapproche la camera du perso pour bien voir ses pieds et le sol.
  await page.evaluate(() => {
    const h = window.__builder.getHero(), c = window.__builder.cam3;
    c.position.set(h.position.x + 3.2, h.position.y + 1.3, h.position.z + 3.2);
    c.lookAt(h.position.x, h.position.y + 0.7, h.position.z);
  });
  await wait(2500);
  await page.screenshot({ path: 'C:\\Users\\asche\\Downloads\\claude\\Oculus\\dev\\hero_sol.png' });
  console.log('capture -> dev/hero_sol.png');
  await browser.close();
})().catch(e => { console.error('ERREUR:', e.message); process.exit(1); });
