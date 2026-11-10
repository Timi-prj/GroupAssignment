# Group Assignment 1 文件路由

- `docs/CDS_534_Database_Management_Group_Project_Requirement.pdf` — 作业原始要求、Topic 3 参考 DDL/查询、SQL 概念题及评分标准；核对交付范围与合规性时读取。
- `docs/report_sections/Section5_Evaluation_final.docx` — 最终报告的第 5 章评估草稿，含工作负载、数据集、基线、结果表和结论；撰写或核查 Evaluation 部分时读取。
- `docs/report_sections/M2_Business_Analysis_original.docx` — M2 业务分析原稿，含另一套未实现字段、查询、数据集和实验占位符；仅用于追溯原稿，不应直接并入最终报告。
- `docs/report_sections/Sections1_3_6_Extract.md` — 从 M2 原稿提炼并与当前六表 SQL、Section 5 实测结果对齐的 §1/§3/§6 英文报告素材；合并业务背景、设计目标、架构权衡和局限性时优先读取。
- `sql/CDS534_Topic3_Gym.sql` — 当前完整数据库构建脚本，包含 6 表 DDL、样例数据和最终三条查询；实际建库、验证数据或修改 SQL 时读取。末尾元数据查询库名仍待修正。
- `sql/legacy/CDS534_Topic3_Gym_QUERY_legacy.sql` — 旧版三条查询，Q2/Q3 与最终查询语义不同；仅用于追溯，不作为最终提交脚本。
- `diagrams/CDS534_Topic3_ER.drawio` — 旧版 ER 图源文件，Member–Class 关系与外键标记尚不符合最终设计；修改 ER 或追溯源文件时读取，提交前须替换为新版定稿。
- `evidence/query_results_legacy/query_1.png` — 旧版 Q1 查询结果截图；Q1 语义与最终版一致，可用于核对 28 条结果。
- `evidence/query_results_legacy/query_2.png` — 旧版 Q2 查询结果截图；无课教练显示 NULL，不代表最终版显示 0 的结果。
- `evidence/query_results_legacy/query_3.png` — 旧版 Q3 查询结果截图；按会员统计且未体现降序，不代表最终版按会员类型汇总的结果。

## 当前提交判断

完整 SQL 已通过 MySQL 8.0.12 实际运行验证；旧 SQL 与旧截图仅作留档。最终报告 PDF、样例数据截图、新版 ER 定稿文件及最终三条查询截图尚未齐备。
