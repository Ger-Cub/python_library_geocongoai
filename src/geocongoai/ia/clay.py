"""Client pour le Modèle Fondation Géospatial Clay (ClayMAE & TorchGeo Embeddings).

Ce module permet d'interagir avec le modèle open-source Clay (Clay v1.5 / v1.0)
pour l'extraction et la visualisation d'embeddings géospatiaux.

Il privilégie les options légères et optimisées :
1. Intégration TorchGeo / Hugging Face pour l'extraction à la volée.
2. Chargement d'embeddings précalculés au format GeoParquet (Source Cooperative) sans calcul local.
3. Réduction de dimension PCA (3 composantes RGB) pour cartographier directement les motifs spatiaux.
"""
import os
from typing import Any, Dict, List, Optional, Tuple, Union


# ---------------------------------------------------------------------------
# Utilitaires internes
# ---------------------------------------------------------------------------

def _require(package: str, pip_extra: str = "") -> Any:
    """Importe un paquet et lève une ImportError claire si absent."""
    import importlib
    try:
        return importlib.import_module(package)
    except ImportError as exc:
        hint = pip_extra or package
        raise ImportError(
            f"Le paquet '{package}' est requis. Installez-le via : pip install {hint}"
        ) from exc


# ---------------------------------------------------------------------------
# ClayEmbeddingDataset  (wrapper léger autour des embeddings précalculés)
# ---------------------------------------------------------------------------

class ClayEmbeddingDataset:
    """Wrapper autour des embeddings Clay précalculés (GeoParquet / Parquet).

    Permet de charger, filtrer spatialement et accéder aux vecteurs d'embeddings
    publiés sur Source Cooperative sans aucun calcul GPU.

    Example::

        ds = ClayEmbeddingDataset.from_source_cooperative(
            "https://source.coop/clay/clay-model-v0-embeddings/kivu_2023.parquet"
        )
        vectors = ds.embedding_matrix()   # numpy (N, D)
    """

    def __init__(self, dataframe: Any, embedding_cols: Optional[List[str]] = None) -> None:
        self._df = dataframe
        self._embedding_cols = embedding_cols

    # ------------------------------------------------------------------
    # Constructeurs alternatifs
    # ------------------------------------------------------------------

    @classmethod
    def from_file(cls, path_or_url: str) -> "ClayEmbeddingDataset":
        """Charge depuis un fichier GeoParquet / Parquet local ou URL."""
        try:
            gpd = _require("geopandas")
            df = gpd.read_parquet(path_or_url)
        except Exception:
            pd = _require("pandas")
            df = pd.read_parquet(path_or_url)
        return cls(df)

    @classmethod
    def from_source_cooperative(cls, url: str) -> "ClayEmbeddingDataset":
        """Charge les embeddings directement depuis Source Cooperative.

        Args:
            url: URL vers le fichier GeoParquet Clay (ex: Source Cooperative).
        """
        return cls.from_file(url)

    # ------------------------------------------------------------------
    # Accès aux données
    # ------------------------------------------------------------------

    @property
    def dataframe(self) -> Any:
        """GeoDataFrame / DataFrame sous-jacent."""
        return self._df

    def embedding_matrix(self) -> Any:
        """Retourne la matrice d'embeddings (N, D) sous forme NumPy."""
        np = _require("numpy")
        df = self._df

        # Détecte automatiquement les colonnes d'embedding
        if self._embedding_cols:
            cols = self._embedding_cols
        else:
            # Cherche une colonne 'embedding' ou colonnes numériques
            if "embedding" in df.columns:
                raw = df["embedding"].tolist()
                return np.array(raw)
            # Colonnes de type float/int (hors geometry, dates, etc.)
            num_cols = [
                c for c in df.columns
                if df[c].dtype.kind in ("f", "i", "u")
                and c not in ("lon", "lat", "x", "y", "year", "month")
            ]
            cols = num_cols

        return df[cols].to_numpy(dtype=np.float32)

    def filter_by_bbox(
        self,
        minx: float, miny: float,
        maxx: float, maxy: float,
        crs: str = "EPSG:4326",
    ) -> "ClayEmbeddingDataset":
        """Filtre spatialement par bounding box (requiert geopandas)."""
        gpd = _require("geopandas")
        shapely = _require("shapely")
        from shapely.geometry import box  # type: ignore
        aoi = box(minx, miny, maxx, maxy)
        gdf = self._df
        if not hasattr(gdf, "geometry"):
            raise ValueError("Le dataframe ne contient pas de colonne 'geometry'.")
        gdf_projected = gdf.to_crs(crs) if hasattr(gdf, "to_crs") else gdf
        mask = gdf_projected.geometry.intersects(aoi)
        return ClayEmbeddingDataset(gdf_projected[mask].copy(), self._embedding_cols)

    def __len__(self) -> int:
        return len(self._df)

    def __repr__(self) -> str:
        return f"ClayEmbeddingDataset(n={len(self)}, cols={list(self._df.columns)[:6]}...)"


