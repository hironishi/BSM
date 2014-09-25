#!/usr/bin/python
# -*- coding: utf-8 -*-

from scipy.optimize import minimize
from scipy.integrate import quad
import math


class BSM:

    maxCnt = 100000

    def __init__(self,equity=0.0,vola_e=0.0,dept=0.0,r=0.0,T=0):
        self._asset = equity + dept
        self._vola_a = vola_e
        self._equity = equity
        self._vola_e = vola_e
        self._dept = dept
        self._r = r
        self._T = float(T)
        self._eval = float("inf")

    def d1(self,vola_a,asset):
        d1 = math.log(asset) - math.log(self._dept) + (self._r - 0.5 * pow(vola_a,2.0))*self._T
        d1 /= (vola_a * math.sqrt(self._T))
        return d1

    def d2(self,vola_a,asset):
        d2 = self.d1(vola_a,asset) - vola_a*math.sqrt(self._T)
        return d2

    def Nd(self,d,average=0.0, deviation=1.0):
        end = float("-inf")
        answer, abserr = quad(lambda x:(1/(math.sqrt(2*math.pi)*deviation))*math.exp(-pow((x-average),2.0)/(2*pow(deviation,2.0))),end,d)
        return answer

    def TheoricalStockPrice(self):
        s = self._asset * self.Nd(self.d1(self._vola_a,self._asset)) - self._dept * math.exp(-self._r * self._T) * self.Nd(self.d2(self._vola_a,self._asset))
        return s

    def TheoricalStockVola(self):
        v = self._asset * self._vola_a * self.Nd(self.d1(self._vola_a,self._asset)) / self._equity
        return v

    def optVola_a(self,x):
        return pow(self._vola_e - self._asset * x * self.Nd(self.d1(x,self._asset)) / self._equity,2.0)

    def updateAssetVola(self):

        ret = minimize(self.optVola_a,self._vola_a,method='nelder-mead',options={'xtol': 1e-8, 'disp': False})
        self._vola_a = ret.x[0]

    def optAsset(self,x):
        return pow(self._equity - x * self.Nd(self.d1(self._vola_a,x)) + self._dept * math.exp(-self._r * self._T) * self.Nd(self.d2(self._vola_a,x)),2.0)

    def updateAsset(self):

        ret = minimize(self.optAsset,self._asset,method='nelder-mead',options={'xtol': 1e-8, 'disp': False})
        self._asset = ret.x[0]

    def evaluation(self):
        delta_s = self._equity - self.TheoricalStockPrice()
        delta_v = self._vola_e - self.TheoricalStockVola()
        d = pow(delta_s,2.0) + pow(delta_v,2.0)
        self._eval = d
        return d

    def optimizeAssetAndAssetVola(self):
        cnt = 0
        while self.evaluation() > 1e-8:
            self.updateAssetVola()
            self.updateAsset()
            cnt += 1
            if cnt > self.maxCnt:
                print "Could not optimize : ",self
                break

    def __repr__(self):
        return "Asset=%s,AssetVola=%s,Tol=%s" % (self._asset,self._vola_a,self._eval)


if __name__ == '__main__' :
    b = BSM(equity=27648346000,vola_e=0.107645819,dept=33801000000,r=0.01,T=1)

    b.optimizeAssetAndAssetVola()

    print b
