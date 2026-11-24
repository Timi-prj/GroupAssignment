# Assignment 3：修改封面并重导出

在 `assignment3_cover.md` 修改学号。提交前确认所有待填项及各成员贡献。R 依赖为 `ISLR2`、`car`、`ggplot2`，图表由脚本从原始数据生成。

在统计作业目录运行：

```powershell
Rscript --vanilla R/assignment3.R
pandoc report/assignment3_cover.md report/assignment3_part_a.md report/assignment3_part_b.md report/assignment3_sources.md --standalone --embed-resources --css report/assignment3_print.css --metadata pagetitle='CDS533 Assignment 3' -o .trash/assignment3.html
```

在浏览器打开 `.trash/assignment3.html`，以 A4 打印保存 PDF，关闭浏览器默认页眉和页脚。最终只交 PDF 与单一 R 脚本。
