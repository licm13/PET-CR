#land data

#input data: latent heat (hfls), sensible heat (hfss), specific humidity (huss), 
#air pressure (ps), air temperature (tas), skin temperature (ts)

#output data: PETe and PETa

get_pet<-function(x){
  hfls<-x[1]*0.0864
  hfss<-x[2]*0.0864
  huss<-x[3]
  ps<-x[4]
  tas<-x[5]
  ts<-x[6]

  ############## Calculating PET ##############
  Lv<-(2500.8-2.36*(tas-273.15)+0.0016*(tas-273.15)^2-0.00006*(tas-273.15)^3)/1000

  vptas<-0.611*exp(17.27*(tas-273.15)/(tas-273.15+237.3))
  vpts<-0.611*exp(17.27*(ts-273.15)/(ts-273.15+237.3))
  
  w<-huss/(1-huss)
  es<-w/(w+0.622)*(ps/1000)
  
  delta<-vptas*4098/(((tas-273.15)+237.3)^2)
  gamma<-1.005e-3/(Lv*0.622)*(ps/1000)
  
  beta<-hfss/hfls
  beta1<-0.24*gamma/delta
  beta2<-gamma*(ts-tas)/(vpts-es)
  
  ##two constraints of the wet Bowen ratio (beta_w)
  beta12<-max(beta2,beta1,na.rm=T)
  beta_w<-min(beta12,beta,na.rm=T)
  
  ##############
  lh<-hfls/Lv
  sh<-hfss/Lv
  rn<-sh+lh
  
  pete<-rn/(1+beta_w)
  peta<-sh/beta_w
  
  out<-c(pete,peta)
  
  return(out)
}


