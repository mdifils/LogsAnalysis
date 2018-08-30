#!/usr/bin/env python3
"""This program make some SQL queries to fetch and analyse data in the news
database. Then print the result out."""

import logdb


# ---------- Creating some views to make queries more readable ----------------
# INNER JOIN between author table and articles one
AUTHOR_SLUG = """CREATE VIEW author_slug AS
                SELECT name, slug
                FROM authors, articles
                WHERE authors.id = articles.author;"""

# from log table I create a view of paths and how many views each of distinct
# path has. But I'm looking at paths to articles actually present in articles
# table which has a reference (foreign key) to author table. Notice that every
# path to an article has this general structure '/article/slug'. So I remove
# '/article/' and rename the column as slug.
SLUG_VIEWS = """CREATE VIEW slug_views AS
                SELECT substring(path from 10) AS slug, count(path) AS views
                FROM log
                GROUP BY path
                HAVING path IN (select '/article/' || slug from articles)
                ORDER BY views desc;"""

# From the timestamp with time zone, I focus only on the date in order to find
# the number of requests the server received every day.
REQUESTS_PER_DAY = """CREATE VIEW requests_per_day AS
                     SELECT time AS date, COUNT(time) AS requests
                     FROM (select time::date from log) as bydate
                     GROUP BY time;"""

# same thing as the previous query but just for the requests with errors.
ERRORS_PER_DAY = """CREATE VIEW errors_per_day AS
                    SELECT time AS date, COUNT(time) AS errors
                    FROM (select time::date from log
                          where status like '4%'
                             or status like '5%') as bydate
                    GROUP BY time;"""

# By doing an inner join between requests_per_day and errors_per_day, I create
# a view with the percentage (in % with 2 digit decimal) of errors for every
ERRORS_PERCENT = """CREATE VIEW errors_percent AS
                    SELECT errors_per_day.date,
                           round(errors*100/requests::numeric, 2) AS percent
                    FROM errors_per_day, requests_per_day
                    WHERE errors_per_day.date = requests_per_day.date;"""

# ----------------------- SELECT QUERIES --------------------------------------
# Only errors > 1% are selected
MOST_ERRORS = """SELECT TO_CHAR(date, 'FMDay FMMonth DD, YYYY') AS day, percent
                 FROM errors_percent
                 WHERE percent > 1
                 ORDER BY percent DESC;"""

# Selecting the first 3 popular articles
POPULAR_ARTICLE = """SELECT * FROM slug_views LIMIT 3;"""

# Selecting the most popular author
POPULAR_AUTHOR = """SELECT name, sum(views) AS total
                  FROM author_slug
                  JOIN slug_views ON slug_views.slug = author_slug.slug
                  GROUP BY name
                  ORDER BY total DESC;"""

# ---------------------- CONNECTING TO DATABASE -------------------------------

# Notice that I'm using the 'with' notation, meaning that psycopg2 will
# automatically close the connection and even commit the query if necessary
with logdb.connect() as connection:
    print("Connected to database")
    logdb.create_view(connection, AUTHOR_SLUG)
    logdb.create_view(connection, SLUG_VIEWS)
    logdb.create_view(connection, REQUESTS_PER_DAY)
    logdb.create_view(connection, ERRORS_PER_DAY)
    logdb.create_view(connection, ERRORS_PERCENT)
    TOP_ARTICLES = logdb.select(connection, POPULAR_ARTICLE)
    TOP_AUTHOR = logdb.select(connection, POPULAR_AUTHOR)
    MOST_ERRORS_DAY = logdb.select(connection, MOST_ERRORS)

# ------------------- PRINTING ANALYSIS RESULTS -------------------------------

print("\n\nHere are the most popular articles by views\n")
for index, data in enumerate(TOP_ARTICLES):
    print("{}: {} --- {} views".format(index+1, data[0], data[1]))

print("\n\nHere are the most popular authors\n")
for index, data in enumerate(TOP_AUTHOR):
    print("{}: {} --- {} views".format(index+1, data[0], data[1]))

print("\n\nHere is the days on which more \
than 1% of requests lead to errors\n")
for index, data in enumerate(MOST_ERRORS_DAY):
    print("{}: {} --- {}% errors".format(index+1, data[0], data[1]))

print("\n\n")

# ---------- DELETING VIEWS CREATED JUST FOR QUERIES READABILITY --------------

VIEWS = ["errors_percent", "errors_per_day",
         "requests_per_day", "slug_views", "author_slug"]
with logdb.connect() as connection:
    for table in VIEWS:
        logdb.drop_view(connection, table)
