from pathlib import Path
script = Path('stegotool/modules/module3_pixel_selector/generate_labels_robust.py').resolve()
p = script.parents[3] / 'data' / 'dev_images'
print('lookup_path =', p)
print('exists =', p.exists())
print('files =', [f.name for f in p.glob('*.*')])
