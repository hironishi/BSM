#!/usr/bin/python
# -*- coding: utf-8 -*-

from scipy.optimize import minimize
from scipy.integrate import quad
import math
import numpy as np
import pandas as pd


class BSM:
    """
    Vasicek-Kealhofer estimation procedureの実装
    """

    def __init__(self,equities=[] or pd.Series() ,dept=0.0,r=0.0,T=0):
        """
        コンストラクタ
        :param equities: 株価(時価総額)の推移
        :param dept: 負債(固定)
        :param r: 無リスク金利
        :param T: 日数単位の負債の満期
        :return:なし
        """
        if len(equities) <= 1:
            print "Error in initialize"
            return
        self._assets = np.array(equities) + np.array([dept]*len(equities))
        """Equity Volaの計算"""
        self._equities_return = pd.Series.pct_change(pd.Series(equities))
        self._equities_return = self._equities_return[self._equities_return != np.nan]
        self._vola_e = float(np.std(self._equities_return))
        """Asset Volaの計算"""
        self._asset_return = pd.Series.pct_change(pd.Series(self._assets))
        self._asset_return = self._asset_return[self._asset_return != np.nan]
        self._vola_a = float(np.std(self._asset_return))

        self._equities = equities
        self._dept = dept
        self._r = r
        self._T = float(T)
        self._eval = float("inf")
        self._pds = []

    def d1(self,vola_a,asset):
        """
        d1を計算する
        :param vola_a:Assetボラティリティ
        :param asset: Asset
        :return:
        """
        d1 = math.log(asset) - math.log(self._dept) + (self._r - 0.5 * pow(vola_a,2.0))*self._T
        d1 /= (vola_a * math.sqrt(self._T))
        return d1

    def d2(self,vola_a,asset):
        """
        d2を計算する
        :param vola_a:Assetボラティリティ
        :param asset: Asset
        :return:
        """
        d2 = self.d1(vola_a,asset) - vola_a*math.sqrt(self._T)
        return d2

    def Nd(self,d,average=0.0, deviation=1.0):
        """
        標準累積正規分布を計算する
        :param d: 求めたいx
        :param average:平均
        :param deviation:分散
        :return:
        """
        end = float("-inf")
        answer, abserr = quad(lambda x:(1/(math.sqrt(2*math.pi)*deviation))*math.exp(-pow((x-average),2.0)/(2*pow(deviation,2.0))),end,d)
        return answer

    def optAsset(self,x,vola_a,equity):
        """
        E - A(0)N(d1) - Xexp(-rT)N(d2)でassetを最適化するための関数
        :param x:
        :param vola_a:
        :param equity:
        :return:
        """

        return pow(self._vola_e - x * vola_a * self.Nd(self.d1(vola_a,x))/float(equity),2.0)
        #return pow(equity - x * self.Nd(self.d1(vola_a,x) + self._dept * math.exp(-self._r * self._T)*self.Nd(self.d2(vola_a,x))),2.0)

    # def optAssetVola(self,x,asset,equity):
    #     """
    #     ¥sigma_e - A(0)*¥sigma_a * N(d1)/Eでvola_aを最適化するための関数
    #     :param x:
    #     :param asset:
    #     :param equity:
    #     :return:
    #     """
    #
    #     return pow(self._vola_e - asset * x * self.Nd(self.d1(x,asset))/float(equity),2.0)

    def UpdateAssets(self,vola_a):

        self._assets = np.array([minimize(self.optAsset,asset,args=(vola_a,equity),method='nelder-mead',options={'xtol': 1e-8, 'disp': False}).x[0] for asset,equity in zip(self._assets,self._equities)])
        """Asset Volaの計算"""
        self._asset_return = pd.Series.pct_change(pd.Series(self._assets))
        self._asset_return = self._asset_return[self._asset_return != np.nan]
        vola_a = float(np.std(self._asset_return))
        return vola_a

    def evaluation(self,vola_a):

        self._eval = pow(vola_a-self._vola_a,2.0)

    def optimize(self):

        vola_a = self.UpdateAssets(self._vola_a)

        while self._eval > 1E-8:
            self.evaluation(vola_a)
            self._vola_a = vola_a
            vola_a = self.UpdateAssets(self._vola_a)

        self._vola_a = vola_a
        self.TheoricalPD()

        print self

    def TheoricalPD(self):
        append = self._pds.append
        for asset in self._assets:
            append(self.Nd(-self.d2(self._vola_a,asset)))


    def __repr__(self):
        """
        オブジェクトに対するprintを行った場合の書式設定
        :return:
        """
        return "Assets[0]=%s,AssetVola=%.3f,Tol=%e,PDs[-1]=%e" % (self._assets[1],self._vola_a,self._eval,self._pds[-1])


if __name__ == '__main__' :

    b = BSM(pd.Series([10,12,11,20,25,10,15,20,5,4,10,50,20]),dept=5,r=0.01,T=1)

    b.optimize()



