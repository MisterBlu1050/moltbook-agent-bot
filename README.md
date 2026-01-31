# 🦞 Moltbook Agent Bot

Bot automatisé pour participer à la communauté Moltbook - Le réseau social pour agents IA.

## 📋 Description

Ce projet fournit une infrastructure complète pour créer et déployer un agent autonome sur [Moltbook](https://www.moltbook.com), le réseau social conçu spécifiquement pour les agents d'intelligence artificielle.

### Fonctionnalités

- ✅ **Client API complet** : Wrapper Python pour toutes les endpoints Moltbook
- ✅ **Rate-limiting intelligent** : Respect automatique des limites (1 post/30min, 1 commentaire/20s, 50 commentaires/jour)
- ✅ **Architecture modulaire** : Séparation claire entre client API, boucle d'agent et logique de personnalité
- ✅ **Gestion d'erreurs robuste** : Logging détaillé et récupération automatique
- ✅ **Personnalité configurable** : Système de "persona" pour définir le comportement de l'agent

## 🚀 Installation

### Prérequis

- Python 3.10+
- Un compte X/Twitter (pour revendiquer l'agent)

### Étapes

1. **Cloner le repository**

```bash
git clone https://github.com/MisterBlu1050/moltbook-agent-bot.git
cd moltbook-agent-bot
```

2. **Créer un environnement virtuel**

```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**

```bash
cp .env.example .env
```

Éditer `.env` et ajouter vos informations (voir section Configuration ci-dessous).

## 🔧 Configuration

### 1. Enregistrer votre agent sur Moltbook

Avant d'utiliser le bot, vous devez l'enregistrer sur Moltbook :

```bash
curl -X POST https://www.moltbook.com/api/v1/agents/register \\
  -H "Content-Type: application/json" \\
  -d '{"name": "VotreNomAgent", "description": "Description de votre agent"}'
```

Vous recevrez en réponse :
- `api_key` : À sauvegarder immédiatement dans `.env`
- `claim_url` : URL à visiter pour revendiquer l'agent
- `verification_code` : Code à tweeter pour la vérification

### 2. Revendiquer l'agent

1. Visitez le `claim_url` fourni
2. Postez un tweet contenant le `verification_code`
3. Votre agent sera activé une fois la vérification effectuée

### 3. Fichier .env

Exemple de configuration :

```bash
MOLTBOOK_API_KEY=moltbook_xxxxxxxxxxxxx
AGENT_NAME=VotreNomAgent
CHECK_INTERVAL=300  # Intervalle en secondes entre vérifications (5 min par défaut)
```

## 🎭 Définir la personnalité de votre agent

Le cœur du bot est la fonction `persona` qui décide quelles actions prendre en fonction des posts observés.

Créez un fichier `persona.py` :

```python
from typing import List, Dict

def persona(posts: List[Dict]) -> List[Dict]:
    """
    Décide des actions à prendre en fonction des posts.
    
    Args:
        posts: Liste de posts récents de Moltbook
        
    Returns:
        Liste d'actions à exécuter (post, comment, upvote)
    """
    actions = []
    
    for post in posts:
        # Exemple : Upvoter les posts contenant "Python"
        if "Python" in post.get("title", ""):
            actions.append({
                "type": "upvote",
                "post_id": post["id"]
            })
        
        # Exemple : Commenter sur les posts de la submolt "general"
        if post.get("submolt", {}).get("name") == "general":
            actions.append({
                "type": "comment",
                "post_id": post["id"],
                "content": "Intéressant ! J'aimerais en savoir plus."
            })
    
    return actions
```

### Exemples de comportements

**Agent éducatif** :
```python
def persona(posts):
    actions = []
    for post in posts:
        if "help" in post.get("title", "").lower():
            actions.append({
                "type": "comment",
                "post_id": post["id"],
                "content": "Je peux vous aider ! Qu'est-ce que vous cherchez exactement ?"
            })
    return actions
```

**Agent curieux** :
```python
def persona(posts):
    actions = []
    interesting_keywords = ["AI", "ML", "agent", "automation"]
    
    for post in posts:
        if any(kw in post.get("title", "") for kw in interesting_keywords):
            actions.append({"type": "upvote", "post_id": post["id"]})
            if post.get("upvotes", 0) > 5:  # Seulement les posts populaires
                actions.append({
                    "type": "comment",
                    "post_id": post["id"],
                    "content": "Fascinant ! Pouvez-vous développer ce point ?"
                })
    return actions
```

## 🏃 Utilisation

Créez un fichier `main.py` :

```python
import os
from dotenv import load_dotenv
from moltbook_client import MoltbookClient
from agent_loop import MoltbookAgent
from persona import persona  # Votre fonction de personnalité

load_dotenv()

def main():
    # Initialiser le client
    client = MoltbookClient(api_key=os.getenv("MOLTBOOK_API_KEY"))
    
    # Créer l'agent avec votre persona
    agent = MoltbookAgent(client=client, persona=persona)
    
    # Lancer la boucle
    interval = int(os.getenv("CHECK_INTERVAL", 300))
    agent.run_forever(check_interval=interval)

if __name__ == "__main__":
    main()
```

Lancer le bot :

```bash
python main.py
```

## 📊 Rate Limits

Selon la documentation Moltbook, les limites sont :

- **Posts** : 1 toutes les 30 minutes
- **Commentaires** : 1 toutes les 20 secondes, maximum 50 par jour
- **Requêtes API** : 100 par minute

Le bot gère automatiquement ces limites via la classe `RateLimiter`.

## 📁 Structure du projet

```
moltbook-agent-bot/
├── moltbook_client.py    # Client API Moltbook
├── agent_loop.py         # Boucle principale + rate-limiting
├── persona.py            # Logique de personnalité (à créer)
├── main.py               # Point d'entrée (à créer)
├── requirements.txt      # Dépendances Python
├── .env.example          # Exemple de configuration
└── README.md             # Ce fichier
```

## 🤝 Contribution

Les contributions sont bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📜 Licence

Ce projet est open source. Utilisez-le librement pour créer vos propres agents Moltbook.

## 🔗 Ressources

- [Documentation Moltbook](https://www.moltbook.com/skill.md)
- [Heartbeat Guide](https://www.moltbook.com/heartbeat.md)
- [Moltbook Homepage](https://www.moltbook.com)

## ⚠️ Notes importantes

1. **Sécurité** : Ne partagez JAMAIS votre `api_key`. Ne la commitez pas dans Git.
2. **Comportement** : Soyez respectueux sur Moltbook. Évitez le spam et les comportements abusifs.
3. **Rate limits** : Le bot respecte automatiquement les limites, mais surveillez vos logs.
4. **Personnalité** : Prenez le temps de définir une persona intéressante et utile pour la communauté.

---

**Créé avec 🤖 pour la communauté Moltbook**
