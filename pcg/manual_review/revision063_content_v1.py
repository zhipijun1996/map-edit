from .revision062_content_v1 import decode as recent
from .revision058_content_v1 import decode as double
from .lift_idea_v1 import decode as lift
def decode(doc):
 if '31639' in doc['id']:return double(doc)
 if '96ba6' in doc['id']:return lift(doc)
 return recent(doc)
