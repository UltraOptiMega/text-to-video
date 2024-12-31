#!/usr/bin/env python

import socket
socket.setdefaulttimeout(120)

from src import create_app

app = create_app()


app.run(host='0.0.0.0', debug=True, port=8000)
