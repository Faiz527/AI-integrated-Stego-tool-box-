from pathlib import Path
from PIL import Image
import numpy as np
from stegotool.modules.module3_pixel_selector.selector_baseline import select_pixels

img_dir = Path('stegotool/data/dev_images')
imgs = list(img_dir.glob('*.*'))
print('Images:', imgs)

for p in imgs:
    im = Image.open(p).convert('RGB')
    arr = np.array(im)
    h,w,_ = arr.shape
    print('\\n', p.name, 'size=', w,'x',h)

    ranked = select_pixels(arr, payload_bits=512, patch_size=5, lsb_bits=1)  # Increased from 256
    print('ranked length=', len(ranked))

    # Try forming groups of 64 (does not depend on ECC)
    group_size = 64
    top_groups = []
    for i in range(0, len(ranked), group_size):
        grp = ranked[i:i+group_size]
        if len(grp) == group_size:
            top_groups.append(grp)
    print('groups that can be formed:', len(top_groups))
