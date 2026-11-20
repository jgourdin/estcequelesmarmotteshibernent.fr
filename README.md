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

Un projet Vercel par dossier :

```bash
cd dist/fr && npx vercel deploy --prod
cd ../en && npx vercel deploy --prod
```

Au premier lancement, Vercel demande de se connecter et de nommer le projet. Ensuite, dans chaque projet : Settings, Domains, ajouter le domaine. Vercel affiche les enregistrements DNS à créer chez OVH (zone DNS du domaine).

Après une modification : `python3 build.py`, puis les deux mêmes commandes.

## Après la mise en ligne

Déclarer les deux sites dans Google Search Console et soumettre leur `sitemap.xml`.
