#!/usr/bin/env python
# manage.py

import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Nuk mund te importohet Django. "
            "A e ke instaluar? A e ke aktivizuar virtual environment-in?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
