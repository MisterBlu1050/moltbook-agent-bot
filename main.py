#!/usr/bin/env python3
"""Point d'entrée principal pour lancer le bot Moltbook Mattanza."""

import sys
import logging
from agent_loop import run_agent
from persona import PERSONALITY, get_response_guidelines

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mattanza_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    logger.info("="*50)
    logger.info(f"Démarrage de {PERSONALITY['name']}")
    logger.info(f"Politique: {PERSONALITY['political_orientation']['ideology']}")
    logger.info(f"Style: {PERSONALITY['communication_style']['tone']}")
    logger.info("="*50)
    logger.info(get_response_guidelines())
    logger.info("="*50)
    
    try:
        run_agent()
    except KeyboardInterrupt:
        logger.info("\nArrêt du bot demandé")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Erreur: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
