###################
# read in NOAA data
cit1 <- read.csv("../Data/NOAA//ChiCinCleDetPhiTor_2009-2015.csv")
cit2 <- read.csv("../Data/NOAA//ChaDsmMilMinMtlNasNobStlWas_2009-2015.csv")
cit3 <- read.csv("../Data/NOAA//NykAtlDenKanFarMemBos_2009-2015.csv")
# strip all the "weather type" columns (not uniformly present)
cit1 <- subset(cit1,,-which(grepl("WT",colnames(cit1))))
cit2 <- subset(cit2,,-which(grepl("WT",colnames(cit2))))
cit3 <- subset(cit3,,-which(grepl("WT",colnames(cit3))))
cities <- rbind(cit1,cit2,cit3)
# convert date to Date format
cities$DATE <- as.Date(as.character(cities$DATE),"%Y%m%d")
# convert station names to columns, variable as Max Temp
library(reshape2)
maxTempNOAA <- dcast(cities, DATE ~ STATION_NAME, value.var="TMAX")
colnames(maxTempNOAA) <- c("DATE",
                           "CHI","CIN","CLE","DET",
                           "PHI","TOR","CHA","DES",
                           "MIL","MIN","MON","NAS",
                           "NOB","STL","WAS","ATL",
                           "BOS","DEN","FAR","KAN",
                           "MEM","NYK")
# convert -9999 to NA
maxTempNOAA[maxTempNOAA==-9999] <- NA
# throw out Canadian cities (too many NA)
maxTempNOAA$TOR <- NULL   # Toronto
maxTempNOAA$NOB <- NULL   # North Bay
maxTempNOAA$MON <- NULL   # Montreal

#################
# read in EC data
# Toronto
TORONTO  <- rbind(read.csv("../Data/EC/Toronto2009.csv",stringsAsFactors=FALSE,skip=25),
                  read.csv("../Data/EC/Toronto2010.csv",stringsAsFactors=FALSE,skip=25),
                  read.csv("../Data/EC/Toronto2011.csv",stringsAsFactors=FALSE,skip=25),
                  read.csv("../Data/EC/Toronto2012.csv",stringsAsFactors=FALSE,skip=25),
                  read.csv("../Data/EC/Toronto2013.csv",stringsAsFactors=FALSE,skip=25),
                  read.csv("../Data/EC/Toronto2013b.csv",stringsAsFactors=FALSE,skip=25),
                  read.csv("../Data/EC/Toronto2014.csv",stringsAsFactors=FALSE,skip=25),
                  read.csv("../Data/EC/Toronto2015.csv",stringsAsFactors=FALSE,skip=25))
# keep only max temp (in thenths of degrees), converting date to Date format
maxTempTORONTO  <- data.frame(DATE=as.Date(TORONTO$Date.Time,"%Y-%m-%d"),
                              TOR=as.integer(10*TORONTO$Max.Temp...C.))
#print(paste("Toronto: missing",
#            sum(is.na(maxTempTORONTO$TOR)), "values."))
# remove incomplete rows (because of change to station name in 2013)
maxTempTORONTO <- maxTempTORONTO[complete.cases(maxTempTORONTO),]

# Montreal (note fixed April 13-14 2015 by merging several files - stations?)
MONTREAL <- rbind(read.csv("../Data/EC/Montreal2009.csv",stringsAsFactors=FALSE,skip=25),
                  read.csv("../Data/EC/Montreal2010.csv",stringsAsFactors=FALSE,skip=25),
                  read.csv("../Data/EC/Montreal2011.csv",stringsAsFactors=FALSE,skip=25),
                  read.csv("../Data/EC/Montreal2012.csv",stringsAsFactors=FALSE,skip=25),
                  read.csv("../Data/EC/Montreal2013.csv",stringsAsFactors=FALSE,skip=25),
                  read.csv("../Data/EC/Montreal2014.csv",stringsAsFactors=FALSE,skip=25),
                  read.csv("../Data/EC/Montreal2015_fix.csv",stringsAsFactors=FALSE,skip=25))
