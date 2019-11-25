library(tm)
library(ggsci)
library(dplyr)
library(e1071)
library(viridis)
library(ggplot2)
library(anytime)
library(tidyverse)
library(lubridate)
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
df$highlightDateC <- as.POSIXct(df$highlightedAt, origin="1970-01-01", tz="EEST")


a <- data.frame(item = NA, freq = df$numOfSentences*1) #multiply it with 10 to scale up
a$item <- "numOfSentences"
b <- data.frame(item = NA, freq = df$numOfWords)
b$item <- "numOfWords"
c <- rbind(a, b)
rm(list = c("a", "b"))

skewness(df$numOfSentences)
skewness(df$numOfWords)

############################################################

# ggplot(df, aes(x = highlightDate)) + 
#   geom_histogram(bins=40, color = "#000000") 

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

dow_table <- table(df$highlightTimeDoW)
dow_levels <- names(dow_table)[c(4, 2, 6, 7, 5, 1, 3)]

ggplot(df, aes(x = highlightTimeDoW)) + 
  geom_histogram(stat="count") + 
  stat_count(aes(y=..count.., label=..count..), geom="text", vjust=-.1) +
  scale_x_discrete(limits = dow_levels) +
  labs(title = "Highlight frequency according to day of week") + 
  xlab("Day of Week") +
  ylab("Number of highlights") +
  theme_minimal()

ggplot(df, aes(x = highlightTimeHour)) + 
  geom_histogram(stat="count") + 
  stat_count(aes(y=..count.., label=..count..), geom="text", vjust=-.1) +
  labs(title = "Highlight frequency according to hour of day") + 
  xlab("Hour of day") +
  ylab("Number of highlights") +
  theme_minimal()

# wordcloud of highlighted text & post titles
d <- read.csv("word_freq_highlights_v1.csv", stringsAsFactors = FALSE)

png("wordcloud_quote.png", width=1000,height=1000)
wordcloud(words = d$word, freq = d$freq, min.freq = 1, rot.per=0.15,
          max.words=300, random.order=F, colors=brewer.pal(8, "Dark2"),
          vfont=c("sans serif","plain"), scale=c(8,.3))
dev.off()

t <- read.csv("word_freq_title_v1.csv", stringsAsFactors = FALSE)

png("wordcloud_title.png", width=1000,height=1000)
wordcloud(words = t$word, freq = t$freq, min.freq = 1, rot.per=0.15,
          max.words=Inf, random.order=F, colors=brewer.pal(8, "Dark2"),
          vfont=c("sans serif","plain"), scale=c(8,.3))
dev.off()

# seasonality if any

dates <- subset(df, select = c("highlightDateC", "numOfWords"))
dates$highlightDateC <- dates$highlightDateC

season <- as_tibble(dates) %>% 
  rename_all(tolower) %>% 
  mutate(date = as.Date(dates$highlightDateC))

season <- season %>% 
  mutate(
    year = factor(year(date)),     # use year to define separate curves
    date_x = update(date, year = 1)  # use a constant year for the x-axis
  ) 

ggplot(season, aes(date_x, numofwords, color = year)) +
  scale_x_date(date_breaks = "1 month", date_labels = "%b") +
  geom_point() + coord_polar()
