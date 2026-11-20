# Marmotte-o-mètre 3000

Les marmottes hibernent-elles en ce moment ? Réponse en 3D, en musique, en français et en anglais.

Un site par langue, chacun sur son domaine :

- français : https://estcequelesmarmotteshibernent.fr
- anglais : https://aremarmotshibernating.com

## Fichiers

- `src/page.html` : la page (HTML, CSS, JS).
- `src/i18n.json` : tous les textes, dans les deux langues.
- `assets/og.png` : image d'aperçu pour les partages.
- `build.py` : construit `dist/`.

## Construire

```bash
python3 build.py
```

Pour d'autres domaines : `python3 build.py https://site-francais https://site-anglais`.

`dist/` contient :

- `fr/` : le site français ;
- `en/` : le site anglais ;
- `artifact.html` : version bilingue en un seul fichier pour l'artefact claude.ai (à ne pas déployer).

Le site anglais envoie les navigateurs réglés en français vers le site français. Le site français ne redirige jamais, pour rester indexable. Le lien de changement de langue en bas de page prend le dessus sur la détection.

## Tester en local

```bash
cd dist/fr && python3 -m http.server 8000
```

## Mettre en ligne (Vercel)

Vercel construit le site à chaque push grâce à `vercel.json` : il lance `python3 build.py` et sert le dossier `public/`.

Deux projets Vercel branchés sur ce même dépôt, un par langue :

| Projet | Variable d'environnement | Domaine |
| --- | --- | --- |
| site français | `MARMOT_SITE=fr` (valeur par défaut) | estcequelesmarmotteshibernent.fr |
| site anglais | `MARMOT_SITE=en` | aremarmotshibernating.com |

La variable se règle dans Settings, Environment Variables. Le domaine s'ajoute dans Settings, Domains ; Vercel affiche alors les enregistrements DNS à créer chez OVH.

## Après la mise en ligne

Déclarer les deux sites dans Google Search Console et soumettre leur `sitemap.xml`.
