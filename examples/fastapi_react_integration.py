"""Exemple d'intégration FastAPI et React pour GeoCongo AI v0.2.0.

Ce fichier montre comment exposer un endpoint FastAPI qui consomme
DrillholeDataset et renvoie le GeoResult au format JSON v1.0.
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from geocongoai import DrillholeDataset

app = FastAPI(title="GeoCongo AI - Geological Analysis API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/analysis/drillholes")
async def analyze_drillholes_api(
    collar_file: UploadFile = File(...),
    assay_file: UploadFile = File(...),
    element: str = Form("cu_pct"),
    grade_threshold: float = Form(0.5),
    eps: float = Form(25.0),
    min_samples: int = Form(3)
):
    """Endpoint recevant deux fichiers CSV (colliers et analyses), effectuant le clustering 3D DBSCAN
    et renvoyant le GeoResult JSON v1.0 directement exploitable par React / Three.js / Plotly.js.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        collar_path = os.path.join(tmp_dir, "collars.csv")
        assay_path = os.path.join(tmp_dir, "assays.csv")

        with open(collar_path, "wb") as f:
            f.write(await collar_file.read())
        with open(assay_path, "wb") as f:
            f.write(await assay_file.read())

        try:
            # 1. Chargement unifié du Dataset
            dataset = DrillholeDataset.from_csv(collar_path=collar_path, assay_path=assay_path)
            
            # 2. Exécution de l'analyse 3D
            geo_result = dataset.analyze(
                method="dbscan",
                element=element,
                grade_threshold=grade_threshold,
                eps=eps,
                min_samples=min_samples
            )

            # 3. Retour du contrat JSON v1.0
            return geo_result.to_dict()

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
