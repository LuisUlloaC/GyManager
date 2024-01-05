import os
import sys
import django
from django.core.management import execute_from_command_line

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from control.main import start_app  # noqa: E402

base_dir = os.path.dirname(__file__).replace("\\", "/")
assets_path = os.path.join(base_dir+"/", "views/ui/")

if __name__ == "__main__" and len(sys.argv) > 1:
    if not sys.stdout:
        app = start_app(assets_path, debug=1)
        app.dev.show()
        execute_from_command_line(sys.argv)
        app.dev.exec()
        sys.exit(app.exec_())
    else:
        execute_from_command_line(sys.argv)
        sys.exit()

start_app(assets_path)
