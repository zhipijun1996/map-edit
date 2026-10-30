from .revision060_content_v1 import decode as legacy_hq
from .revision061_content_v2 import decode as spec02

def decode(doc):return legacy_hq(doc)if'plains-hq'in doc['id']else spec02(doc)
