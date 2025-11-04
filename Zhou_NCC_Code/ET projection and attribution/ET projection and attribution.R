#########et projection&attribution###########
#load global mean data in 1pctCO2 first: cmip6_glob

aic<-array(NA,dim=c(12,111,7))
for(m in 1:7){
  da<-cmip6_glob[,,m*3]#1pctCO2-rad: three variables (et,pete,pr); 140 yrs; 7 models
  
  et<-rollapply(da[1,ls],mean,width=30) #30-year moving average
  pete<-rollapply(da[2,ls],mean,width=30)
  pr<-rollapply(da[3,ls],mean,width=30)

  tryCatch({
    f<-function (y) (et[1]-pr[1]*pete[1]/(pr[1]^y+pete[1]^y)^(1/y))^2
    xmin<-optimize(f,c(0,10),tol=0.000001)
    n2<-xmin$minimum
  },error=function(e){cat('ERROR:',conditionMessage(e),'\n')}) 
  
  aic[1,,m]<-et #directly projected ET in 1pctCO2-rad
  aic[2,,m]<-pr*(1+(pete/pr)^-n2)^(-1/n2) #ET projected using the Budyko approach
}

#et attribution
getn<-function(x){
  et<-x[1]
  pet<-x[2]
  pr<-x[3]
  
  tryCatch({
    f<-function (y) (et-pr*pet/(pr^y+pet^y)^(1/y))^2
    xmin<-optimize(f,c(0,10),tol=0.000001)
    n<-xmin$minimum
  },error=function(e){cat('ERROR:',conditionMessage(e),'\n')})
  return(n)
}


data0<-cmip6_glob[,,c(1:7)*3-2] #1pctCO2: three variables (et,pete,pr); 140 yrs; 7 models

data<-array(NA,dim=c(3,111,7))
for(i in 1:3){
  for(j in 1:7){
    data[i,,j]<-rollapply(data0[i,,j],mean,width=30) #30-year running mean
  }
}

nm<-apply(data,c(2,3),getn) #get parameter n

out1<-array(NA,dim=c(111,3,7))
out2<-array(NA,dim=c(111,3,7))

for(m in 1:7){
  pr<-data[3,,m]
  pete<-data[2,,m]
  et<-data[1,,m]
  
  et_cc<-pr*(1+(pete/pr)^-nm[1,m])^(-1/nm[1,m])
  et_lu<-et-et_cc
  
  et_rad<-rollapply(cmip6_glob[1,,m*3],mean,width=30)#et in 1pctCO2-rad
  et_lus<-et-et_rad
  
  out1[,,m]<-cbind(et-et[1],et_cc-et_cc[1],et_lu-et_lu[1]) #budyko approach
  out2[,,m]<-cbind(et-et[1],et_rad-et_rad[1],et_lus-et_lus[1]) #1pctCO2 experiments
}
