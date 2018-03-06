#!/usr/bin/env python
from __future__ import unicode_literals

import atexit
import os
import shutil
import sys

import django


def pytest_configure():
    """
    Hack the ``project_template`` dir included with Mezzanine into
    an actual project to test against.

    Based on mezzanine.bin.runtests.
    """
    from mezzanine.utils.importing import path_for_import
    package_path = path_for_import("mezzanine")
    project_path = os.path.join(package_path, "project_template")

    os.environ["DJANGO_SETTINGS_MODULE"] = "project_name.test_settings"

    project_app_path = os.path.join(project_path, "project_name")

    local_settings_path = os.path.join(project_app_path, "local_settings.py")
    test_settings_path = os.path.join(project_app_path, "test_settings.py")

    sys.path.insert(0, package_path)
    sys.path.insert(0, project_path)

    if not os.path.exists(test_settings_path):
        shutil.copy(local_settings_path + ".template", test_settings_path)
        with open(test_settings_path, "r") as f:
            local_settings = f.read()
        with open(test_settings_path, "w") as f:
            test_settings = """
from . import settings
globals().update(i for i in settings.__dict__.items() if i[0].isupper())
if "surveys" not in settings.INSTALLED_APPS:
    INSTALLED_APPS = list(settings.INSTALLED_APPS) + ["surveys"]
# Use the MD5 password hasher by default for quicker test runs.
PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',)
"""
            f.write(test_settings + local_settings)

        def cleanup_test_settings():
            import os  # Outer scope sometimes unavailable in atexit functions.
            for fn in [test_settings_path, test_settings_path + 'c']:
                try:
                    os.remove(fn)
                except OSError:
                    pass
        atexit.register(cleanup_test_settings)

    django.setup()
