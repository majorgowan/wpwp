source("readData.R")
source("myFunctions.R")

city <- "TOR"
clusterTriangle <- c("CHI","MON","NYK")
nclust <- 3
numPC <- 8
predDay <- 1
statRange <- c(1,3*365)  # for pca and cluster computations

# create data frame with the temperatures lagged
# by predDay+1 and predDay+2 days
lagCityData <- lagData(maxTemp, 
                       days=c(predDay,predDay+1))

# cluster based on differences between 
# the target city and the triangle cities
predDayString <- paste("0",predDay,sep="")
clTr <- paste(clusterTriangle,predDayString,sep="")
cty <- paste(city,predDayString,sep="")
triangle <- lagCityData[,clTr]-lagCityData[,cty]
clust <- clusters(triangle,
                  colnames=clTr,
                  cent=nclust,
                  samp=statRange,
                  seed=666)

# allocate full data set into clusters
clustersAll <- allocateClusters(clust$centers, triangle)

# plot clusters
# plotClusters(clust,triangle)

# replace the two-day lag column with the "tendency"
lagCityTendency <- tendency(lagCityData)

# compute principal components using
# first three years of data
pca_tend <- compPC(lagCityTendency,
                   statRange, withDate=TRUE)

# project lagged temp and lagged tendency 
lagTendPCData <- projPC(lagCityTendency,
                        pca_tend, withDate = TRUE)

# insert unlagged temperatures for city to be predicted
lagTendPCData <- mergeCity(city, maxTemp, lagTendPCData)

# formula for regression models
formulaString <- paste(city,"~",
                       paste(paste("PC",1:numPC,sep=""),
                             collapse=" + "))

# partition data into the nclust clusters
# and construct regression model for each
training <- lagTendPCData[format(lagTendPCData$DATE,"%Y")<2014,]
trainClust <- clustersAll[format(lagTendPCData$DATE,"%Y")<2014]
models <- list()
for (ii in 1:nclust) {
  rows <- which(trainClust==ii)
  trainData <- training[rows,]
  models[[ii]] <- lm(as.formula(formulaString),data=trainData)
}

# do the same for testing set
testing <- lagTendPCData[format(lagTendPCData$DATE,"%Y")==2014,]
testClust <- clustersAll[format(lagTendPCData$DATE,"%Y")==2014]
pred2014 <- rep(0,nrow(testing))
for (ii in 1:nclust) {
  rows <- which(testClust==ii)
  testData <- testing[rows,]
  pred2014[rows] <- predict(models[[ii]],newdata=testData)
}

# base model: weather same as on prediction day
base <- c(training[(nrow(training)-predDay+1):nrow(training),2],
          testing[1:(nrow(testing)-predDay),2])

# performance report
perfReport(pred2014,testing[,2],base)

title <- paste("Temperature prediction for",city,
               "\nusing temperature and temperature tendency",
               "\nfrom",predDay,"days earlier,",
               numPC,"principal components,",
               "and ",nclust,"clusters")

Rsquare <- Rsq(pred2014,testing[,2],base)
RMSError <- 0.1*RMSE(pred2014,testing[,2])
#plotResults(title, testing, pred2014, Rsquare, RMSError, springTime=TRUE)
