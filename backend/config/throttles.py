"""Limites de débit, chacune propre à sa route.

Django Ninja range l'historique d'une limite sous « throttle_<scope>_<identifiant> », et
le scope vaut « anon » ou « auth » quelle que soit la route : sans scope propre, toutes
les routes partageraient un compteur, et une limite à la minute effacerait l'historique
d'une limite à l'heure.
"""

from ninja.throttling import AnonRateThrottle, AuthRateThrottle


class AnonRouteThrottle(AnonRateThrottle):
    """Par adresse IP, pour une route."""

    def __init__(self, scope, rate):
        self.scope = f"anon-{scope}"
        super().__init__(rate)


class AuthRouteThrottle(AuthRateThrottle):
    """Par compte connecté (ou par adresse IP à défaut), pour une route."""

    def __init__(self, scope, rate):
        self.scope = f"auth-{scope}"
        super().__init__(rate)
