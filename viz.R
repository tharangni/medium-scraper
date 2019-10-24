library(ggplot2)
library(dplyr)
library(viridis)
library(anytime)

df <- read.csv("claps_v1.csv", stringsAsFactors = FALSE)
df$datePosted <- as.POSIXlt(df$postedAt, origin="1970-01-01")
df$yearPosted <- df$date$year + 1900
df$monthPosted <- months(df$date)
df$weekdayPosted <- weekdays(df$date)
df$datePosted <- as.POSIXct(df$datePosted) %>% unlist
df <- df %>% filter(nchar(tags)>3, readingTime > 0)

# count of number of posts vs. count of freq. of claps : distribution of user claps
# hist(df$userClapCount,
#      breaks = 18,
#      probability = TRUE)
# lines(density(df$userClapCount))


ggplot(data = df, aes(x = userClapCount)) + 
  geom_histogram(aes(y = ..density..), binwidth = 1) + 
  geom_density(alpha = 0.2, fill = "#00FF00") +
  geom_vline(aes(xintercept = mean(userClapCount)),
             linetype="dashed", color="black") + 
  scale_x_continuous("User Claps", labels = as.character(df$userClapCount), breaks = df$userClapCount) +
  # coord_cartesian(xlim = c(1, 38)) + 
  expand_limits(x = 0, y = 0) +
  labs(title = "Distribution of user claps") +
  theme(panel.grid.major.x = element_blank(), panel.grid.minor = element_blank())


# distribution of reading time for clapped posts
ggplot(data = df, aes(x = readingTime)) + 
  geom_histogram(aes(y = ..density..), binwidth = 1) + 
  geom_density(alpha = 0.2, fill = "#FF6666") +
  geom_vline(aes(xintercept = mean(readingTime)),
             linetype="dashed", color="black") + 
  scale_x_continuous("Reading Time", labels = as.character(df$readingTime), breaks = df$readingTime) +
  labs(title = "Distribution of reading time for clapped posts") +
  theme(panel.grid.major.x = element_blank(), panel.grid.minor = element_blank())

# claps vs. reading time
# this results in a dot plot (strip chart)
userClapsVsReadingTime <- df %>% select(userClapCount, readingTime)
# userClapsVsReadingTime <- distinct(userClapsVsReadingTime)

ggplot(data = userClapsVsReadingTime, aes(x = userClapCount, y = readingTime, fill = userClapCount)) + 
  geom_violin(aes(group = userClapCount), trim = FALSE) +
  scale_fill_viridis(direction = -1) +
  geom_jitter(position = position_jitter(0.2), cex=1.2, alpha = 0.5, color="#555555") + 
  labs(title = "User Clap Count vs. Reading time") 

  # stat_summary(fun.data="mean_sdl", mult=1, geom="crossbar", width=0.5)
  # stat_summary(fun.y=mean, geom="line", size=0.3, color="red")
  # coord_cartesian(xlim = c(0, 30), ylim = c(0, 30)) 

# tags vs. claps
tagsDf <- df %>% select(tags, userClapCount)

charCheck <- function(a) {
  b <- unlist(a)
  return(b[nchar(b)>3])
}

tagsDf$tags <- tagsDf$tags %>% strsplit("'")
tagsDf$tags <- lapply(tagsDf$tags, charCheck)
uniqueTags <- tidyr::unnest(tagsDf, cols = "tags")
uniqueTags <- aggregate(uniqueTags$userClapCount, by=list(tags = uniqueTags$tags), FUN=sum)

# wordcloud of tag frequencies by nclaps
ggplot(uniqueTags, aes(x=tags, y=nClaps)) + 
  geom_point() +
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, size=6))

# tags vs. reading time

# posts <-> claps <-> reading time <<->> tags