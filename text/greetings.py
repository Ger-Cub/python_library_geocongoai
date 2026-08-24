"""Fonctions de salutations et présentation simples en français."""
from typing import Any

def saluer(nom: Any) -> str:
    """Retourne une salutation simple.

    Args:
        nom: nom ou identifiant de la personne/entité

    Returns:
        Message de salutation
    """
    return f"Bonjour, {nom} !"


def introduire(nom: Any, metier: str) -> str:
    """Retourne une introduction courte.

    Args:
        nom: nom de la personne
        metier: métier ou rôle
    """
    return f"Je m'appelle {nom} et je suis {metier}."


def dire_au_revoir(nom: Any) -> str:
    """Message d'au revoir simple."""
    return f"Au revoir, {nom} !"


__all__ = ["saluer", "introduire", "dire_au_revoir"]
