"""Connect reserved empty cells without adding colliders or sealing Port faces."""
from collections import deque


def connect(cells,ports,budget=64):
    original=set(cells);cells=set(cells)
    forbidden={tuple(p['grid']['cell'][i]+p['normal'][i]for i in range(2))for p in ports.values()}
    if cells&forbidden:raise ValueError('port_neighbor_already_reserved')
    xmin=min(x for x,y in cells)-1;xmax=max(x for x,y in cells)+1
    ymin=min(y for x,y in cells)-1;ymax=max(y for x,y in cells)+1
    def component():
        seen={min(cells)};front=list(seen)
        for x,y in front:
            for q in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
                if q in cells and q not in seen:seen.add(q);front.append(q)
        return seen
    while True:
        own=component();other=cells-own
        if not other:return cells,sorted(map(list,cells-original))
        queue=deque(sorted(own));parents={p:None for p in own};found=None
        while queue:
            x,y=queue.popleft()
            if (x,y)in other:found=(x,y);break
            for q in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
                if q in parents or q in forbidden or not xmin<=q[0]<=xmax or not ymin<=q[1]<=ymax:continue
                parents[q]=(x,y);queue.append(q)
        if found is None:raise ValueError('cannot_connect_reservation_without_sealing_port')
        while found is not None:cells.add(found);found=parents[found]
        if len(cells-original)>budget:raise ValueError('empty_reservation_connection_budget_exceeded')
