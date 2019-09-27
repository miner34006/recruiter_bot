# -*- coding: utf-8 -*-

import time

from app import app, APPLICATION_PORT


if __name__ == '__main__':
    time.sleep(3)
    app.run(host='0.0.0.0', port=APPLICATION_PORT)
