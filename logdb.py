#!/usr/bin/env python3
"""This module create a connection to the database 'news' and define some
   methods to select data in different tables, to create and drop views."""

import psycopg2


def connect():
    """return a database connection"""
    return psycopg2.connect(database="news")


def create_view(conn, query):
    """create a view
       conn : psycopg2 object
              A connection to a database
       query : str
               SQL query
    """
    with conn.cursor() as cursor:
        cursor.execute(query)


def drop_view(conn, view_name):
    """Drop a view"""
    with conn.cursor() as cursor:
        cursor.execute("DROP VIEW %s" % view_name)


def select(conn, query):
    """fetch data in the database and return it to be used later on"""
    with conn.cursor() as cursor:
        cursor.execute(query)
        data = cursor.fetchall()
    return data
