import sys, os
INTERP = os.path.join(os.environ['HOME'], 'http://5l4ck.cmyr.net', 'flask_env', 'bin', 'python')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())
sys.path.append('debtbot')
from debtbot.slask import app as application

# Uncomment next two lines to enable debugging
# from werkzeug.debug import DebuggedApplication
# application = DebuggedApplication(application, evalex=True)
