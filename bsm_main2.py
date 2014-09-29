#!/usr/bin/python
# -*- coding: utf-8 -*-


from bsm2 import BSM
import pandas as pd
import sys
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as bbp
import datetime as dt
from matplotlib import rc
rc('mathtext', default='regular')


def main():

    dir = "../"
    window = 120
    stock_file = dir + "stock_db_2014-09-29.csv"
    stock_fs_file = dir + "stock_db_stock_fs_data2014-09-21.csv"

    stock_df = pd.read_csv(stock_file)
    stock_fs_df = pd.read_csv(stock_fs_file)

    ccode = 9613#8267#9613#8263

    s_df = stock_df[stock_df["ccode"]==ccode].reset_index()
    s_df = s_df[-window:-1]
    fs_df = stock_fs_df[stock_fs_df["ccode"]==ccode].reset_index()

    issued_stock = float(fs_df["all_issued_stock"].loc[len(fs_df["all_issued_stock"])-1])
    dept = float(fs_df["dept_with_interest"].loc[len(fs_df["dept_with_interest"])-1])
    equity_value = pd.Series(s_df["close"] * issued_stock)


    r = 0.01 #国債利回りから推計
    T = 250 #daily

    b = BSM(equity_value,dept,r,T)

    b.optimize()

    retdf = pd.DataFrame({"th_asset":b._assets,
                          "asset":[float(fs_df["total_asset"].loc[len(fs_df["total_asset"])-1])]*len(b._assets),
                          "vola_a":[b._vola_a]*len(b._assets),
                          "mktcap":equity_value,
                          "date":[dt.datetime.strptime(date,"%Y-%m-%d %H:%M:%S") for date in s_df["date"]],
                          "dept":[b._dept]*len(b._assets),
                          "PD":b._pds
    })



    #print retdf

    """plot"""
    graph1 = "../" + str(ccode) + "_graph2.pdf"

    pp = bbp.PdfPages(graph1)

    font_option = {"size":8}
    plt.rc("font",**font_option)

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax2 = ax1.twinx()

    retdf.plot(ax=ax1,x="date",y="th_asset",label="ThAsset",style="b-")
    retdf.plot(ax=ax1,x="date",y="dept",label="Dept",style="g-")
    #retdf.plot(ax=ax1,x="date",y="mktcap",label="MktCap",style="r-")
    retdf.plot(ax=ax2,x="date",y="PD",label="PD",style="g--")

    ax1.legend(loc="best",prop={'size':6})
    ax2.legend(loc="best",prop={'size':6})

    ax1.grid()
    ax2.set_ylim(0, 0.005)
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Value")
    ax2.set_ylabel("PD(%)")
    plt.suptitle(str(ccode), size='10')
    pp.savefig(fig)
    plt.close("all")
    pp.close()

    return 0

if __name__ == '__main__' :
    sys.exit(main())