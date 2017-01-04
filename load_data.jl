prices=Array{Float64}(readcsv("prices.txt")[3:end,2:end]);
volumes=Array{Int64}(readcsv("volumes.txt")[3:end,2:end]);
data=readcsv("returns.txt");
returns=Array{Float64}(data[2:end,2:end]);
T,n=size(returns);
assets=Array{String}(data[1,2:end]);
dates=Array{String}(data[2:end,1]);
