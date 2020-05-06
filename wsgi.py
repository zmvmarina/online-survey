
from online_survey.application import application as app
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
        if len(sys.argv) > 2:
            debug = sys.argv[2].lower() == "debug"
        else:
            debug = False
    else:
        port = 5000
        debug = False
    app.config['DEBUG'] = debug
    app.run(port=port)
