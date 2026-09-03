# 🤖 Prompt pour l'Agent Gemini — Mise à jour du SDK Python `geocongoai` (GEOCONGOAI_API_KEY)

> **Instructions pour l'utilisateur :** Copiez l'intégralité du texte ci-dessous et collez-le à l'agent Gemini dans le projet du SDK Python (`geocongoai`).

---

```markdown
Bonjour Gemini ! 

Dans le cadre du projet **GeoCongo AI**, nous avons mis en place une nouvelle méthode d'authentification pour le SDK Python via des **Clés API personnelles** (`GEOCONGOAI_API_KEY`), remplaçant l'utilisation de l'identifiant interne `user_id` (UUID Supabase).

Merci d'effectuer les modifications suivantes dans la base de code du SDK Python `geocongoai` :

---

### 🎯 Objectifs de la mise à jour

1. **Prise en charge de `GEOCONGOAI_API_KEY`** :
   - Autoriser la clé via l'argument `api_key` du constructeur `GeoCongoClient(api_key="gcg_live_...")`.
   - Si `api_key` n'est pas transmis, la lire automatiquement depuis la variable d'environnement `os.getenv("GEOCONGOAI_API_KEY")`.
   - Si ni `api_key` ni `user_id` ne sont fournis, lever une exception explicite avec un message d'aide pour obtenir une clé sur le dashboard Web.

2. **Injection des Headers HTTP** :
   - Pour chaque requête HTTP vers les Edge Functions Supabase (`/rag-agent`, `/search-geological`, `/search-documents`), inclure les headers :
     ```python
     headers = {
         "Content-Type": "application/json",
         "Authorization": f"Bearer {self.api_key}",
         "x-geocongo-api-key": self.api_key
     }
     ```

3. **Suppression de l'obligation de `user_id` dans les payloads** :
   - Dans `ask_rag(query, conversation_id=...)`, ne plus exiger `user_id`. Le payload doit simplement contenir `{"query": query, ...}`. L'Edge Function résout désormais automatiquement l'identité de l'utilisateur à partir du header `x-geocongo-api-key`.
   - Maintenir la rétrocompatibilité si l'ancien `user_id` est passé sans `api_key`.

4. **Documentation & Exemples (`README.md` et docstrings)** :
   - Mettre à jour le fichier `README.md` avec le nouveau snippet d'initialisation :
     ```python
     import os
     from geocongoai import GeoCongoClient

     # Recommandé : via variable d'environnement
     os.environ["GEOCONGOAI_API_KEY"] = "gcg_live_votre_cle_api"
     client = GeoCongoClient()

     # Poser une question à l'Agent RAG
     response = client.ask_rag("Quels sont les gisements connus de cobalt au Lualaba ?")
     print(response.answer)
     ```

---

### 💻 Exemple de modification attendue dans `geocongoai/client.py` (ou fichier équivalent)

```python
import os
import requests
from typing import Optional, Dict, Any, List

class GeoCongoClient:
    """
    Client Python officiel pour l'écosystème GeoCongo AI.
    """
    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        supabase_url: Optional[str] = None,
        supabase_anon_key: Optional[str] = None,
        user_id: Optional[str] = None,  # conservé pour rétrocompatibilité
    ):
        # 1. Résolution de la clé API
        self.api_key = api_key or os.getenv("GEOCONGOAI_API_KEY")
        self._user_id = user_id
        
        if not self.api_key and not self._user_id:
            raise ValueError(
                "Authentification requise : Veuillez fournir api_key='gcg_live_...' "
                "ou définir la variable d'environnement GEOCONGOAI_API_KEY.\n"
                "Vous pouvez générer une clé d'accès dans votre espace membre GeoCongo AI : "
                "https://www.geocongoai.com/api-keys"
            )

        self._supabase_url = (supabase_url or os.getenv("SUPABASE_URL", "https://votre-projet.supabase.co")).rstrip("/")
        self._base_url = f"{self._supabase_url}/functions/v1"

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["x-geocongo-api-key"] = self.api_key
        return headers

    def ask_rag(self, query: str, conversation_id: Optional[str] = None, language: str = "fr") -> Any:
        url = f"{self._base_url}/rag-agent"
        payload = {
            "query": query,
            "language": language
        }
        if conversation_id:
            payload["conversationId"] = conversation_id
        
        # En mode legacy (sans API key), injecter le user_id dans le body
        if not self.api_key and self._user_id:
            payload["userId"] = self._user_id

        response = requests.post(url, json=payload, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def search_geological(self, query: str, type: str = "all", **filters) -> List[Dict[str, Any]]:
        url = f"{self._base_url}/search-geological"
        payload = {"query": query, "type": type, "filters": filters}
        response = requests.post(url, json=payload, headers=self._get_headers())
        response.raise_for_status()
        return response.json().get("results", [])

    def search_documents(self, query: str, **filters) -> List[Dict[str, Any]]:
        url = f"{self._base_url}/search-documents"
        payload = {"query": query, "filters": filters}
        response = requests.post(url, json=payload, headers=self._get_headers())
        response.raise_for_status()
        return response.json().get("results", [])
```

---

Merci de vérifier que toutes les fonctions d'appel API restent parfaitement fonctionnelles et de lancer les tests unitaires / linter du SDK si disponible !

```
