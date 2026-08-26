"""Renderers de visualisation 3D interactifs basés sur Plotly.
"""
import os
import base64
from typing import Optional, Any

try:
    import plotly.graph_objects as go
except ImportError:
    go = None


def _get_logo_b64() -> str:
    """Récupère le logo officiel GeoCongo AI encodé en Data URI Base64."""
    assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    logo_path = os.path.join(assets_dir, "geocongoai_logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/png;base64,{encoded}"
    return ""


class PlotlyRenderer:
    """Générateur de scènes 3D interactives Plotly pour un GeoResult."""

    def __init__(self, result: Any):
        self.result = result

    def build_figure(self, title: Optional[str] = None, for_html: bool = False) -> Any:
        """Construit une instance de plotly.graph_objects.Figure."""
        if go is None:
            raise ImportError("plotly est requis pour générer des visualisations 3D. Installez plotly.")

        fig = go.Figure()
        raw_title = title or self.result.metadata.get("title", "GeoCongo AI — Visualisation 3D Géologique")
        clean_title = raw_title.replace("🌍 ", "").replace("🌍", "").strip()
        bold_title_html = f"<b>{clean_title}</b>"

        logo_b64 = _get_logo_b64()

        collars = getattr(self.result, "collars", [])
        points = getattr(self.result, "points", [])
        geometries = getattr(self.result, "geometries", [])
        element = self.result.metadata.get("element", "cu_pct")

        # 1. Trajectoires et forages (avec symboles carrés pour la légende)
        if collars:
            collar_dict = {c["hole_id"]: c for c in collars}
            for hole_id, c in collar_dict.items():
                pts = [p for p in points if p.get("hole_id") == hole_id]
                if not pts:
                    continue
                pts = sorted(pts, key=lambda item: item.get("mid_depth", 0))
                cx, cy, cz = float(c.get("x", 0)), float(c.get("y", 0)), float(c.get("z", 0))
                line_x = [cx] + [p["x"] for p in pts]
                line_y = [cy] + [p["y"] for p in pts]
                line_z = [cz] + [p["z"] for p in pts]

                fig.add_trace(go.Scatter3d(
                    x=line_x, y=line_y, z=line_z,
                    mode='lines+markers',
                    line=dict(color='#bdc3c7', width=4),
                    marker=dict(symbol='circle', size=3, color='#bdc3c7'),
                    name=f"Forage {hole_id}",
                    hoverinfo='text',
                    text=f"Forage: {hole_id}<br>Profondeur max: {pts[-1].get('mid_depth', 0):.1f}m"
                ))

        # 2. Analyses géochimiques (points colorés avec colorbar distincte)
        if points:
            px = [p["x"] for p in points]
            py = [p["y"] for p in points]
            pz = [p["z"] for p in points]
            p_grades = [float(p.get(element, 0.0)) if p.get(element) is not None else 0.0 for p in points]
            hover_texts = [
                f"Forage: {p.get('hole_id')}<br>Prof: {p.get('mid_depth', 0):.1f}m<br>{element.upper()}: {float(p.get(element, 0)):.2f}%<br>Cluster: {p.get('cluster', 'N/A')}"
                for p in points
            ]

            fig.add_trace(go.Scatter3d(
                x=px, y=py, z=pz,
                mode='markers',
                marker=dict(
                    symbol='circle',
                    size=6,
                    color=p_grades,
                    colorscale='Viridis',
                    colorbar=dict(
                        title=dict(text=f"<b>{element.upper()} (%)</b>", font=dict(color="#ffffff", size=13)),
                        x=1.02,
                        y=0.45,
                        len=0.65,
                        thickness=18,
                        tickfont=dict(color="#ffffff", size=11),
                        bgcolor="rgba(30, 39, 46, 0.5)",
                        bordercolor="#485460",
                        borderwidth=1
                    ),
                    opacity=0.9
                ),
                name="Analyses Géochimiques",
                text=hover_texts,
                hoverinfo='text'
            ))

        # 3. Enveloppes 3D (Convex Hulls / Meshes)
        colors = ['#e74c3c', '#e67e22', '#9b59b6', '#3498db', '#2ecc71', '#f1c40f']
        for idx, g in enumerate(geometries):
            color = colors[idx % len(colors)]
            vertices = g.get("vertices", {})
            simplices = g.get("simplices", {})
            cid = g.get("cluster_id", idx)
            vol = g.get("volume_m3", 0.0)

            if vertices and simplices:
                fig.add_trace(go.Mesh3d(
                    x=vertices.get("x", []),
                    y=vertices.get("y", []),
                    z=vertices.get("z", []),
                    i=simplices.get("i", []),
                    j=simplices.get("j", []),
                    k=simplices.get("k", []),
                    color=color,
                    opacity=0.45,
                    name=f"Gisement #{cid} (Vol: {vol:.0f}m³)",
                    showscale=False,
                    hoverinfo='name'
                ))

        # Configuration des images et du logo alignés parfaitement avec le titre
        layout_images = []
        if logo_b64 and not for_html:
            layout_images.append(dict(
                source=logo_b64,
                xref="paper", yref="paper",
                x=0.005, y=1.035,
                sizex=0.045, sizey=0.075,
                xanchor="left", yanchor="middle",
                layer="above"
            ))

        title_x_offset = 0.058 if logo_b64 else 0.01

        title_config = dict(
            text=bold_title_html,
            x=title_x_offset,
            y=0.965,
            xanchor='left',
            yanchor='top',
            font=dict(size=18, color='#ffffff', family='sans-serif')
        ) if not for_html else None

        margin_top = 10 if for_html else 65

        # Layout Sombre Professionnel GeoCongo AI avec Légende Séparée & Logo Alignés
        fig.update_layout(
            title=title_config,
            images=layout_images,
            paper_bgcolor='#1e272e',
            plot_bgcolor='#1e272e',
            # Légende isolée à gauche sous le titre pour éviter tout chevauchement avec la colorbar à droite
            legend=dict(
                x=0.01,
                y=0.88,
                xanchor="left",
                yanchor="top",
                orientation="v",
                bgcolor="rgba(24, 32, 42, 0.9)",
                bordercolor="#485460",
                borderwidth=1.5,
                font=dict(color="#ffffff", size=12, family="sans-serif"),
                itemsizing="constant",
                itemwidth=30,
                tracegroupgap=6,
                title=dict(text="<b>📌 LÉGENDE DES COUCHES</b>", font=dict(color="#91FCA3", size=11))
            ),
            scene=dict(
                xaxis=dict(
                    title=dict(text='<b>Est (X) [m]</b>', font=dict(color='#ffffff', size=12)),
                    backgroundcolor="#2c3e50",
                    gridcolor="#485460",
                    tickfont=dict(color='#ffffff')
                ),
                yaxis=dict(
                    title=dict(text='<b>Nord (Y) [m]</b>', font=dict(color='#ffffff', size=12)),
                    backgroundcolor="#2c3e50",
                    gridcolor="#485460",
                    tickfont=dict(color='#ffffff')
                ),
                zaxis=dict(
                    title=dict(text='<b>Élévation (Z) [m]</b>', font=dict(color='#ffffff', size=12)),
                    backgroundcolor="#2c3e50",
                    gridcolor="#485460",
                    tickfont=dict(color='#ffffff')
                ),
                aspectmode='data'
            ),
            margin=dict(l=10, r=10, b=10, t=margin_top)
        )

        return fig

    def show(self, title: Optional[str] = None, raw_figure: bool = False) -> Any:
        """Construit et affiche la visualisation dans un environnement interactif (Notebook).
        
        Par défaut, affiche la vue complète avec en-tête professionnel, logo et badges.
        Si raw_figure=True, retourne l'objet plotly.graph_objects.Figure brut.
        """
        if not raw_figure:
            try:
                from IPython.display import HTML
                from .html import HTMLRenderer
                html_renderer = HTMLRenderer(self.result)
                html_code = html_renderer.render()
                return HTML(html_code)
            except Exception:
                pass
        fig = self.build_figure(title=title)
        return fig

