library(ggsci)
library(dplyr)
library(viridis)
library(ggplot2)
library(anytime)
library(wordcloud)
library(hrbrthemes)
library(RColorBrewer)
set.seed(101)


df <- read.csv("claps_v1.csv", stringsAsFactors = FALSE)
df$datePosted <- as.POSIXlt(df$postedAt, origin="1970-01-01")
df$yearPosted <- df$date$year + 1900
df$monthPosted <- months(df$date)
df$weekdayPosted <- weekdays(df$date)
df$datePosted <- as.POSIXct(df$datePosted) %>% unlist
df <- df %>% filter(nchar(tags)>3, readingTime > 0)

# count of number of posts vs. count of freq. of claps : distribution of user claps
a <- data.frame(item = NA, freq = df$userClapCount)
a$item <- "userClapCount"
b <- data.frame(item = NA, freq = df$readingTime)
b$item <- "readingTime"
c <- rbind(a, b)
rm(list = c("a", "b"))

ggplot(c, aes(x = freq, fill = item)) + 
  geom_density(alpha = 0.75) +
  scale_fill_brewer(palette="RdYlGn") + 
  theme_minimal() +
  labs(title = "Distribution of userClaps and readingTime")


# claps vs. reading time
# this results in a dot plot (strip chart)
userClapsVsReadingTime <- df %>% select(userClapCount, readingTime)
tt <- userClapsVsReadingTime %>% group_by(userClapCount, readingTime) %>% summarise(freq = (sum(readingTime)))
tt$freq <- tt$freq/tt$readingTime

ggplot(data = tt, aes(x = userClapCount, y = readingTime, size = freq)) + 
  geom_point(alpha=0.7, shape=21, color="black", fill = "#DD4124") +
  scale_size(range = c(1, 12), name="Frequency") +
  scale_x_continuous(breaks=seq(0, max(tt$readingTime), 2)) +
  scale_y_continuous(breaks=seq(0, max(tt$userClapCount), 2)) +
  theme_minimal() +
  labs(title = "User Clap Count vs. Reading time") +
  theme(panel.grid.major.x = element_blank(), panel.grid.major.y = element_blank()) 


# tags vs. claps
tagsDf <- df %>% select(tags, userClapCount)

charCheck <- function(a) {
  b <- unlist(a)
  return(b[nchar(b)>3])
}

tagsDf$tags <- tagsDf$tags %>% strsplit("'")
tagsDf$tags <- lapply(tagsDf$tags, charCheck)
uniqueTags <- tidyr::unnest(tagsDf, cols = "tags")
uniqueTags <- aggregate(uniqueTags$userClapCount, 
                        by=list(tags = uniqueTags$tags), 
                        FUN=sum)

# wordcloud of tag frequencies by nclaps
colnames(uniqueTags) <- c("tags", "nClaps")
uniqueTags <- uniqueTags[order(-uniqueTags$nClaps),]
rownames(uniqueTags) <- NULL
subsetTags <- uniqueTags[uniqueTags$nClaps>25,]

wordcloud(words = subsetTags$tags, freq = subsetTags$nClaps, min.freq = 1, rot.per=0.35,
          max.words=200, random.order=FALSE, colors=brewer.pal(8, "RdYlGn"))
