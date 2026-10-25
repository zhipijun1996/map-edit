from pcg.prototype.creative_batches.grapple.delivery_v1 import do_reuse,SELECTED
if __name__=='__main__':
 do_reuse('workshop-creative-grapple-reuse-v3',[r[0]for r in SELECTED[:4]])
 do_reuse('workshop-creative-grapple-reuse-v4',[SELECTED[4][0]])
