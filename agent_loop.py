"""Boucle principale de l'agent Moltbook avec rate-limiting."""
import time
import logging
from typing import Dict, Any, List, Callable
from moltbook_client import MoltbookClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RateLimiter:
    """Gestion du rate-limiting selon les règles Moltbook."""
    
    def __init__(self):
        self.last_post_time = 0.0
        self.comment_times: List[float] = []
        self.POST_COOLDOWN = 30 * 60  # 30 minutes
        self.COMMENT_COOLDOWN = 20  # 20 secondes
        self.DAILY_COMMENT_LIMIT = 50
    
    def can_post(self) -> bool:
        """Vérifier si on peut poster."""
        return time.time() - self.last_post_time >= self.POST_COOLDOWN
    
    def can_comment(self) -> bool:
        """Vérifier si on peut commenter."""
        now = time.time()
        
        # Nettoyer les anciens timestamps (> 24h)
        self.comment_times = [t for t in self.comment_times if now - t < 86400]
        
        # Vérifier limite quotidienne
        if len(self.comment_times) >= self.DAILY_COMMENT_LIMIT:
            return False
        
        # Vérifier cooldown
        if self.comment_times and (now - self.comment_times[-1]) < self.COMMENT_COOLDOWN:
            return False
        
        return True
    
    def record_post(self):
        """Enregistrer un post."""
        self.last_post_time = time.time()
    
    def record_comment(self):
        """Enregistrer un commentaire."""
        self.comment_times.append(time.time())
    
    def time_until_post(self) -> float:
        """Temps d'attente avant le prochain post (en secondes)."""
        elapsed = time.time() - self.last_post_time
        remaining = max(0, self.POST_COOLDOWN - elapsed)
        return remaining
    
    def time_until_comment(self) -> float:
        """Temps d'attente avant le prochain commentaire (en secondes)."""
        if not self.comment_times:
            return 0
        elapsed = time.time() - self.comment_times[-1]
        remaining = max(0, self.COMMENT_COOLDOWN - elapsed)
        return remaining


class MoltbookAgent:
    """Agent Moltbook avec boucle de participation."""
    
    def __init__(self, client: MoltbookClient, persona: Callable[[List[Dict]], List[Dict]]):
        """Initialiser l'agent.
        
        Args:
            client: Client API Moltbook
            persona: Fonction de décision (posts -> actions)
        """
        self.client = client
        self.persona = persona
        self.rate_limiter = RateLimiter()
    
    def tick(self) -> Dict[str, Any]:
        """Exécuter une itération de l'agent.
        
        Returns:
            Statistiques de l'itération
        """
        stats = {
            "posts_created": 0,
            "comments_created": 0,
            "upvotes": 0,
            "errors": 0
        }
        
        try:
            # Récupérer le feed
            logger.info("Fetching posts...")
            response = self.client.get_posts(sort="new", limit=20)
            posts = response.get("posts", [])
            
            if not posts:
                logger.info("No posts found")
                return stats
            
            # Décider des actions via la persona
            logger.info(f"Processing {len(posts)} posts...")
            actions = self.persona(posts)
            
            # Exécuter les actions respect rate-limits
            for action in actions:
                try:
                    action_type = action.get("type")
                    
                    if action_type == "post" and self.rate_limiter.can_post():
                        logger.info(f"Creating post: {action.get('title')}")
                        self.client.create_post(
                            submolt=action["submolt"],
                            title=action["title"],
                            content=action.get("content"),
                            url=action.get("url")
                        )
                        self.rate_limiter.record_post()
                        stats["posts_created"] += 1
                    
                    elif action_type == "comment" and self.rate_limiter.can_comment():
                        logger.info(f"Commenting on post {action.get('post_id')}")
                        self.client.create_comment(
                            post_id=action["post_id"],
                            content=action["content"],
                            parent_id=action.get("parent_id")
                        )
                        self.rate_limiter.record_comment()
                        stats["comments_created"] += 1
                    
                    elif action_type == "upvote":
                        logger.info(f"Upvoting post {action.get('post_id')}")
                        self.client.upvote_post(action["post_id"])
                        stats["upvotes"] += 1
                    
                    # Petit délai entre actions
                    time.sleep(2)
                
                except Exception as e:
                    logger.error(f"Error executing action {action_type}: {e}")
                    stats["errors"] += 1
        
        except Exception as e:
            logger.error(f"Error in tick: {e}")
            stats["errors"] += 1
        
        return stats
    
    def run_forever(self, check_interval: int = 300):
        """Exécuter l'agent en boucle continue.
        
        Args:
            check_interval: Intervalle entre vérifications (en secondes)
        """
        logger.info("Starting agent loop...")
        
        while True:
            try:
                logger.info("=" * 50)
                logger.info("Starting new tick")
                
                stats = self.tick()
                
                logger.info(f"Tick complete: {stats}")
                logger.info(f"Next post available in: {self.rate_limiter.time_until_post():.0f}s")
                logger.info(f"Next comment available in: {self.rate_limiter.time_until_comment():.0f}s")
                
                # Attendre avant la prochaine itération
                logger.info(f"Waiting {check_interval}s until next tick...")
                time.sleep(check_interval)
            
            except KeyboardInterrupt:
                logger.info("Agent stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                time.sleep(60)  # Attendre 1 min en cas d'erreur
