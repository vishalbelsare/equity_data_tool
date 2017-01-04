returns=csvread('returns.txt',1,1);
prices=csvread('prices.txt',2,1);
volumes=csvread('volumes.txt',2,1);
[T,n]=size(returns);
