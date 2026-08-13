#!/usr/bin/env python3
import os
import shutil
import zipapp

def build():
    dist_dir = "dist"
    target_pyz = os.path.join(dist_dir, "occ-check.pyz")
    
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)

    print("Building dist/occ-check.pyz...")
    zipapp.create_archive(
        source="lib/occ",
        target=target_pyz,
        interpreter="/usr/bin/env python3",
        main="cli:main"
    )
    
    os.chmod(target_pyz, 0o755)
    print(f"Bundle built successfully: {target_pyz}")

if __name__ == "__main__":
    build()
