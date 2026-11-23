# CDS533 Assignment 3 — Question 3：Seven Studies
# 负责人：何铭恩（HE Mingen, 3162445）


library(ISLR2)
library(car)



# Study A：两联赛 log(Salary) 比较（两独立样本 t 检验）
hitters <- as.data.frame(ISLR2::Hitters)
hitters_salary <- subset(hitters, !is.na(Salary) & Salary > 0)
hitters_salary$log_salary <- log(hitters_salary$Salary)

AL <- hitters_salary$log_salary[hitters_salary$League == "A"]
NL <- hitters_salary$log_salary[hitters_salary$League == "N"]


# 描述统计
tapply(hitters_salary$log_salary, hitters_salary$League, length)
tapply(hitters_salary$log_salary, hitters_salary$League, mean)
tapply(hitters_salary$log_salary, hitters_salary$League, sd)

# Welch 两样本 t 检验（不假设方差相等，R 默认更稳健）
t.test(log_salary ~ League, data = hitters_salary, var.equal = FALSE)



# Study B：log(Outstate) vs log(Room.Board) 配对 t 检验
colleges <- as.data.frame(ISLR2::College)
college_costs <- subset(colleges, !is.na(Outstate) & !is.na(Room.Board) &
                          Outstate > 0 & Room.Board > 0)
college_costs$log_tuition <- log(college_costs$Outstate)
college_costs$log_living  <- log(college_costs$Room.Board)

# 描述统计（差值）
d <- college_costs$log_tuition - college_costs$log_living
length(d); mean(d); sd(d)

# 配对 t 检验
t.test(college_costs$log_tuition, college_costs$log_living, paired = TRUE)



# Study C：符号检验（binomial，p = 0.5）
differ <- subset(college_costs, Outstate != Room.Board)
n_diff    <- nrow(differ)
n_greater <- sum(differ$Outstate > differ$Room.Board)

# 二项检验（双侧）
binom.test(n_greater, n_diff, p = 0.5, alternative = "two.sided")



# Study D：mpg 分布 美/日 比较（Mann-Whitney U）
cars_two <- subset(as.data.frame(ISLR2::Auto), origin %in% c(1, 3))
cars_two$origin_group <- factor(cars_two$origin,
                                levels = c(1, 3),
                                labels = c("American", "Japanese"))

# 描述统计（中位数）
tapply(cars_two$mpg, cars_two$origin_group, median)
tapply(cars_two$mpg, cars_two$origin_group, mean)
tapply(cars_two$mpg, cars_two$origin_group, length)

# Mann-Whitney（等价 Wilcoxon 秩和检验）
wilcox.test(mpg ~ origin_group, data = cars_two, correct = FALSE)



# Study E：公私校频率 vs 0.5（拟合优度）
private_counts <- table(colleges$Private)
private_counts

# 二项检验（Private Yes 比例 vs 0.5）
binom.test(private_counts["Yes"], sum(private_counts), p = 0.5,
           alternative = "two.sided")

# 等价卡方拟合优度
chisq.test(private_counts, p = c(0.5, 0.5))



# Study F：Private × Top10 关联（卡方独立性）
colleges$top10_group <- factor(ifelse(colleges$Top10perc >= 50, "High", "Lower"),
                               levels = c("Lower", "High"))
private_top10 <- table(colleges$Private, colleges$top10_group)
private_top10

# 行比例（Private 内 High 比例）
prop.table(private_top10, margin = 1)

# 卡方独立性检验
chisq.test(private_top10, correct = FALSE)



# Study G：三产地 mpg 方差齐性（Levene）
auto_full <- as.data.frame(ISLR2::Auto)
auto_full$origin_group <- factor(auto_full$origin,
                                 levels = c(1, 2, 3),
                                 labels = c("American", "European", "Japanese"))

# 各组样本量、方差
tapply(auto_full$mpg, auto_full$origin_group, length)
tapply(auto_full$mpg, auto_full$origin_group, var)

# Levene 检验（以中位数为中心，更稳健）
car::leveneTest(mpg ~ origin_group, data = auto_full, center = median)

