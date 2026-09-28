import sys

project_home = "/home/SEU_USUARIO/Projeto-ava-heloina"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from app import app as application
