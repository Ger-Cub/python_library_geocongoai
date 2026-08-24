# Changelog

## [0.1.0] - 2026-08-24
### Added
- Initial package scaffold `geocongoai` with modules: `text`, `vision`, `ia`, `gundua_engine`.
- `text.greetings`: `saluer`, `introduire`, `dire_au_revoir`.
- `vision.qr`: `generate_qr`.
- `vision.bgremoval`: `remove_background` (wrapper rembg).
- `vision.pansharpen`: `pansharpen_brovey` (Brovey implementation).
- `ia.prithvi`: `PrithviClient` (terratorch-based wrapper).
- `ia.alphaearth`: `AlphaEarthClient` (GEE sampling wrapper).
- Basic unit tests and CI/workflows for build and publish.