maxTempMONTREAL <- data.frame(DATE=as.Date(MONTREAL$Date.Time,"%Y-%m-%d"),
                             MON=as.integer(10*MONTREAL$Max.Temp...C.))
#print(paste("Montreal: missing",
#            sum(is.na(maxTempMONTREAL$MON)), "values."))

# Windsor
WINDSOR  <- rbind(read.csv("../Data/EC/Windsor2009.csv",stringsAsFactors=FALSE,skip=25),
                  read.csv("../Data/EC/Windsor2010.csv",stringsAsFactors=FALSE,skip=25),
                  read.csv("../Data/EC/Windsor2011.csv",stringsAsFactors=FALSE,skip=25),
                  read.csv("../Data/EC/Windsor2012.csv",stringsAsFactors=FALSE,skip=25),
                  read.csv("../Data/EC/Windsor2013.csv",stringsAsFactors=FALSE,skip=25),
                  read.csv("../Data/EC/Windsor2014.csv",stringsAsFactors=FALSE,skip=25),
                  read.csv("../Data/EC/Windsor2014b.csv",stringsAsFactors=FALSE,skip=25),
                  read.csv("../Data/EC/Windsor2015.csv",stringsAsFactors=FALSE,skip=25))
maxTempWINDSOR <- data.frame(DATE=as.Date(WINDSOR$Date.Time,"%Y-%m-%d"),
                             WIN=as.integer(10*WINDSOR$Max.Temp...C.))
#print(paste("Windsor: missing",
#            sum(is.na(maxTempWINDSOR$WIN)), "values."))
# remove incomplete rows (because of discontinuity in 2014)
maxTempWINDSOR <- maxTempWINDSOR[complete.cases(maxTempWINDSOR),]

# Quebec
QUEBEC <- rbind(read.csv("../Data/EC/QUEBEC2009.csv",stringsAsFactors=FALSE,skip=25),
                read.csv("../Data/EC/QUEBEC2010.csv",stringsAsFactors=FALSE,skip=25),
                read.csv("../Data/EC/QUEBEC2011.csv",stringsAsFactors=FALSE,skip=25),
                read.csv("../Data/EC/QUEBEC2012.csv",stringsAsFactors=FALSE,skip=25),
                read.csv("../Data/EC/QUEBEC2013.csv",stringsAsFactors=FALSE,skip=25),
                read.csv("../Data/EC/QUEBEC2014.csv",stringsAsFactors=FALSE,skip=25),
                read.csv("../Data/EC/QUEBEC2015.csv",stringsAsFactors=FALSE,skip=25))
maxTempQUEBEC <- data.frame(DATE=as.Date(QUEBEC$Date.Time,"%Y-%m-%d"),
                              QUE=as.integer(10*QUEBEC$Max.Temp...C.))
#print(paste("Quebec City: missing",
#            sum(is.na(maxTempQUEBEC$QUE)), "values."))
maxTempQUEBEC <- maxTempQUEBEC[complete.cases(maxTempQUEBEC),]

# merge data frames on Date
maxTempEC <- merge(maxTempTORONTO, maxTempMONTREAL, by = "DATE")
maxTempEC <- merge(maxTempEC, maxTempWINDSOR, by = "DATE")
maxTempEC <- merge(maxTempEC, maxTempQUEBEC, by = "DATE")

###########################
# merge NOAA and EC on DATE
maxTemp <- merge(maxTempNOAA,maxTempEC,by="DATE")

############################
# clean up namespace, memory
rm(cities, maxTempNOAA,
   MONTREAL, TORONTO, WINDSOR, QUEBEC,
   maxTempTORONTO, maxTempMONTREAL, maxTempWINDSOR,
   maxTempQUEBEC,
   maxTempEC)