# ---------------------------------------------------------------------------
# ClayClient  –  client principal
# ---------------------------------------------------------------------------

class ClayClient:
    """Client complet pour le Foundation Model Clay.

    Trois voies d'utilisation (de la plus légère à la plus lourde) :

    **Voie 1 – Embeddings précalculés (sans GPU)** ::

        client = ClayClient()
        ds = client.load_precomputed_embeddings(
            "https://source.coop/clay/.../kivu.parquet"
        )
        pca_result = client.apply_pca(ds.embedding_matrix())

    **Voie 2 – TorchGeo natif (GPU optionnel)** ::

        client = ClayClient(use_torchgeo=True)
        client.load_model()                   # téléchargement mis en cache HF
        result = client.extract_embeddings(image_tensor)

    **Voie 3 – Carte spatiale RGB depuis GeoTIFF** ::

        result = client.generate_spatial_pca_map("sentinel2.tif", "output_rgb.tif")
    """

    #: Modèles TorchGeo supportés pour Clay / fondation géospatiale
    TORCHGEO_MODELS: Dict[str, str] = {
        "dofa": "dofa_base_patch16_224",
        "resnet18": "resnet18",
        "vit_small": "vit_small_patch16_224",
    }

    def __init__(
        self,
        model_name: str = "made-with-clay/Clay",
        checkpoint_path: Optional[str] = None,
        device: Optional[str] = None,
        use_torchgeo: bool = True,
        torchgeo_backbone: str = "dofa",
    ) -> None:
        """Initialise le client Clay.

        Args:
            model_name: Repo Hugging Face ou identifiant local.
            checkpoint_path: Chemin vers un fichier .ckpt / .safetensors.
            device: ``'cuda'``, ``'cpu'`` ou ``None`` pour auto-détection.
            use_torchgeo: Utiliser TorchGeo comme backend principal (recommandé).
            torchgeo_backbone: Backbone TorchGeo parmi ``'dofa'``, ``'resnet18'``.
        """
        self.model_name = model_name
        self.checkpoint_path = checkpoint_path
        self.device = device
        self.use_torchgeo = use_torchgeo
        self.torchgeo_backbone = torchgeo_backbone
        self.model = None
        self._device: Optional[str] = None
        self._wavelengths: Optional[List[float]] = None  # Pour DOFA

    # ------------------------------------------------------------------
    # Chargement du modèle
    # ------------------------------------------------------------------

    def load_model(
        self,
        repo_id: Optional[str] = None,
        filename: str = "clay-v1.5.ckpt",
        wavelengths: Optional[List[float]] = None,
    ) -> None:
        """Charge le modèle Clay (TorchGeo ou HuggingFace Hub).

        **TorchGeo** (voie recommandée, poids mis en cache automatiquement) :
        Charge DOFA (ViT-B/16 entraîné sur EO) ou ResNet18 (SSL4EO).

        **HuggingFace Hub** (fallback) :
        Télécharge ``clay-v1.5.ckpt`` depuis ``made-with-clay/Clay``.

        Args:
            repo_id: Identifiant HuggingFace (défaut : ``self.model_name``).
            filename: Nom du fichier checkpoint.
            wavelengths: Longueurs d'onde centrales des bandes (pour DOFA).
                Ex Sentinel-2 RGB : ``[0.49, 0.56, 0.66]``.
        """
        torch = _require("torch")
        self._device = self.device or ("cuda" if torch.cuda.is_available() else "cpu")
        self._wavelengths = wavelengths or [0.49, 0.56, 0.66]  # Sentinel-2 B2/B3/B4

        # --- Voie 1 : TorchGeo natif ---
        if self.use_torchgeo:
            try:
                from torchgeo.models import (  # type: ignore
                    DOFABase16_Weights,
                    ResNet18_Weights,
                    get_model,
                )

                backbone_key = self.torchgeo_backbone.lower()
                if backbone_key == "dofa":
                    self.model = get_model(
                        "dofa_base_patch16_224",
                        weights=DOFABase16_Weights.DOFA_MAE,
                    )
                elif backbone_key == "resnet18":
                    self.model = get_model(
                        "resnet18",
                        weights=ResNet18_Weights.SENTINEL2_RGB_MOCO,
                    )
                else:
                    self.model = get_model(backbone_key)

                self.model = self.model.eval().to(self._device)
                self._backend = "torchgeo"
                return

            except ImportError:
                pass  # TorchGeo non installé → fallback HuggingFace
            except Exception:
                pass  # Autre erreur → fallback

        # --- Voie 2 : HuggingFace Hub ---
        if self.checkpoint_path and os.path.exists(self.checkpoint_path):
            ckpt_file = self.checkpoint_path
        else:
            try:
                from huggingface_hub import hf_hub_download  # type: ignore
                r_id = repo_id or self.model_name
                ckpt_file = hf_hub_download(repo_id=r_id, filename=filename)
            except Exception as exc:
                raise RuntimeError(
                    f"Impossible d'obtenir '{filename}' depuis HuggingFace. "
                    "Spécifiez `checkpoint_path` ou installez `huggingface_hub`."
                ) from exc

        state = torch.load(ckpt_file, map_location=self._device)
        self.model = state.get("state_dict", state)
        if hasattr(self.model, "eval"):
            self.model.eval()
        self.checkpoint_path = ckpt_file
        self._backend = "huggingface"

    # ------------------------------------------------------------------
    # Embeddings précalculés (sans GPU)
    # ------------------------------------------------------------------

    def load_precomputed_embeddings(self, source_url_or_path: str) -> ClayEmbeddingDataset:
        """Charge des embeddings Clay précalculés (GeoParquet).

        Aucun GPU requis. Les embeddings publiés sur Source Cooperative
        (``https://source.coop/clay/``) sont directement exploitables.

        Args:
            source_url_or_path: Chemin local ou URL vers un fichier GeoParquet.

        Returns:
            :class:`ClayEmbeddingDataset` prêt à l'emploi.
        """
        return ClayEmbeddingDataset.from_file(source_url_or_path)

    # ------------------------------------------------------------------
    # Extraction d'embeddings (modèle en mémoire)
    # ------------------------------------------------------------------

    def extract_embeddings(
        self,
        image_patch: Any,
        coords: Optional[Tuple[float, float]] = None,
        time_metadata: Optional[Any] = None,
        wavelengths: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Extrait le vecteur latent d'un patch d'image satellite.

        Le modèle est chargé automatiquement si nécessaire.

        Args:
            image_patch: Tenseur PyTorch ou NumPy ``(B, C, H, W)`` ou ``(C, H, W)``.
            coords: Tuple ``(lat, lon)`` optionnel.
            time_metadata: Timestamp ou jour de l'année optionnel.
            wavelengths: Longueurs d'onde centrales (pour DOFA).
                Défaut : ``[0.49, 0.56, 0.66]`` (Sentinel-2 RGB).

        Returns:
            Dict ``{'embeddings': ndarray, 'shape': tuple, 'model': str, 'backend': str}``.
        """
        if self.model is None:
            self.load_model()

        torch = _require("torch")
        np = _require("numpy")

        # --- Préparation du tenseur ---
        if isinstance(image_patch, np.ndarray):
            tensor = torch.from_numpy(image_patch).float()
        else:
            tensor = image_patch.float()

        if tensor.ndim == 3:
            tensor = tensor.unsqueeze(0)  # (1, C, H, W)

        # Redimensionne pour les modèles ViT qui attendent 224×224
        if getattr(self, "_backend", None) in ("torchgeo", None) and self.use_torchgeo:
            if tensor.shape[-1] != 224 or tensor.shape[-2] != 224:
                try:
                    import torch.nn.functional as F  # noqa
                    tensor = F.interpolate(tensor, size=(224, 224), mode="bilinear", align_corners=False)
                except Exception:
                    pass

        tensor = tensor.to(self._device)

        wl = wavelengths or self._wavelengths or [0.49, 0.56, 0.66]

        with torch.no_grad():
            model = self.model
            try:
                # DOFA (TorchGeo) : nécessite les longueurs d'onde
                if hasattr(model, "forward_features") and "dofa" in str(type(model)).lower():
                    out = model.forward_features(tensor, wavelengths=wl)
                elif hasattr(model, "forward_features"):
                    out = model.forward_features(tensor)
                    # Global average pooling si dimension spatiale restante
                    if out.ndim == 4:
                        out = out.mean(dim=(-2, -1))
                elif hasattr(model, "encoder"):
                    out = model.encoder(tensor, coords, time_metadata)
                elif callable(model):
                    out = model(tensor)
                else:
                    out = tensor  # passthrough si mock

                if hasattr(out, "detach"):
                    embeddings = out.detach().cpu().numpy()
                elif isinstance(out, (list, tuple)):
                    embeddings = np.concatenate(
                        [o.detach().cpu().numpy() if hasattr(o, "detach") else np.array(o) for o in out],
                        axis=-1,
                    )
                else:
                    embeddings = np.array(out)

            except Exception as exc:
                raise RuntimeError(f"Erreur lors de l'extraction d'embeddings : {exc}") from exc

        return {
            "embeddings": embeddings,
            "shape": embeddings.shape,
            "model": self.model_name,
            "backend": getattr(self, "_backend", "unknown"),
        }

    # ------------------------------------------------------------------
    # PCA
    # ------------------------------------------------------------------

    def apply_pca(
        self,
        embeddings: Any,
        n_components: int = 3,
        normalize: bool = True,
    ) -> Dict[str, Any]:
        """Réduit la dimensionnalité des embeddings vers N composantes.

        Les 3 premières composantes PCA peuvent être projetées comme image
        RGB ``[0, 255]`` pour cartographier directement les motifs spatiaux.
        Des zones de même couleur partagent des propriétés géologiques proches.

        Args:
            embeddings: Array NumPy ``(N, D)`` ou ``(H, W, D)``.
            n_components: Nombre de composantes (3 = RGB, 2 = scatter 2D).
            normalize: Normalise les composantes dans ``[0, 255]``.

        Returns:
            Dict avec ``pca_features``, ``normalized_components``,
            ``rgb_image`` (si entrée spatiale), ``explained_variance_ratio``.
        """
        np = _require("numpy")
        PCA = _require("sklearn.decomposition").PCA  # type: ignore

        arr = np.asarray(embeddings, dtype=np.float32)
        orig_shape = arr.shape

        if arr.ndim == 3:
            h, w, d = orig_shape
            flat = arr.reshape(-1, d)
        elif arr.ndim > 3:
            flat = arr.reshape(orig_shape[0], -1)
        else:
            flat = arr
            h, w = None, None

        pca = PCA(n_components=min(n_components, flat.shape[1], flat.shape[0]))
        reduced = pca.fit_transform(flat)

        if normalize:
            mn = reduced.min(axis=0, keepdims=True)
            mx = reduced.max(axis=0, keepdims=True)
            denom = np.where((mx - mn) == 0, 1e-6, mx - mn)
            norm = ((reduced - mn) / denom * 255.0).astype(np.uint8)
        else:
            norm = reduced

        rgb_image = None
        if arr.ndim == 3 and h is not None and w is not None:
            rgb_image = norm.reshape(h, w, pca.n_components_)

        return {
            "pca_features": reduced,
            "normalized_components": norm,
            "rgb_image": rgb_image,
            "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
            "n_components": pca.n_components_,
        }

    # ------------------------------------------------------------------
    # Similarité cosinus
    # ------------------------------------------------------------------

    def similarity_search(
        self,
        query_embedding: Any,
        candidate_embeddings: Any,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """Recherche les ``top_k`` patches les plus similaires (similarité cosinus).

        Args:
            query_embedding: Vecteur query ``(D,)`` ou ``(1, D)``.
            candidate_embeddings: Matrice candidates ``(N, D)``.
            top_k: Nombre de voisins à retourner.

        Returns:
            Dict ``{'indices': array, 'scores': array}`` triés par score décroissant.
        """
        np = _require("numpy")

        q = np.asarray(query_embedding, dtype=np.float32).flatten()
        C = np.asarray(candidate_embeddings, dtype=np.float32)

        # Normalisation L2
        q_norm = q / (np.linalg.norm(q) + 1e-9)
        C_norm = C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-9)

        scores = C_norm @ q_norm  # (N,)
        top_idx = np.argsort(scores)[::-1][:top_k]

        return {"indices": top_idx, "scores": scores[top_idx]}

    # ------------------------------------------------------------------
    # Clustering KMeans
    # ------------------------------------------------------------------

    def cluster_embeddings(
        self,
        embeddings: Any,
        n_clusters: int = 6,
        random_state: int = 42,
    ) -> Dict[str, Any]:
        """Segmente non-supervisée les patches en ``n_clusters`` groupes (KMeans).

        Utile pour découvrir automatiquement des classes de terrain (forêt,
        eau, mines, zones urbaines) sans annotation manuelle.

        Args:
            embeddings: Matrice ``(N, D)``.
            n_clusters: Nombre de clusters.
            random_state: Graine aléatoire pour la reproductibilité.

        Returns:
            Dict ``{'labels': array(N,), 'centroids': array(K, D), 'inertia': float}``.
        """
        np = _require("numpy")
        KMeans = _require("sklearn.cluster").KMeans  # type: ignore

        arr = np.asarray(embeddings, dtype=np.float32)
        km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init="auto")
        labels = km.fit_predict(arr)

        return {
            "labels": labels,
            "centroids": km.cluster_centers_,
            "inertia": float(km.inertia_),
            "n_clusters": n_clusters,
        }

    # ------------------------------------------------------------------
    # Carte spatiale PCA depuis GeoTIFF
    # ------------------------------------------------------------------

    def generate_spatial_pca_map(
        self,
        tif_path: str,
        output_rgb_tif: Optional[str] = None,
        n_components: int = 3,
        patch_size: int = 16,
        stride: int = 8,
    ) -> Dict[str, Any]:
        """Génère une carte spatiale RGB à partir des embeddings Clay + PCA.

        Découpe le GeoTIFF en patches, génère les embeddings pour chaque patch,
        reconstruit une grille spatiale et applique la PCA pour un rendu RGB.
        Optionnellement sauvegarde le résultat en GeoTIFF.

        Args:
            tif_path: GeoTIFF d'entrée (multi-bandes).
            output_rgb_tif: Chemin de sortie GeoTIFF RGB (optionnel).
            n_components: Nombre de composantes PCA.
            patch_size: Taille des patches en pixels.
            stride: Pas d'échantillonnage.

        Returns:
            Dict ``{'rgb_array', 'transform', 'crs', 'output_path', 'variance_explained'}``.
        """
        rasterio = _require("rasterio")
        np = _require("numpy")

        with rasterio.open(tif_path) as src:
            data = src.read().astype(np.float32)  # (C, H, W)
            profile = src.profile.copy()
            transform = src.transform
            crs = src.crs

        c, h, w = data.shape

        # Normalisation simple [0, 1]
        data_norm = data / (data.max() + 1e-9)

        # Extraction de patches avec stride
        patch_embeddings = []
        centers = []

        for row in range(0, h - patch_size + 1, stride):
            for col in range(0, w - patch_size + 1, stride):
                patch = data_norm[:, row:row + patch_size, col:col + patch_size]
                patch_tensor = patch[np.newaxis, ...]  # (1, C, ph, pw)

                if self.model is not None:
                    try:
                        res = self.extract_embeddings(patch_tensor)
                        emb = res["embeddings"].flatten()
                    except Exception:
                        emb = patch.mean(axis=(1, 2))  # fallback moyenne spectrale
                else:
                    emb = patch.mean(axis=(1, 2))

                patch_embeddings.append(emb)
                centers.append((row + patch_size // 2, col + patch_size // 2))

        all_embs = np.array(patch_embeddings, dtype=np.float32)  # (N_patches, D)

        # PCA vers N composantes
        pca_res = self.apply_pca(all_embs, n_components=n_components, normalize=True)
        pca_feats = pca_res["normalized_components"]  # (N_patches, 3)

        # Reconstruction image de sortie (interpolation)
        out_h = (h - patch_size) // stride + 1
        out_w = (w - patch_size) // stride + 1
        rgb_grid = pca_feats.reshape(out_h, out_w, n_components) if len(pca_feats) == out_h * out_w else None

        output_path = None
        if output_rgb_tif and rgb_grid is not None:
            # Rééchantillonne à la résolution originale
            try:
                import cv2  # type: ignore
                rgb_full = cv2.resize(rgb_grid.astype(np.uint8), (w, h), interpolation=cv2.INTER_LINEAR)
            except ImportError:
                from PIL import Image  # type: ignore
                img = Image.fromarray(rgb_grid.astype(np.uint8))
                rgb_full = np.array(img.resize((w, h), Image.BILINEAR))

            rgb_bands = np.transpose(rgb_full, (2, 0, 1))
            profile.update(count=n_components, dtype=rasterio.uint8)
            with rasterio.open(output_rgb_tif, "w", **profile) as dst:
                dst.write(rgb_bands)
            output_path = output_rgb_tif

        return {
            "rgb_array": rgb_grid,
            "transform": transform,
            "crs": crs,
            "output_path": output_path,
            "variance_explained": pca_res["explained_variance_ratio"],
            "n_patches": len(patch_embeddings),
        }

    # ------------------------------------------------------------------
    # Extraction complète TorchGeo (dataset structuré)
    # ------------------------------------------------------------------

    def embed_torchgeo_dataloader(
        self,
        dataloader: Any,
        wavelengths: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Extrait les embeddings pour tout un DataLoader TorchGeo.

        Chaque batch ``{'image': tensor}`` est passé dans le modèle (DOFA / ResNet18).
        Les embeddings sont accumulés et retournés avec les labels si disponibles.

        Args:
            dataloader: DataLoader TorchGeo (``batch['image']`` de forme ``(B, C, H, W)``).
            wavelengths: Longueurs d'onde centrales pour DOFA.

        Returns:
            Dict ``{'embeddings': ndarray(N, D), 'labels': ndarray|None}``.
        """
        if self.model is None:
            self.load_model(wavelengths=wavelengths)

        torch = _require("torch")
        np = _require("numpy")

        try:
            from tqdm import tqdm  # type: ignore
            iterator = tqdm(dataloader, desc="Extraction embeddings Clay")
        except ImportError:
            iterator = dataloader

        wl = wavelengths or self._wavelengths or [0.49, 0.56, 0.66]
        all_embs, all_labels = [], []

        for batch in iterator:
            x = batch["image"].to(self._device).float()
            y = batch.get("label", None)

            # Normalisation basique (scale Sentinel-2 DN → ~[0,1])
            if x.max() > 10.0:
                x = x / 10_000.0

            # Resize 224×224 si nécessaire
            if x.shape[-1] != 224 or x.shape[-2] != 224:
                try:
                    import torch.nn.functional as F  # noqa
                    x = F.interpolate(x, size=(224, 224), mode="bilinear", align_corners=False)
                except Exception:
                    pass

            with torch.no_grad():
                model = self.model
                if hasattr(model, "forward_features"):
                    try:
                        emb = model.forward_features(x, wavelengths=wl)
                    except TypeError:
                        emb = model.forward_features(x)
                    if emb.ndim == 4:
                        emb = emb.mean(dim=(-2, -1))
                else:
                    emb = model(x)

                all_embs.append(emb.cpu().numpy())
                if y is not None:
                    all_labels.append(y.numpy() if hasattr(y, "numpy") else np.array(y))

        return {
            "embeddings": np.concatenate(all_embs, axis=0),
            "labels": np.concatenate(all_labels, axis=0) if all_labels else None,
        }


__all__ = ["ClayClient", "ClayEmbeddingDataset"]
