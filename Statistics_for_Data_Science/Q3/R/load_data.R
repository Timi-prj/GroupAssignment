# ============================================================
# CDS533 Assignment 3 — QQ Music 数据加载与清理脚本
# 角色：数据基础（Q4 EDA 负责人 + Q4 建模负责人共用入口）
# 目录规范：原始数据只读，清理逻辑写进代码，不使用手工修改版覆盖原文件
# 路径：统一相对路径，从项目根目录运行
# ============================================================

# ---- 依赖包 ----
# 本脚本仅用 base R 的 read.csv，无额外依赖
# （如需 tidyverse/dplyr，请在各自题目脚本中单独声明并加载）

# ---- 1. 读取数据 ----
# 说明：CSV 首列带 BOM（UTF-8-sig），用 fileEncoding = "UTF-8-BOM" 去除；
#       artist(s)_name 内含逗号，需正确解析引号。
qq <- read.csv("data/QQ_Music.csv",
               stringsAsFactors = FALSE,
               fileEncoding = "UTF-8-BOM")

# ---- 2. 数据概览 ----
# 观测单位：一首歌（one song record）
# 行数：844 首歌曲
# 列数：21 列

# ---- 3. 变量字典（Data Dictionary）----
# 标识/文本类：
#   track_name          歌曲名
#   artist(s)_name      艺人名（多艺人以逗号分隔）
# 发布信息：
#   released_year       发行年（1942–2023）
#   released_month      发行月（1–12）
#   released_day        发行日（1–31）
#   artist_count        参与艺人数量（1–8）
# 平台指标：
#   in_QQ_playlists     QQ 音乐收录该曲的歌单数（31–52898）
#   in_QQ_charts        QQ 音乐榜单排名/出现指标（0–147）
#   streams             QQ 音乐流媒体播放量（2762–3,703,895,074）
#   in_apple_playlists  Apple Music 收录歌单数（0–672）
#   in_apple_charts     Apple Music 榜单指标（0–275）
# 音频特征：
#   bpm                 每分钟节拍数（tempo）
#   key                 音乐调性（A/A#/B/C#/D/D#/E/F/F#/G/G#，含 89 个缺失）
#   mode                调式（Major / Minor）
#   danceability_%      舞动性（23–96，0–100 量表）
#   valence_%           积极性（4–97，0–100 量表）
#   energy_%            能量感（9–97，0–100 量表）
#   acousticness_%      原声度（0–97，0–100 量表）
#   instrumentalness_%  器乐度（0–91，0–100 量表）
#   liveness_%          现场感（3–92，0–100 量表）
#   speechiness_%       说唱度（2–59，0–100 量表）

# ---- 4. 类型修正 ----
# 音调 key 为无序类别（nominal），转为 factor
qq$key <- factor(qq$key, levels = c("A", "A#", "B", "C#", "D",
                                    "D#", "E", "F", "F#", "G", "G#"))

# 调式 mode 为无序二分类
qq$mode <- factor(qq$mode, levels = c("Major", "Minor"))

# ---- 5. 缺失值与无效值说明 ----
# 经检查：
#   - key 列有 89 个缺失（NA），其余列无缺失。
#   - 各百分比列（*_%）均在 0–100 合法区间内，无越界无效值。
#   - streams / bpm 等均为正数或合理范围，未发现需剔除的无效记录。
# 处理原则（遵循作业第 6 条要求）：
#   - 不伪造、不猜值填补。
#   - key 缺失在建模中如需使用，可按 NA 单独作为一类处理；
#     若模型不接受 NA，将按分析需要做 listwise 删除并在正文说明。
#   - 本脚本仅做“识别与标注”，不做任何删除，保证原始信息可追溯。

# ---- 6. 打印摘要供核对 ----
cat("=== QQ Music 数据载入成功 ===\n")
cat("行数（歌曲数）：", nrow(qq), "\n")
cat("列数：", ncol(qq), "\n")
cat("key 缺失数：", sum(is.na(qq$key)), "\n")
cat("mode 取值：", paste(levels(qq$mode), collapse = "/"), "\n\n")
print(str(qq, give.attr = FALSE))
