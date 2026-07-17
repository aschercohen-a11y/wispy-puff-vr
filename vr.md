# Wispy Puff VR — Le Jardin Magique

> Jeu **VR** (Meta Quest + téléphone + PC) dans le navigateur, aucune installation.
> Tu es un **petit fantôme qui vole** dans un jardin magique : ramasser des cristaux, souffler une bulle (au **micro** !), faire pousser des plantes, transporter la bulle dans un portail.

**Jeu :** https://wispyvr.swipego.app · **Repo :** `aschercohen-a11y/wispy-puff-vr`

---

## 🔖 REPRISE DE SESSION — LIRE EN PREMIER

**Où on en est (dernière session) :**
- ✅ Jeu complet et jouable : vol fantôme 6DOF, cristaux, bulle au souffle (micro), jardinage, portail téléporteur, papillons, herbe animée, 2 maisons, champignons amanites qui dandinent.
- ✅ **Grosse découverte** : je génère des modèles **3D texturés à partir d'une PHOTO**, moi-même, via l'IA **TripoSR** (voir §« Pouvoir clé »). Testé et validé sur la maison-carotte.
- 🟡 **Dernier truc en cours** : la **maison-carotte IA** (`models/carrot_ai.glb`) vient d'être plantée à `(x=7, z=6)`, échelle 6, `rotation.y = Math.PI`. **À vérifier dans le casque** : taille OK ? porte orientée vers le centre ? couleurs à rendre plus vives ? → ajuster dans `index.html` (loader `carrot_ai.glb`).

**Comment reprendre :**
1. Ouvrir le dossier `C:\Users\asche\Downloads\claude\Oculus`.
2. Le jeu = **`index.html`** (toute la scène + logique).
3. Modifier → déployer (voir §Workflow) → recharger `wispyvr.swipego.app` dans le Quest.
4. ⚠️ **PC WebGL cassé** (GPU AMD planté) → la preview 3D ne marche PAS sur le PC de l'utilisateur (Chrome). Tester **dans le casque** ou sur **téléphone**. Réparer = redémarrer PC + mettre à jour pilote AMD.

---

## 🎨 LE POUVOIR CLÉ : photo → 3D texturée (par IA, de mon côté)

**On peut transformer n'importe quelle photo d'objet en modèle 3D texturé**, sans que l'utilisateur touche à son PC. Pipeline testé :

```bash
pip install gradio_client Pillow
```

**Génération (image → GLB) — `dev/triposr.py` :**
- Service : **`stabilityai/TripoSR`** (Hugging Face, gratuit, appelé via `gradio_client`).
- Endpoints : `/preprocess` (image, remove_bg=True, fg_ratio=0.85) → image détourée ; puis `/generate` (image, marching_cubes_resolution=256) → `(obj, glb)`.
- Sortie : GLB **texturé** (couleurs de la photo). Qualité : organique mais un peu « fondu » et couleurs douces.

**Autres services testés :**
- `stabilityai/stable-fast-3d` (SF3D) : meilleure qualité mais a renvoyé **AppError** (quota GPU anonyme) — réessayer plus tard, ou avec un token HF.
- `JeffreyXiang/TRELLIS` : CONFIG_ERROR (cassé au moment du test).
- `tencent/Hunyuan3D-2*` : Internal Server Error.
→ **TripoSR = le fiable pour l'instant.**

**Aperçu/rendu (Blender headless) :**
- `dev/render2.py` : rend un GLB en image (cadrage auto). Cycles **CPU** (EEVEE plante en headless). **view_transform = 'Standard'** (sinon AgX délave les couleurs vives).
- `dev/turntable.py` : rend 16 vues en rotation → puis on assemble un **GIF 360°** avec Pillow.

**Pour ajouter un objet depuis une photo :** `dev/triposr.py` (changer `IMG` et `OUT`) → rendre avec `render2.py` pour valider → copier le `.glb` dans `models/` → ajouter un `GLTFLoader().load(...)` dans `index.html` → déployer.

