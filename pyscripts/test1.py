from collections import OrderedDict
from sentinelsat import SentinelAPI

api = SentinelAPI('agarciabellan', '@Gar1983')

tiles = ['33VUC']

query_kwargs = {
        'platformname': 'Sentinel-2',
        'producttype': 'S2MSI1C',
        'date': ('NOW-3DAYS', 'NOW')}

products = OrderedDict()
for tile in tiles:
    kw = query_kwargs.copy()
    kw['tileid'] = tile
    pp = api.query(**kw)
    products.update(pp)

api.download_all(products)