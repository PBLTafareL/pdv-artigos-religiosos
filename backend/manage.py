#!/usr/bin/env python
import os, sys
def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flor_dende.settings.prod')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Ative o venv: venv\\Scripts\\activate") from exc
    execute_from_command_line(sys.argv)
if __name__ == '__main__':
    main()
