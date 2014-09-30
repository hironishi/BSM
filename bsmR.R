##############################
#Black Sholes Merton Model
##############################
GetD1 <- function(A0,L,R,Vola.A,Tm){
  d1 <- log(A0)-log(L)+(R+0.5*(Vola.A)^2)*Tm;
  d1 <- d1/(Vola.A*sqrt(Tm));
}
GetD2 <- function(A0,L,R,Vola.A,Tm){
  d2 <- GetD1(A0,L,R,Vola.A,Tm) - Vola.A*sqrt(Tm);
}
ImpliedStockValue <- function(A0,L,R,Vola.A,Tm){
  Nd1 <- pnorm(GetD1(A0,L,R,Vola.A,Tm));
  Nd2 <- pnorm(GetD2(A0,L,R,Vola.A,Tm));
  stock.price <- A0*Nd1-L*exp(-1*R*Tm)*Nd2;
}
#vola.sの式が怪しい。
ImpliedStockVolatility <- function(A0,S0,L,R,Vola.A,Tm){
  Nd1 <- pnorm(GetD1(A0,L,R,Vola.A,Tm));
#  Vola.S <- Vola.A*A0*Nd1/S0;
  Vola.S <- Vola.A*S0*Nd1/A0;
}
ImpliedDebtPrice <- function(A0,L,R,Vola.A,Tm){
  d<-A0-ImpliedStockValue(A0,L,R,Vola.A,Tm);
}
##############################
#Optimization
##############################
#Implied Asset Volatility
ImpliedAssetVolatility <- function(A0,S0,Vola.S,L,R,Tm){
  eval.stock.vola.function <- function(x){
    (Vola.S - ImpliedStockVolatility(A0,S0,L,R,x,Tm))^2
  }
  if(is.na(A0))
    return(NA);
  if(is.na(S0))
    return(NA);
  if(is.na(Vola.S))
    return(NA);
  if(is.na(L))
    return(NA);
  opt.asset.vola <- optimize(eval.stock.vola.function,interval=c(0.001,5),tol=10^(-6))$minimum;
}
#Implied Asset Value
ImpliedAssetValue <- function(S0,Vola.S,L,R,Tm){
  eval.stock.function <- function(x){
    (S0 - ImpliedStockValue(x,L,R,ImpliedAssetVolatility(x,S0,Vola.S,L,R,Tm),Tm))^2
  }
  if(is.na(S0))
    return(NA);
  if(is.na(Vola.S))
    return(NA);
  if(is.na(L))
    return(NA);
  opt.asset.value <- optimize(eval.stock.function,interval=c(0.5*(S0+L),2.0*(S0+L)),tol=10^(-6))$minimum;
}
##############################
#BSM Lapper
##############################
CalcHistoricalStockVolatility<-function(vector){
  sd(diff(log(vector)),na.rm=T);
}
CalcImpliedAssetReturn<-function(stock.vector,L,R,Tm){
  stock.vola<-CalcHistoricalStockVolatility(stock.vector);
  asset.values<-unlist(sapply(stock.vector
                              ,ImpliedAssetValue,stock.vola,L,R,Tm));
  return(c(NA,diff(log(asset.values))));
}
CalcImpliedAssetReturn2<-function(stock.vector,L,rate.vector,Tm){
  stock.vola<-CalcHistoricalStockVolatility(stock.vector);
  asset.values<-unlist(sapply(1:length(stock.vector)
                              ,FUN=function(idx){
                                s0<-stock.vector[idx];
                                r0<-rate.vector[idx];
                                ImpliedAssetValue(s0,stock.vola,L,r0,Tm)
                              }))
  return(c(NA,diff(log(asset.values))));
}
CalcImpliedAssetReturnDF<-function(data,L,R,Tm){
  as.data.frame(lapply(data
                       ,CalcImpliedAssetReturn,L,R,Tm));
}
CalcImpliedAssetVolatility<-function(stock.vector,L,R,Tm){
  stock.vola<-CalcHistoricalStockVolatility(stock.vector);
  asset.vola<-unlist(sapply(stock.vector
                            ,FUN=function(stock){
                              ImpliedAssetVolatility(ImpliedAssetValue(stock,stock.vola,L,R,Tm)
                                                     ,stock,stock.vola,L,R,Tm
                              );
                            }));
}
CalcImpliedAssetVolatilityDF<-function(data,L,R,Tm){
  as.data.frame(lapply(data
                       ,CalcImpliedAssetVolatility,L,R,Tm));
}