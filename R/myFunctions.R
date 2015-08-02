#############
# FUNCTIONS #
#############

###################### DATA FRAME MANIPULATION #############################

#############################
# create lagged columns
# assume first column is DATE
lagData <- function(data, days = 1:4) {
  numDays <- length(days)
  # empty list for data frames
  lags <- list()
  newnames <- list()
  # copy date column less maximum number of lag days rows
  lags[[1]] <- data[(max(days)+1):(nrow(data)),1]
  newnames[[1]] <- c("DATE")
  # construct lagged data frames (including or without first column)
  for (ii in 1:numDays) {
    # drop DATE column from columns to lag
    lags[[ii+1]] <- data[(max(days)+1-days[ii]):(nrow(data)-days[ii]),-1]
    # rename columns in lagged data frames (append lag length)
    newnames[[ii+1]] <- paste((colnames(data))[-1],"0",days[ii],sep="")
  }
  # cbind everything into one data frame
  lagdf <- as.data.frame(lags[[1]])
  for (ii in 1:numDays) {
    lagdf <- cbind(lagdf,lags[[ii+1]])
  }
  colnames(lagdf) <- unlist(newnames)

  # remove incomplete cases (I think only at the end)
  lagdf <- lagdf[complete.cases(lagdf),]

  return(lagdf)
}

##############################################
# compute tendency using last two days in data
tendency <- function(lagData) {
  newData <- lagData
  # get city abbreviations from data frame
  cities <- colnames(lagData)[2:ncol(lagData)]
  cities <- unique(substr(cities,1,3))
  numcols <- ncol(lagData)
  numcities <- length(cities)
  citytend <- paste(cities,"_T",sep="")
  count <- 0
  for (jj in (numcols-numcities+1):numcols) {
    count <- count+1
    newData[,jj] <- newData[,jj-numcities] - newData[,jj]
    colnames(newData)[jj] <- citytend[count]
  }
  return(newData)
}

##############################
# compute principal components
# using columns of supplied
# data frame
compPC <- function(data, rows = c(1,365), withDate=FALSE) {
  if (withDate) {
    pca <- prcomp(data[(rows[1]:rows[2]),-1])
  } else {
    # default is that DATE is already removed
    pca <- prcomp(data[(rows[1]:rows[2]),])
  }
  return(pca)
}

###########################
# convert a data frame from
# city to PC-component form
projPC <- function(data, pca, withDate=TRUE) {
  if (withDate) {
    # default is that DATE is included
    # assumed to be in first column
    pred <- predict(pca, newdata=data[,-1])
    newdata <- cbind(data[,1],as.data.frame(pred))
    colnames(newdata)[1] <- "DATE"
    return(newdata)
  } else {
    return(as.data.frame(predict(pca, newdata=data)))
  }
}

########################
# insert city after date
mergeCity <- function(cityName, cityData, targetData) {
  newdata <- merge(cityData[,c("DATE",cityName)],
                   targetData, by="DATE")
  return(newdata)
}

############################### CLUSTER ####################################

# compute clusters using relative
# in selection of cities
# colnames is a vector of strings
clusters <- function(data, colnames, cent=4, 
                     samp = c(1,3*365), seed=666) {
  set.seed(seed)
  KMC <- kmeans(data[samp[1]:samp[2],colnames],centers=cent,
                iter.max = 100)
  # return cluster object
  return(KMC)
}

# allocate data into clusters based on
# proximity to centers
allocateClusters <- function(centers, data) {
  dist <- NULL
  for (ii in 1:nrow(centers)) {
    dist <- cbind(dist,colSums((t(data)-centers[ii,])^2))
  }
  return(apply(dist,1,which.min))  
}

######################### PERFORMANCE MEASURES #############################

sumSquares <- function(predictions, actual) {
  return(sum((predictions-actual)^2))
}

Rsq <- function(predictions, actual, base) {
  SSE <- sumSquares(predictions, actual)
  SST <- sumSquares(base, actual)
  return(1 - SSE/SST)
}

RMSE <- function(predictions, actual) {
  return(sqrt(sumSquares(predictions,actual)/length(actual)))
}

