# A2 PPT 需求与制作方案

## 已确认范围

制作6页可编辑中文PPT，直接并入小组汇报，无独立封面、数据介绍页或附录。顺序为统一实验设置、逻辑回归、KNN、Apriori、Mushroom四模型横向对比、模型选择结论。A2负责逻辑回归、KNN与Apriori。讲稿约3分钟，写入备注。

## 证据与口径

以 docs/mushroom_model_comparison.md、docs/mushroom_section_outline.md 和 artifacts/a2_mushroom 原始指标为依据。分类正类为有毒p，横向比较ZeroR、J48-top9、逻辑回归、KNN。Apriori展示Support、Confidence、Lift，不加入分类排名。SVM不展示。

保留跨工具折索引不同、全数据预处理限制和基准结果的外推边界。成本比较采用结构分析，不将不同协议计时当作公平速度测试。

## 开发方案

使用 @oai/artifact-tool 的JavaScript接口生成原生文本、表格与数据曲线，浅底深绿、16:9。源代码位于src/a2_presentation，临时构建及验证位于artifacts/a2_presentation，最终PPT位于deliverables/A2_PPT。

按项目指令委派Luna Max编码，并由全新上下文的同模型同强度子Agent独立审查。渲染检查每页，验证数值与源材料一致。
