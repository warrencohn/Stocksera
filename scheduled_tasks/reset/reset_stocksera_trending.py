import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
from helpers import connect_mysql_database

cnx, engine = connect_mysql_database()
cur = cnx.cursor()


def main():
    """
    Reset Stocksera trending table in database
    """
    cur.execute("SELECT * FROM stocksera_trending ORDER BY count DESC LIMIT 10")
    top_10 = cur.fetchall()

    cur.execute("DELETE FROM stocksera_trending")

    count = 20
    for row in top_10:
        row = list(row)
        row[2] = count
        print(row)
        cur.execute("INSERT IGNORE INTO stocksera_trending VALUES (%s, %s, %s)", tuple(row))
        cnx.commit()
        count -= 1


if __name__ == '__main__':
    main()
