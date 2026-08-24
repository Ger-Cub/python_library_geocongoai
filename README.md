# geocongoai

Bibliothèque Python légère pour utilitaires GeoCongo AI — v0.1.0

Contenu principal:

- `geocongoai.text`: fonctions `saluer`, `introduire`, `dire_au_revoir`.
- `geocongoai.vision`: `generate_qr`, `remove_background` (extra), `pansharpen_brovey`.
- `geocongoai.ia`: `PrithviClient` (wrapper terratorch, extra `ia`).
- `geocongoai.gundua_engine`: stubs `analyse_deterministe`, `analyse_ia_fondation`, `traiter_image_satellite`.

Installation (dev rapide):

```
python -m pip install -e .[vision]
```

Voir `pyproject.toml` pour les extras `vision` et `ia`.
