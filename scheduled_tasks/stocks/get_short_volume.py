import io
import os
import sys
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from helpers import connect_mysql_database
import scheduled_tasks.reddit.stocks.fast_yahoo as fast_yahoo

cnx, engine = connect_mysql_database()
cur = cnx.cursor()


current_date = datetime.utcnow().date()


def get_30d_data_finra():
    """
    Get short volume data from https://cdn.finra.org/ in the last 30 days
    """
    last_date = datetime.utcnow().date() - timedelta(days=30)
    combined_df = pd.DataFrame(columns=["Date", "Symbol", "ShortVolume", "ShortExemptVolume", "TotalVolume", "%Shorted"])
    while current_date >= last_date:
        print("Looking at " + str(last_date))
        url = r"https://cdn.finra.org/equity/regsho/daily/CNMSshvol{}.txt".format(str(last_date).replace("-", ""))
        s = requests.get(url).content
        df = pd.read_csv(io.StringIO(s.decode('utf-8')), delimiter="|")

        if len(df) == 1:
            print("No data for " + str(last_date) + "\n")
        else:
            del df["Market"]
            df["%Shorted"] = 100 * (df["ShortVolume"] / df["TotalVolume"])
            df["%Shorted"] = df["%Shorted"].round(2)
            combined_df = combined_df.append(df)
        last_date = last_date + timedelta(days=1)

    combined_df["Date"] = combined_df["Date"].astype(str)
    combined_df["Date"] = combined_df["Date"].apply(lambda x: x[0:4] + "-" + x[4:6] + "-" + x[6:])
    combined_df.columns = ["Date", "Ticker", "Short Vol", "Short Exempt Vol", "Total Vol", "% Shorted"]
    combined_df = combined_df[~combined_df["% Shorted"].isna()]
    print(combined_df)

    start = 0
    while start < len(combined_df):
        print(start)
        cur.executemany("INSERT IGNORE INTO short_volume VALUES (%s, %s, %s, %s, %s, %s)",
                        combined_df[start:start + 50000].values.tolist())
        cnx.commit()
        start += 50000


def get_daily_data_finra(date_to_process: datetime.date = datetime.utcnow().date()-timedelta(days=0)):
    """
    Get short volume data from https://cdn.finra.org/
    """
    url = r"https://cdn.finra.org/equity/regsho/daily/CNMSshvol{}.txt".format(str(date_to_process).replace("-", ""))
    print(url)
    s = requests.get(url).content
    df = pd.read_csv(io.StringIO(s.decode('utf-8')), delimiter="|")
    if len(df) == 1:
        print("No data for " + str(date_to_process) + "\n")
    else:
        df["Date"] = df["Date"].astype(str).apply(lambda x: x[0:4] + "-" + x[4:6] + "-" + x[6:])
        df["%Shorted"] = 100 * (df["ShortVolume"] / df["TotalVolume"])
        df["%Shorted"] = df["%Shorted"].round(2)

        del df["Market"]
        df = df[~df["%Shorted"].isna()]

        cur.executemany("INSERT IGNORE INTO short_volume VALUES (%s, %s, %s, %s, %s, %s)", df.values.tolist())
        cnx.commit()

        highest_shorted = df[df["ShortVolume"] >= 3000000].nlargest(50, "%Shorted")
        del highest_shorted["Date"]
        highest_shorted.index = np.arange(1, len(highest_shorted) + 1)
        highest_shorted.reset_index(inplace=True)
        highest_shorted.rename(columns={"index": "Rank",
                                        "ShortVolume": "Short Volume",
                                        "ShortExemptVolume": "Short Exempt Vol",
                                        "TotalVolume": "Total Volume",
                                        "%Shorted": "% Shorted"}, inplace=True)

        quick_stats = {'regularMarketPreviousClose': 'Previous Close',
                       'regularMarketChangePercent': '1 Day Change %',
                       'marketCap': 'Market Cap'}
        stats_df = fast_yahoo.download_quick_stats(highest_shorted["Symbol"].to_list(), quick_stats)

        highest_shorted = pd.merge(highest_shorted, stats_df, on="Symbol")
        highest_shorted.replace(np.nan, "N/A", inplace=True)
        highest_shorted.rename(columns={"Symbol": "Ticker"}, inplace=True)
        highest_shorted.to_sql("highest_short_volume", engine, if_exists="replace", index=False)


def main():
    get_30d_data_finra()
    # get_daily_data_finra()


if __name__ == '__main__':
    main()
