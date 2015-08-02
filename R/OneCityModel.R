source("readData.R")
source("myFunctions.R")

city <- "TOR"
lagdays <- c(1,2,3,4)
numPC <- length(lagdays)
predDay <- min(lagdays)

# keep only requested city
cityData <- maxTemp[,c("DATE",city)]

# create data frame with the temperatures lagged
# by one through "lagdays" days
lagCityData <- lagData(cityData, days=lagdays)

# compute principal components using
# first three years of data
pca_kday <- compPC(lagCityData, c(1,3*365), withDate=TRUE)

# project lagged temperatures onto PC basis 
lagPCData <- projPC(lagCityData, pca_kday, withDate = TRUE)

# insert unlagged temperatures for city to be predicted
lagPCData <- mergeCity(city, maxTemp, lagPCData)

# construct training (before 2014) and testing (2014) sets
train <- which(as.numeric(format(lagPCData$DATE,"%Y"))<2014)
test <- which(as.numeric(format(lagPCData$DATE,"%Y"))==2014)
training <- lagPCData[train,]
testing <- lagPCData[test,]

formulaString <- paste(city, "~",
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

title <- paste("Temperature prediction for ",city,
               "\nusing temperatures from days",
               " -",paste(lagdays, collapse=", -"), sep="")

Rsquare <- Rsq(pred2014,testing[,2],base)
RMSError <- 0.1*RMSE(pred2014,testing[,2])
#plotResults(title, testing, pred2014, Rsquare, RMSError, springTime=TRUE)
