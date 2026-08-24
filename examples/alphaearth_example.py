"""Exemple d'utilisation de `AlphaEarthClient` pour extraire des échantillons GEE.

Assurez-vous d'avoir configuré l'authentification Earth Engine avant l'exécution.
"""
from geocongoai.ia.alphaearth import AlphaEarthClient


def main():
    client = AlphaEarthClient()
    try:
        client.authenticate()
    except Exception as e:
        print("GEE auth failed:", e)
        return

    # Exemple: créer une petite géométrie (GeoJSON-like) ou utiliser ee.Geometry
    # Ici on suppose que l'utilisateur utilisera ee.Geometry sur place.
    import ee
    geom = ee.Geometry.Point([29.5, -2.55]).buffer(1000)

    res = client.extract_embeddings(geometry=geom, start_date="2022-01-01", end_date="2022-12-31")
    if "error" in res:
        print("Sampling error:", res["error"])
    else:
        print(f"Extracted {res['count']} samples; bands={res['bands']}")


if __name__ == "__main__":
    main()
