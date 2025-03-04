import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from finvizfinance.insider import Insider

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
from scheduled_tasks.reddit.stocks.fast_yahoo import download_quick_stats
from helpers import connect_mysql_database

cnx, engine = connect_mysql_database()
cur = cnx.cursor()


def check_date(value, last_date):
    if value > last_date:
        value = value - timedelta(days=365)
    return value


def latest_insider_trading():
    """
    Get recent insider trading data from Finviz
    """
    for type_trading in ["buys", "sales"]:
        print("latest {}".format(type_trading))
        finsider = Insider(option="latest {}".format(type_trading))
        insider_trader = finsider.get_insider()

        insider_trader["Owner"] = insider_trader["Owner"].str.title()
        insider_trader = insider_trader[insider_trader["Value ($)"] >= 50000]

        insider_trader["Date"] = insider_trader["Date"] + " 2022"
        insider_trader["Date"] = pd.to_datetime(insider_trader["Date"], format="%b %d %Y", errors='coerce')
        # insider_trader["Date"] = insider_trader["Date"].astype(str)

        insider_trader["SEC Form 4"] = insider_trader["SEC Form 4"].apply(lambda x: x.rsplit(' ', 2)[0])
        insider_trader["SEC Form 4"] = insider_trader["SEC Form 4"] + " 2022"
        insider_trader["SEC Form 4"] = pd.to_datetime(insider_trader["SEC Form 4"], format="%b %d %Y", errors='coerce')
        # insider_trader["SEC Form 4"] = insider_trader["SEC Form 4"].astype(str)

        if type_trading == "sales":
            insider_trader["Value ($)"] = -insider_trader["Value ($)"]

        # print(insider_trader)
        last_date = datetime.utcnow().date()

        insider_trader["Date"] = insider_trader["Date"].apply(lambda x: check_date(x, last_date))
        insider_trader["SEC Form 4"] = insider_trader["SEC Form 4"].apply(lambda x: check_date(x, last_date))
        insider_trader["Date"] = insider_trader["Date"].astype(str)
        insider_trader["SEC Form 4"] = insider_trader["SEC Form 4"].astype(str)
        print(insider_trader)

        for index, row in insider_trader.iterrows():
            cur.execute("INSERT IGNORE INTO latest_insider_trading VALUES "
                        "(%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s, %s)", tuple(row))
            cnx.commit()


def latest_insider_trading_analysis():
    last_date = str(datetime.utcnow().date() - timedelta(days=30))

    insider_df = pd.read_sql_query("SELECT * FROM latest_insider_trading", engine)
    insider_df = insider_df.drop_duplicates(subset=["Ticker", "TransactionDate", "Cost", "Shares", "Value",
                                                    "DateFilled"], keep='first')
    insider_df = insider_df[insider_df["DateFilled"] > last_date]
    insider_df = pd.DataFrame(insider_df.groupby(["Ticker"])['Value'].agg('sum'))

    insider_df = insider_df.reindex(insider_df["Value"].abs().sort_values(ascending=False).index).head(50)
    insider_df.reset_index(inplace=True)
    insider_df.rename(columns={"Value": "Amount"}, inplace=True)

    quick_stats = {'marketCap': 'MktCap'}
    quick_stats_df = download_quick_stats(insider_df["Ticker"].to_list(), quick_stats, threads=True).reset_index()
    quick_stats_df = quick_stats_df[quick_stats_df["MktCap"] != "N/A"]
    quick_stats_df.rename(columns={"Symbol": "Ticker"}, inplace=True)

    insider_df = insider_df.merge(quick_stats_df, on="Ticker")
    insider_df["Proportion"] = (insider_df["Amount"].abs() / insider_df["MktCap"]) * 100
    insider_df["Proportion"] = insider_df["Proportion"].astype(float).round(3)
    insider_df.to_sql("latest_insider_trading_analysis", engine, if_exists="replace", index=False)


def main():
    latest_insider_trading()
    latest_insider_trading_analysis()


if __name__ == '__main__':
    main()
