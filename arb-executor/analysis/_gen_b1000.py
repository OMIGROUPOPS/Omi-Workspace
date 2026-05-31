import numpy as np, pickle
from blend_continuous import CENTS
from _v15_validate import get_draws
DR={}
for c in CENTS:
    d,npos=get_draws(c,1000,seed=13)
    DR[c]=(None if d is None else d.tolist(), npos)
    pickle.dump(DR, open('/tmp/v15_draws_b1000.pkl','wb'))  # incremental
print("DONE B=1000", len(DR))
open('/tmp/b1000_done.flag','w').write('done')
