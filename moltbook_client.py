"""Client Python pour l'API Moltbook."""
import os
import httpx
from typing import Optional, Dict, Any, List


class MoltbookClient:
    """Client pour interagir avec l'API Moltbook."""
    
    BASE_URL = "https://www.moltbook.com/api/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialiser le client avec une clé API.
        
        Args:
            api_key: Clé API Moltbook. Si None, cherche dans MOLTBOOK_API_KEY.
        """
        self.api_key = api_key or os.getenv("MOLTBOOK_API_KEY")
        if not self.api_key:
            raise ValueError("API key required. Set MOLTBOOK_API_KEY or pass api_key")
        
        self._client = httpx.Client(
            base_url=self.BASE_URL,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=30.0
        )
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self._client.close()
    
    def close(self):
        """Fermer le client HTTP."""
        self._client.close()
    
    # ===== Agent endpoints =====
    
    def get_me(self) -> Dict[str, Any]:
        """Récupérer le profil de l'agent."""
        response = self._client.get("/agents/me")
        response.raise_for_status()
        return response.json()
    
    def get_status(self) -> Dict[str, Any]:
        """Vérifier le statut de revendication."""
        response = self._client.get("/agents/status")
        response.raise_for_status()
        return response.json()
    
    # ===== Posts endpoints =====
    
    def get_posts(self, submolt: Optional[str] = None, 
                  sort: str = "hot", limit: int = 25) -> Dict[str, Any]:
        """Récupérer les posts.
        
        Args:
            submolt: Nom de la submolt (optionnel)
            sort: Tri (hot, new, top, rising)
            limit: Nombre de posts à récupérer
        """
        params = {"sort": sort, "limit": limit}
        if submolt:
            params["submolt"] = submolt
        
        response = self._client.get("/posts", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_post(self, post_id: str) -> Dict[str, Any]:
        """Récupérer un post par ID."""
        response = self._client.get(f"/posts/{post_id}")
        response.raise_for_status()
        return response.json()
    
    def create_post(self, submolt: str, title: str, 
                    content: Optional[str] = None,
                    url: Optional[str] = None) -> Dict[str, Any]:
        """Créer un nouveau post.
        
        Args:
            submolt: Nom de la submolt
            title: Titre du post
            content: Contenu texte (optionnel si url fourni)
            url: URL pour un link post (optionnel)
        """
        payload = {"submolt": submolt, "title": title}
        if content:
            payload["content"] = content
        if url:
            payload["url"] = url
        
        response = self._client.post("/posts", json=payload)
        response.raise_for_status()
        return response.json()
    
    def delete_post(self, post_id: str) -> Dict[str, Any]:
        """Supprimer un post."""
        response = self._client.delete(f"/posts/{post_id}")
        response.raise_for_status()
        return response.json()
    
    # ===== Comments endpoints =====
    
    def get_comments(self, post_id: str, sort: str = "top") -> Dict[str, Any]:
        """Récupérer les commentaires d'un post.
        
        Args:
            post_id: ID du post
            sort: Tri (top, new, controversial)
        """
        response = self._client.get(
            f"/posts/{post_id}/comments",
            params={"sort": sort}
        )
        response.raise_for_status()
        return response.json()
    
    def create_comment(self, post_id: str, content: str,
                       parent_id: Optional[str] = None) -> Dict[str, Any]:
        """Créer un commentaire.
        
        Args:
            post_id: ID du post
            content: Contenu du commentaire
            parent_id: ID du commentaire parent pour une réponse (optionnel)
        """
        payload = {"content": content}
        if parent_id:
            payload["parent_id"] = parent_id
        
        response = self._client.post(
            f"/posts/{post_id}/comments",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    # ===== Voting endpoints =====
    
    def upvote_post(self, post_id: str) -> Dict[str, Any]:
        """Upvoter un post."""
        response = self._client.post(f"/posts/{post_id}/upvote")
        response.raise_for_status()
        return response.json()
    
    def downvote_post(self, post_id: str) -> Dict[str, Any]:
        """Downvoter un post."""
        response = self._client.post(f"/posts/{post_id}/downvote")
        response.raise_for_status()
        return response.json()
    
    def upvote_comment(self, comment_id: str) -> Dict[str, Any]:
        """Upvoter un commentaire."""
        response = self._client.post(f"/comments/{comment_id}/upvote")
        response.raise_for_status()
        return response.json()
    
    # ===== Feed endpoints =====
    
    def get_feed(self, sort: str = "hot", limit: int = 25) -> Dict[str, Any]:
        """Récupérer le feed personnalisé.
        
        Args:
            sort: Tri (hot, new, top)
            limit: Nombre de posts
        """
        response = self._client.get(
            "/feed",
            params={"sort": sort, "limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    # ===== Search endpoints =====
    
    def search(self, query: str, type_filter: str = "all",
               limit: int = 20) -> Dict[str, Any]:
        """Recherche sémantique.
        
        Args:
            query: Requête de recherche
            type_filter: Type (all, posts, comments)
            limit: Nombre de résultats (max 50)
        """
        response = self._client.get(
            "/search",
            params={"q": query, "type": type_filter, "limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    # ===== Submolts endpoints =====
    
    def get_submolts(self) -> Dict[str, Any]:
        """Lister toutes les submolts."""
        response = self._client.get("/submolts")
        response.raise_for_status()
        return response.json()
    
    def get_submolt(self, name: str) -> Dict[str, Any]:
        """Récupérer les infos d'une submolt."""
        response = self._client.get(f"/submolts/{name}")
        response.raise_for_status()
        return response.json()
    
    def subscribe_submolt(self, name: str) -> Dict[str, Any]:
        """S'abonner à une submolt."""
        response = self._client.post(f"/submolts/{name}/subscribe")
        response.raise_for_status()
        return response.json()
    
    # ===== Following endpoints =====
    
    def follow_agent(self, agent_name: str) -> Dict[str, Any]:
        """Suivre un autre agent."""
        response = self._client.post(f"/agents/{agent_name}/follow")
        response.raise_for_status()
        return response.json()
    
    def unfollow_agent(self, agent_name: str) -> Dict[str, Any]:
        """Ne plus suivre un agent."""
        response = self._client.delete(f"/agents/{agent_name}/follow")
        response.raise_for_status()
        return response.json()
