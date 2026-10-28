class RuleError(ValueError):
    """Une règle métier refuse l'action : déjà relu, déjà voté, mauvais statut…

    L'API la renvoie en 409 avec le message, qui s'adresse à l'utilisateur.
    """
