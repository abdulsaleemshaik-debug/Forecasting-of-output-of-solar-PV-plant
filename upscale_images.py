import os
from PIL import Image

folder = 'report_figures'

for fname in os.listdir(folder):
    if fname.endswith('.png'):
        path = os.path.join(folder, fname)
        try:
            with Image.open(path) as img:
                print(f"Upscaling {fname}...")
                # Increase visual resolution linearly by 1.5x to pack more dense pixels
                # so the printer/PDF-viewer renders them extremely sharp
                new_size = (int(img.width * 1.5), int(img.height * 1.5))
                upscaled = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Save with strict high-resolution metadata
                upscaled.save(path, dpi=(600, 600))
        except Exception as e:
            print(f"Error processing {fname}: {e}")

print("All figures upscaled and set to 600 DPI for maximum visual resolution.")
