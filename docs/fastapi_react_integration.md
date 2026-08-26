# Guide d'Intégration FastAPI & React (GeoCongo AI v0.2.0)

Ce document explique comment connecter le moteur d'analyse Python `geocongoai` à votre backend FastAPI et votre frontend web React.

---

## 1. Backend FastAPI

Le backend reçoit les fichiers de forages (CSV/DataFrames) et renvoie l'objet universel `GeoResult` sérialisé via `result.to_dict()`.

```python
# main.py
from fastapi import FastAPI, UploadFile, File, Form
from geocongoai import DrillholeDataset

app = FastAPI()

@app.post("/api/v1/analysis/drillholes")
async def analyze_drillholes(
    collar_file: UploadFile = File(...),
    assay_file: UploadFile = File(...)
):
    dataset = DrillholeDataset.from_csv(collar_file.file, assay_file.file)
    result = dataset.analyze(method="dbscan", element="Cu", grade_threshold=0.5)
    
    # Renvoie le dictionnaire conforme au standard GeoCongo JSON v1.0
    return result.to_dict()
```

---

## 2. Frontend React (Exemple Plotly.js / Three.js)

Le composant React consomme le contrat `GeoCongoResult` JSON sans exécuter de calculs lourds :

```tsx
// Geology3DViewer.tsx
import React, { useEffect, useState } from 'react';
import Plot from 'react-plotly.js';

interface GeoCongoResult {
  metadata: { element: string; cluster_count: number };
  points: Array<{ x: number; y: number; z: number; Cu: number; cluster: number }>;
  geometries: Array<{
    vertices: { x: number[]; y: number[]; z: number[] };
    simplices: { i: number[]; j: number[]; k: number[] };
  }>;
}

export const Geology3DViewer: React.FC<{ data: GeoCongoResult }> = ({ data }) => {
  // Traitement direct des points et maillages 3D
  const pointTrace = {
    type: 'scatter3d',
    mode: 'markers',
    x: data.points.map(p => p.x),
    y: data.points.map(p => p.y),
    z: data.points.map(p => p.z),
    marker: {
      size: 5,
      color: data.points.map(p => p.Cu),
      colorscale: 'Viridis'
    }
  };

  const meshTraces = data.geometries.map((g, idx) => ({
    type: 'mesh3d',
    x: g.vertices.x,
    y: g.vertices.y,
    z: g.vertices.z,
    i: g.simplices.i,
    j: g.simplices.j,
    k: g.simplices.k,
    opacity: 0.4,
    color: '#e74c3c'
  }));

  return (
    <Plot
      data={[pointTrace, ...meshTraces]}
      layout={{
        title: 'Modèle 3D GeoCongo AI',
        paper_bgcolor: '#1e272e',
        plot_bgcolor: '#1e272e',
        scene: { aspectmode: 'data' }
      }}
    />
  );
};
```
