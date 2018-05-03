# -*- encoding: utf-8 -*-
from __future__ import absolute_import

import config

from .esipy_observers import token_update_observer
from lazyblacksmith.extension.cache import cache

from esipy import EsiApp
from esipy import EsiClient
from esipy import EsiSecurity
from esipy.cache import BaseCache
from esipy.events import AFTER_TOKEN_REFRESH
from requests.adapters import HTTPAdapter


class LbCache(BaseCache):
    """ Custom BaseCache implementation for Lazyblacksmith
        used in esipy, to use the flask cache
    """

    def set(self, key, value, timeout=300):
        cache.set(key, value, timeout)

    def get(self, key, default=None):
        cached = cache.get(key)
        return cached if cached is not None else default

    def invalidate(self, key):
        cache.delete(key)


lbcache = LbCache()

transport_adapter = HTTPAdapter(
    pool_connections=20,
    pool_maxsize=300,
)

# ESI objects to be imported
esiapp = EsiApp.create(cache=lbcache, cache_time=0, datasource=config.ESI_DATASOURCE)
esisecurity = EsiSecurity(
    app=esiapp.get_latest_swagger,
    redirect_uri="%s%s" % (
        config.ESI_REDIRECT_DOMAIN, '/sso/callback',
    ),
    client_id=config.ESI_CLIENT_ID,
    secret_key=config.ESI_SECRET_KEY,
)
esiclient = EsiClient(
    security=esisecurity,
    transport_adapter=transport_adapter,
    cache=lbcache,
    headers={'User-Agent': config.ESI_USER_AGENT}
)

# register observers
AFTER_TOKEN_REFRESH.add_receiver(token_update_observer)
