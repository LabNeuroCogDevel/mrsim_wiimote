#!/usr/bin/Rscript
#
# Small R script to do simple plot of wii motion data
# Niles Oien January 2013

args <- commandArgs(trailingOnly = TRUE)
nargs <- length(args)
if (nargs != 1){
 print(quote=F,"USAGE : wiiPlot.R <input filename>")
 print(quote=F,"EXAMPLE : wiiPlot.R  wiiData/20130121_075804_test_23_motion.csv")
 print(quote=F, "Output filename will be wiiData/20130121_075804_test_23_motion.png")
 q(save="no")
}

inFilename <- args[1]

if (!(file.exists(inFilename))){
 print(quote=F,paste("File", inFilename, "not found"))
 q(save="no")
}

x <- read.table(inFilename, sep=",", header=T)
n <- length(x[,1])
print(quote=F, paste(n,"points read from", inFilename))

nc <- nchar(inFilename)
outFilename <- paste(sep="", substr(inFilename,1,nc-3), "png")
png(outFilename)

mrn <- max(x$numRumbles)
print(quote=F,paste(mrn,"rumbles were delivered"))
small <- paste(mrn,"rumbles delivered")
big <- paste("Motion data for", substr(inFilename,1,nc-11))
plot(x$timeSec, x$refToDataAngleDegrees, xlab="Time (seconds)", ylab="Angle difference (degrees)",
     main=big,sub=small)

print(quote=F, paste("Plot written to", outFilename))
q(save="no")