PRED <- function(predictions, actual, margin) {
  return((table(abs(predictions - actual) < margin) /
     length(actual))[2])
}

diffs <- function(data) {
  # return vector of differences (starting with zeros) between
  # adjacent entries in data
  return(c(0,data[-1]-data[-length(data)]))
}

extremes <- function(data, change, indices=FALSE) {
  # return rows in data where change equals "change" or more
  if (indices)
    return(which(diffs(data) >= change))
  else
    return(diffs(data) >= change)
}

########################
# performance report
#
perfReport <- function(prediction, actual, base) {
  print(paste("SSE:", round(sumSquares(prediction,actual))))
  print(paste("SST:", round(sumSquares(base,actual))))
  print(paste("Rsq:", round(Rsq(prediction,actual, base),2)))
  print(paste("RMS error:",
              round(0.1*RMSE(prediction,actual),2),"degrees"))
  print(paste("3 degree rate:",
              round(PRED(prediction,actual,30),2),
              "(",round(PRED(base,actual,30),2),")"))
  print(paste("5 degree rate:",
              round(PRED(prediction,actual,50),2),
              "(",round(PRED(base,actual,50),2),")"))

  warmTable <- table(extremes(actual,50),extremes(prediction,50))
  colnames(warmTable) <- c("PF","PT")
  coolTable <- table(extremes(-actual,50),extremes(-prediction,50))
  colnames(coolTable) <- c("PF","PT")
  print("Warmings by 5 degrees:")
  print(warmTable)
  print("Coolings by 5 degrees:")
  print(coolTable)
}
  
############################ PLOT FUNCTIONS ################################

########################
# plot results
#
plotResults <- function(title, testing, pred2014,
                        Rsq, RMSE,
                        springTime=TRUE) {
  january <- as.numeric(as.Date("2014-01-01"))
  march <- as.numeric(as.Date("2014-03-21"))
  twentyfive <- 250
  if (springTime) {
    plot(testing$DATE[80:170],testing[80:170,2],
         main=title, cex.main=0.9,
         xlab="2014", ylab="Temp / 0.1C",
         type='b',lwd=2)
    text(march, twentyfive+30,
         substitute(R^2==a,list(a=round(Rsq,2))),
         adj=c(0,0.5),cex=0.8)
    text(march, twentyfive-10,
         paste("RMSE","=", round(RMSE,2),"C"),
         adj=c(0,0.5),cex=0.8)
    lines(testing$DATE[80:170],pred2014[80:170],
          type='b', pch=19, col="red", lwd=1)
    legend("bottomright",inset=0.1,cex=1.2,
           legend=c("actual","predicted"),
           pch=c(1,19),col=c("black","red"),bty="n")
  } else {
    plot(testing$DATE[1:365],testing[1:365,2],
         main=title, cex.main=0.9,
         xlab="2014", ylab="Temp / 0.1C",
         type='b',lwd=2)
    text(january, twentyfive,
         substitute(R^2==a,list(a=round(Rsq,2))),
         adj=c(0,0.5),cex=0.8)
    text(january, twentyfive-50,
         paste("RMSE","=", round(RMSE,2),"C"),
         adj=c(0,0.5),cex=0.8)
    lines(testing$DATE[1:365],pred2014[1:365],
          type='b', pch=19, col="red", lwd=1)
    legend("bottom",inset=0.2,cex=1.2,
           legend=c("actual","predicted"),
           pch=c(1,19),col=c("black","red"),bty="n")
  }
}

########################
# plot clusters
#
library(scatterplot3d)
plotClusters <- function(clust, triangle) {
  nclust <- length(clust$size)
  myColours <- rainbow(nclust,start=0,end=4/6)
  samp <- sample(x = nrow(triangle), size = 600)
  sp <- scatterplot3d(triangle[samp,1],
                      triangle[samp,2],
                      triangle[samp,3],
                      pch=19,
                      color=myColours[clust$cluster[samp]],
                      xlab=substring(colnames(triangle)[1],1,3),
                      ylab=substring(colnames(triangle)[2],1,3),
                      zlab=substring(colnames(triangle)[3],1,3),
                      box=FALSE, type="h",cex.symbols=0.5,lwd=0.5)
}