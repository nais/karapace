#!/usr/bin/env python3

import os
import time
import subprocess
import venv

TEST_DIR = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))


def main():
    env_builder = venv.EnvBuilder(upgrade=True, with_pip=True)
    venv_dir = os.path.join(TEST_DIR, "venv")
    env_builder.create(venv_dir)
    subprocess.check_call([os.path.join(venv_dir, "bin", "pip"), "install", "wheel"])
    subprocess.check_call([os.path.join(venv_dir, "bin", "pip"), "install", "requests", "requests-toolbelt", "pytest", "pytest-sugar"])
    with subprocess.Popen(["kubectl", "--context=dev-gcp", "--namespace=aura", "port-forward", "svc/karapace-test", "8080:80"]) as pf:
        try:
            time.sleep(5)
            return subprocess.call([os.path.join(venv_dir, "bin", "pytest")])
        finally:
            pf.terminate()


if __name__ == '__main__':
    import sys
    sys.exit(main())
