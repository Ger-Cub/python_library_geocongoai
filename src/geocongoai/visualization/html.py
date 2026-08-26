"""Générateur de rendu HTML autonome pour GeoResult.
"""
from typing import Optional, Any
from .plotly import PlotlyRenderer, _get_logo_b64


class HTMLRenderer:
    """Générateur d'exportation HTML offline autonome."""

    def __init__(self, result: Any):
        self.result = result

    def render(self, output_path: Optional[str] = None) -> str:
        """Génère la chaîne HTML autonome avec en-tête professionnel, logo GeoCongo AI et Plotly.js.

        Args:
            output_path: Chemin du fichier HTML à sauvegarder (optionnel).

        Returns:
            Code HTML complet sous forme de chaîne de caractères.
        """
        plotly_renderer = PlotlyRenderer(self.result)
        fig = plotly_renderer.build_figure(for_html=True)

        plotly_div = fig.to_html(full_html=False, include_plotlyjs='cdn', div_id='geocongo-3d-canvas')

        logo_b64 = _get_logo_b64()
        raw_title = self.result.metadata.get("title", "GeoCongo AI — Visualisation 3D Géologique")
        clean_title = raw_title.replace("🌍 ", "").replace("🌍", "").strip()

        meta = getattr(self.result, "metadata", {})
        elem = meta.get("element", "cu_pct").upper()
        n_points = meta.get("filtered_intervals", len(getattr(self.result, "points", [])))
        n_clusters = meta.get("cluster_count", len(getattr(self.result, "geometries", [])))
        stats = getattr(self.result, "statistics", {})
        max_grade = f"{stats.get('max', 0.0):.2f}%" if stats.get('max') is not None else "N/A"

        logo_html = f'<img src="{logo_b64}" class="logo-img" alt="GeoCongo AI Logo">' if logo_b64 else ""

        html_code = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{clean_title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }}
        body {{ background-color: #1e272e; color: #ffffff; overflow: hidden; height: 100vh; display: flex; flex-direction: column; }}
        header {{
            background: linear-gradient(135deg, #161e23 0%, #1e272e 100%);
            border-bottom: 1px solid #34495e;
            padding: 10px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 100;
        }}
        .brand-container {{ display: flex; align-items: center; gap: 14px; }}
        .logo-img {{ width: 38px; height: 38px; object-fit: contain; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.4)); }}
        .header-title {{ font-size: 1.15rem; font-weight: 700; color: #ffffff; letter-spacing: 0.3px; }}
        .header-badges {{ display: flex; align-items: center; gap: 10px; }}
        .badge {{
            background-color: rgba(44, 62, 80, 0.7);
            border: 1px solid #485460;
            padding: 5px 12px;
            border-radius: 6px;
            font-size: 0.82rem;
            font-weight: 600;
            color: #dcdde1;
        }}
        .badge-highlight {{ border-color: #91FCA3; color: #91FCA3; background-color: rgba(145, 252, 163, 0.1); }}
        .canvas-container {{ flex: 1; width: 100%; height: calc(100vh - 60px); position: relative; }}
        #geocongo-3d-canvas {{ width: 100%; height: 100%; }}
    </style>
</head>
<body>
    <header>
        <div class="brand-container">
            {logo_html}
            <h1 class="header-title"><b>{clean_title}</b></h1>
        </div>
        <div class="header-badges">
            <span class="badge">📊 Intervalles: <b>{n_points}</b></span>
            <span class="badge">💎 Gisements 3D: <b>{n_clusters}</b></span>
            <span class="badge badge-highlight">⚡ Max {elem}: <b>{max_grade}</b></span>
        </div>
    </header>
    <main class="canvas-container">
        <div style="height:100%; width:100%;">
            {plotly_div}
        </div>
    </main>
</body>
</html>"""

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_code)

        return html_code


