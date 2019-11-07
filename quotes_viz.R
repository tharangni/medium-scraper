library(ggsci)
library(dplyr)
library(viridis)
library(ggplot2)
library(anytime)
library(wordcloud)
library(hrbrthemes)
library(RColorBrewer)
set.seed(101)

############################################################

numberOfWords <- function(sentence) {
  return(sapply(strsplit(sentence, " "), length))
}

getmode <- function(v) {
  uniqv <- unique(v)
  uniqv[which.max(tabulate(match(v, uniqv)))]
}


############################################################

df <- read.csv("highlights_v1.csv", stringsAsFactors = F)
df$highlightDate <- as.POSIXct(df$highlightedAt, origin="1970-01-01")

df$quoteLength <- lapply(df$quoteText, numberOfWords) %>% unlist


############################################################

ggplot(df, aes(x = highlightDate)) + 
  geom_histogram(bins=40, color = "#000000") 

ggplot(df, aes(x = quoteLength)) + 
  geom_histogram(bins = 40) +
  stat_function(fun = function(x) dnorm(x, mean = mean(df$quoteLength), 
                                        sd = sd(df$quoteLength)) * length(df$quoteLength) * 8,
                color = "black", size = 1)
