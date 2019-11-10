library(ggsci)
library(dplyr)
library(e1071)
library(viridis)
library(ggplot2)
library(anytime)
library(wordcloud)
library(hrbrthemes)
library(RColorBrewer)
set.seed(101)

############################################################

getmode <- function(v) {
  uniqv <- unique(v)
  uniqv[which.max(tabulate(match(v, uniqv)))]
}


############################################################

df <- read.csv("highlights_v1.csv", stringsAsFactors = F)
df$highlightDate <- as.POSIXct(df$highlightedAt, origin="1970-01-01")


a <- data.frame(item = NA, freq = df$numOfSentences*20)
a$item <- "numOfSentences"
b <- data.frame(item = NA, freq = df$numOfWords)
b$item <- "numOfWords"
c <- rbind(a, b)
rm(list = c("a", "b"))

skewness(df$numOfSentences)
skewness(df$numOfWords)

############################################################

ggplot(df, aes(x = highlightDate)) + 
  geom_histogram(bins=40, color = "#000000") 

ggplot(df, aes(x = numOfWords)) + 
  geom_histogram(bins = 40) +
  stat_function(fun = function(x) dnorm(x, mean = mean(df$numOfWords), 
                                        sd = sd(df$numOfWords)) * length(df$numOfWords) * 8,
                color = "black", size = 1)

ggplot(df, aes(x = numOfSentences)) + 
  geom_histogram(bins = 12) +
  stat_function(fun = function(x) dnorm(x, mean = mean(df$numOfSentences), 
                                        sd = sd(df$numOfSentences)) * length(df$numOfSentences) * 1,
                color = "black", size = 1)

ggplot(c, aes(x = freq, fill = item)) + 
  geom_density(alpha = 0.75) +
  scale_fill_brewer(palette="RdYlGn") + 
  theme_minimal() +
  labs(title = "Distribution of numOfWords and numOfSentences")

ggplot(df, aes(x=numOfWords, y = numOfSentences))  +
  geom_point() 
