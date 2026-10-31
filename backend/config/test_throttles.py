from django.core.cache import cache
from django.test import RequestFactory, SimpleTestCase

from accounts.models import User

from .throttles import AnonRouteThrottle, AuthRouteThrottle


class RouteThrottleTests(SimpleTestCase):
    def setUp(self):
        cache.clear()
        self.request = RequestFactory().post("/")
        self.request.auth = User(pk=1, username="lea")

    def test_each_route_counts_on_its_own(self):
        hourly = AuthRouteThrottle("verification", "3/h")
        other = AuthRouteThrottle("mot-de-passe", "10/m")
        for _ in range(5):
            self.assertTrue(other.allow_request(self.request))

        self.assertTrue(all(hourly.allow_request(self.request) for _ in range(3)))
        self.assertFalse(hourly.allow_request(self.request))

    def test_a_minute_limit_does_not_clear_an_hourly_history(self):
        visitor = RequestFactory().post("/")  # sans compte : limité par adresse IP
        hourly = AnonRouteThrottle("inscription", "2/h")
        minute = AnonRouteThrottle("connexion", "10/m")
        hourly.allow_request(visitor)
        hourly.allow_request(visitor)
        minute.allow_request(visitor)

        self.assertFalse(hourly.allow_request(visitor))
