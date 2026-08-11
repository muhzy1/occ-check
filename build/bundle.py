#!/usr/bin/env python3
import os
import zipapp
import shutil

def build_artifact():
    build_dir = "/tmp/occ_build"
    output_file = "dist/occ-check"

    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs("dist", exist_ok=True)
    os.makedirs(build_dir)

    shutil.copytree("occ_check", os.path.join(build_dir, "occ_check"))
    
    with open(os.path.join(build_dir, "__main__.py"), "w") as f:
        f.write("import sys\n")
        f.write("from occ_check.cli import main\n")
        f.write("if __name__ == '__main__':\n")
        f.write("    main()\n")

    zipapp.create_archive(
        build_dir,
        target=output_file,
        interpreter="/usr/bin/env python3"
    )
    os.chmod(output_file, 0o755)
    print("[SUCCESS] Compiled single-file artifact created at: {}".format(output_file))

if __name__ == "__main__":
    build_artifact()
