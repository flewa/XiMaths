"""Crée une paire de clés VAPID pour le Web Push, à copier dans .env ou .env.prod.

Changer de clés invalide les abonnements existants : chaque membre réactive alors les
notifications sur ses appareils.
"""

import base64

from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from django.core.management.base import BaseCommand
from py_vapid import Vapid02


def b64url(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


class Command(BaseCommand):
    help = "Crée une paire de clés VAPID (Web Push)."

    def handle(self, *args, **options):
        vapid = Vapid02()
        vapid.generate_keys()
        private = vapid.private_key.private_numbers().private_value.to_bytes(32, "big")
        public = vapid.public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
        self.stdout.write(f"VAPID_PUBLIC_KEY={b64url(public)}")
        self.stdout.write(f"VAPID_PRIVATE_KEY={b64url(private)}")
