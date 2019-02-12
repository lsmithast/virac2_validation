#!/usr/bin/env python

import numpy as np
import sqlutilpy

"""
Do make sure this script has restrictive permissions so as not to leave your
login details visible to all. In fact, Sergey has the following suggestions:
Instead of setting login details in here
1) People should be using .pgpass
2) and/or PGHOST/PGDATBASE environment variables
see:
https://www.postgresql.org/docs/9.6/libpq-pgpass.html
https://www.postgresql.org/docs/9.6/libpq-envars.html
"""

def connect():
    return sqlutilpy.getConnection(
        db='wsdb',
        driver="psycopg2",
        host='', # db hostname
        user='', # db username here
        password='') # db password here


def getsql(sql, conn=connect()):
    return sqlutilpy.get(sql, conn=conn, asDict=True)
