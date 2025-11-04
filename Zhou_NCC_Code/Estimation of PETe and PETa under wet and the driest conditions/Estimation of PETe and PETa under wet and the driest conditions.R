#ocean data

#input data: latent heat (hfls), sensible heat (hfss), specific humidity (huss), 
#air pressure (ps), air temperature (tas), skin temperature (ts)

#output data: PETe and PETa under wet and the driest conditions

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
  
  gamma<-1.005e-3/(Lv*0.622)*(ps/1000)
  
  tae<-tas+es/gamma #air temperature under the driest conditions
  tse<-ts+vpts/gamma #surface temperature under the driest conditions
  
  vpts2<-0.611*exp(17.27*(tse-273.15)/(tse-273.15+237.3))
  
  beta<-hfss/hfls #Bowen ratio over ocean grid cells
  bw_wet<-gamma*(ts-tas)/(vpts-es) #wet Bowen ratio under wet conditions (ocean grid cells)
  bw_dry<-gamma*(tse-tae)/vpts2 #wet Bowen ratio under the driest conditions (ocean grid cells)
  
  ##############
  lh<-hfls/Lv
  sh<-hfss/Lv
  rn<-sh+lh

  PETe_w<-rn/(1+bw_wet)
  PETa_w<-sh/bw_wet

  PETe_d<-rn/(1+bw_dry)
  PETa_d<-rn/bw_dry #latent heat is zero under the driest conditions
  
  tsd<-(tse+tae)/2-(ts+tas)/2
  
  out<-c(lh,beta,bw_wet,bw_dry,PETe_w,PETa_w,PETe_d,PETa_d,tsd)
  
  return(out)
}
