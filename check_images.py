import os
from PIL import Image

for fname in os.listdir('report_figures'):
    if fname.endswith('.png'):
        path = os.path.join('report_figures', fname)
        try:
            with Image.open(path) as img:
                print(f"{fname}: {img.size} -- dpi: {img.info.get('dpi')}")
        except Exception as e:
            print(f"Error {fname}: {e}")
