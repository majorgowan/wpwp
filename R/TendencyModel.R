source("readData.R")
source("myFunctions.R")

city <- "TOR"
numPC <- 8
predDay <- 1

# create data frame with the temperatures lagged
# by one and two days
lagCityData <- lagData(maxTemp, 
                       days=c(predDay,predDay+1))

# replace the two-day lag column with the "tendency"
lagCityTendency <- tendency(lagCityData)

# compute principal components using
# first three years of data
pca_tend <- compPC(lagCityTendency,
                   c(1,3*365), withDate=TRUE)

# project lagged temp and lagged tendency 
lagTendPCData <- projPC(lagCityTendency,
                        pca_tend, withDate = TRUE)

# insert unlagged temperatures for city to be predicted
lagTendPCData <- mergeCity(city, maxTemp, lagTendPCData)

# construct training (before 2014) and testing (2014) sets
train <- which(as.numeric(
               format(lagTendPCData$DATE,"%Y"))<2014)
test <- which(as.numeric(
              format(lagTendPCData$DATE,"%Y"))==2014)
training <- lagTendPCData[train,]
testing <- lagTendPCData[test,]

formulaString <- paste(city,"~",
                       paste(paste("PC",1:numPC,sep=""),
                             collapse=" + "))

model <- lm(as.formula(formulaString), data=training)

# predictions
pred2014 <- predict(model,testing)

# base model: weather same as on prediction day
base <- c(training[(nrow(training)-predDay+1):nrow(training),2],
          testing[1:(nrow(testing)-predDay),2])

# performance report
perfReport(pred2014,testing[,2],base)

title <- paste("Temperature prediction for",city,
               "\nusing temperature and temperature tendency",
               "\nfrom",predDay,"days earlier and",
               numPC,"principal components")

Rsquare <- Rsq(pred2014,testing[,2],base)
RMSError <- 0.1*RMSE(pred2014,testing[,2])
#plotResults(title, testing, pred2014, Rsquare, RMSError, springTime=TRUE)
