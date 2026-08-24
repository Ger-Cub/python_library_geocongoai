"""Exemple d'utilisation minimal de `geocongoai.ia.prithvi.PrithviClient`.

Note: terratorch et torch doivent être installés et configurés.
"""
from geocongoai.ia.prithvi import PrithviClient


def main():
    client = PrithviClient(model_name="prithvi_eo_v2_300", pretrained=True)
    print("Loading model (this may download or raise if terratorch not installed)...")
    try:
        client.load_model()
    except Exception as e:
        print("Model load failed:", e)
        return

    # Remplacez par le chemin vers votre TIF
    tif_path = "path/to/sample.tif"
    try:
        res = client.extract_deep_features(tif_path)
        print("Features keys:", res.keys())
    except Exception as e:
        print("Inference failed:", e)


if __name__ == "__main__":
    main()
