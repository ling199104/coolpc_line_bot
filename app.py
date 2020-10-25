from controllers.line_bot import *
from os import environ


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=environ['PORT'])