---

## 🛠️ Fabrication des modèles — 2 voies

| Voie | Pour quoi | Fichiers |
|---|---|---|
| **Script Blender (`bpy`)** | pièces simples/stylisées sur-mesure | `dev/crystal.py`, `dev/mushroom2.py` (amanite), `dev/carrothouse.py`, `dev/house.py` |
| **IA photo→3D (TripoSR)** | objets détaillés depuis une image | `dev/triposr.py` |
| **Packs gratuits Poly Pizza (CC0)** | assets détaillés prêts | téléchargés (arbre, chaumière) |

**Astuces Blender apprises :** rendu en **Standard** (pas AgX), Cycles **CPU** en headless, matériau **verre+émission** (cristal), **spirale de Fibonacci** pour les pois du champignon, pilotage 100% par **script** (je n'ai pas la main sur le **sculptage manuel** → c'est pour ça que la carotte détaillée passe par l'IA).

---

## 🎮 Gameplay (mini-jeux mélangés)

| Jeu | But | Comment |
|---|---|---|
| 👻 **Voler** | explorer partout | vol libre 6DOF, traverse les murs |
| 🔮 **Cristaux** | ramasser les 12 (dont flottants) | s'approcher → +1 graine + son/effet |
| 🫧 **Bulle** | la mener au **portail** | souffler (micro/gâchette/bouton/F) ; elle **flotte à hauteur fixe** (ne tombe pas), on l'oriente ; **gondole** comme une vraie bulle, laisse une **traînée**, **éclate en gouttelettes** au contact d'un objet |
| 🌀 **Portail** | transporter un max de bulles | réussite → aspiration + jingle → le portail réapparaît ailleurs |
| 🌱 **Jardinage** | faire pousser | graines (=cristaux) → planter champignon/fleur/arbre qui grandit |

**Ambiance :** herbe 3D qui ondule (vent), nuages, **8 papillons** qui volètent, **champignons amanites** qui dandinent (squash & stretch), ciel de jour + soleil.

---

## 🕹️ Contrôles

### 🥽 Quest (VR immersif)
> ⚠️ Cliquer le **GROS bouton « ENTER VR »** en bas de la PAGE (pas le mode VR du navigateur). Dans le vrai mode, le jardin t'entoure à 360° **sans aucune fenêtre**. Activer le **micro sur la page AVANT** d'entrer.
- **Stick gauche** : voler vers où tu regardes (regarde en haut = tu montes)
- **Stick droit** haut/bas : monter/descendre — gauche/droite : pivoter
- **Gâchette** : souffler · **Grip** : planter

### 📱 Téléphone
- **Joystick** : voler · **glisser** : regarder
- Boutons : **⬆/⬇** (monter/descendre), **💨** (souffler), **🌱** (planter), **🎤** (activer micro)

### 🖥️ PC (si WebGL réparé)
- Souris : orbiter · **F** : souffler · **G** : planter

---

## 🚀 Workflow / déploiement

```
Éditer index.html  →  déployer  →  recharger dans le Quest
```
**Déployer (2 étapes) :**
```bash
cd C:\Users\asche\Downloads\claude\Oculus
git add . && git commit -m "..." && git push        # (email achat@shootnbox.fr)
# puis déclencher Coolify :
curl -H "Authorization: Bearer <TOKEN>" \
  "http://217.182.89.133:8000/api/v1/deploy?uuid=pj5udv9xweahucsyyktq509d&force=true"
```
**Anti-cache** : si on change un `.glb` déjà déployé, ajouter `?v=N` sur l'URL de chargement dans `index.html`.

**Vérifier sans casque** (mon côté) : `node dev/shot.js` (screenshot du déployé) ou `dev/shot-local.js` (localhost) — via un serveur `python -m http.server 8080` dans `Oculus/`.

---

## 🧱 Infrastructure

- **URL** : https://wispyvr.swipego.app · **Repo** : `aschercohen-a11y/wispy-puff-vr` (public)
- **Serveur** : OVH `217.182.89.133` (Coolify) · **App UUID** : `pj5udv9xweahucsyyktq509d`
- **Deploy API** : `GET http://217.182.89.133:8000/api/v1/deploy?uuid=pj5udv9xweahucsyyktq509d&force=true` (Bearer token — voir CLAUDE.md global)
- **Build** : `Dockerfile` → **nginx** statique. three.js **vendu en local** (`vendor/`), aucun CDN.

---

## 📁 Structure

```
Oculus/
├── index.html            ← TOUT le jeu (scène three.js + logique + contrôles)
├── game.js               ← moteur 2D d'origine (masqué : GAME_ENABLED=false)
├── Dockerfile
├── vendor/               ← three.js local (three.module.js, GLTFLoader, OrbitControls, VRButton, BufferGeometryUtils)
├── models/               ← .glb
│   ├── crystal.glb           (Blender script)
│   ├── mushroom.glb          (Blender script — amanite rouge, remplace l'ancien)
│   ├── pp_tree.glb           (Poly Pizza CC0)
│   ├── pp_cartoonhouse.glb   (Poly Pizza CC0 — chaumière)
│   ├── carrothouse.glb       (Blender script — ANCIENNE carotte, non utilisée)
│   └── carrot_ai.glb         (IA TripoSR — carotte PLANTÉE, texturée)
├── dev/                  ← scripts de fabrication (Blender + IA + vérif)  ← IMPORTANT, sauvegardés ici
│   ├── triposr.py            (photo → GLB texturé via TripoSR)
│   ├── sf3d.py               (alternative SF3D, quota-limité)
│   ├── render2.py / render_front.py  (rendu preview d'un GLB)
│   ├── turntable.py          (16 vues → GIF 360°)
│   ├── crystal.py / mushroom2.py / carrothouse.py / house.py  (modèles scriptés)
│   └── shot.js / shot-local.js / diag.js / probe*.py  (vérif headless + sondage Spaces IA)
├── vr.md                 ← ce document (état + doc complète)
├── preview.ps1           ← preview locale (localhost:8080)
└── carotte-360.gif / carotte-avant.png   ← aperçus de la carotte IA
```

---

## ✅ Fait / 🟡 En cours / 💡 À faire

**Fait :** vol fantôme, cristaux, bulle+micro+éclatement, portail téléporteur, jardinage, papillons, herbe animée, 2 maisons, amanites qui dandinent, pipeline **photo→3D IA**.

**En cours (à finir) :**
- 🟡 **Carotte IA** plantée — vérifier dans le casque : **taille / orientation porte / couleurs** (rendre plus vives ?). Loader dans `index.html` (`carrot_ai.glb`, pos (7,6), scale 6, rotY π).

**Idées / suite :**
- 🎨 Booster la saturation de la carotte IA · relancer une gen plus nette (ou SF3D avec token)
- 🐦 oiseaux qui planent · 🐝 abeilles · 🎵 musique d'ambiance · 💧 étang/ruisseau · 🌅 cycle jour/nuit
- 🎯 niveaux, chrono, score de survie de la bulle · ✨ plus de particules (collecte/plantation)
- 🔧 réparer le WebGL du PC (redémarrage + pilote AMD) pour la preview PC

---

## 👥 Méthode de travail
- **Utilisateur** : idées, direction artistique, **photos de référence**, tests casque.
- **Moi** : code three.js/WebXR, scripts Blender, **génération IA photo→3D**, déploiement, réglages.
- **Règle magique** : une **photo** d'objet → je le transforme en **3D texturée** (IA) → je le **plante** dans le jardin.

*Wispy Puff VR — un petit fantôme, une bulle, un jardin magique. Fait à deux, dans le navigateur, pour le Meta Quest.*
