import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
let Presentation;
let PresentationFile;

const here = path.dirname(fileURLToPath(import.meta.url));
const workspaceDir = path.resolve(here, "..", "..");
const buildDir = path.join(workspaceDir, "artifacts", "a2_presentation", "build");
const previewDir = path.join(buildDir, "slides");
const outputDir = path.join(workspaceDir, "deliverables", "A2_PPT");
const finalPath = path.join(outputDir, "A2_Mushroom_模型与横向对比.pptx");
const runtimeNodeModules = "C:/Users/Beixc/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules";
const runtimePython = "C:/Users/Beixc/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe";
const skillDir = "C:/Users/Beixc/.codex/plugins/cache/openai-primary-runtime/presentations/26.1030.10813/skills/presentations";
const font = "Microsoft YaHei";

const C = {
  bg: "#F6F8F4",
  green: "#173D2F",
  green2: "#557F65",
  green3: "#91B49A",
  ink: "#25352D",
  muted: "#56665C",
  rule: "#D5DED6",
  row: "#EDF2ED",
  white: "#FFFFFF",
};

async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true });
}

async function readJson(rel) {
  return JSON.parse(await fs.readFile(path.join(workspaceDir, rel), "utf8"));
}

function readCsv(rel) {
  return fs.readFile(path.join(workspaceDir, rel), "utf8").then((raw) => {
    const [header, ...lines] = raw.trim().split(/\r?\n/);
    const keys = header.split(",");
    return lines.map((line) => {
      const cells = line.split(",");
      return Object.fromEntries(keys.map((key, i) => [key, cells[i]]));
    });
  });
}

function addText(slide, name, text, x, y, w, h, opts = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    name,
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    typeface: font,
    fontSize: opts.size ?? 23,
    color: opts.color ?? C.ink,
    bold: opts.bold ?? false,
    alignment: opts.align ?? "left",
    verticalAlignment: opts.vAlign ?? "top",
    autoFit: "shrinkText",
    wrap: "square",
    insets: 0,
  };
  return shape;
}

function addTitle(slide, title, subtitle = "") {
  addText(slide, "slide-title", title, 64, 42, 1148, 58, { size: 46, bold: true, color: C.green });
  if (subtitle) addText(slide, "slide-subtitle", subtitle, 66, 104, 1145, 36, { size: 22, color: C.muted });
}

function addTable(slide, values, x, y, w, h, columnWeights, rowHeights = []) {
  const rows = values.length;
  const cols = values[0].length;
  const table = slide.tables.add({
    rows,
    columns: cols,
    left: x,
    top: y,
    width: w,
    height: h,
    columnTracks: columnWeights.map((value) => ({ mode: "fr", value })),
    values,
  });
  table.borders.assign({ style: "solid", fill: C.rule, width: 1 });
  for (let r = 0; r < rows; r++) {
    if (rowHeights[r]) table.rows[r].height = rowHeights[r];
    for (let c = 0; c < cols; c++) {
      const cell = table.getCell(r, c);
      const header = r === 0;
      cell.fill = header ? C.green : (r % 2 === 1 ? C.white : C.row);
      cell.text.style = {
        typeface: font,
        fontSize: header ? 21 : 20,
        bold: header || c === 0,
        color: header ? C.white : C.ink,
        alignment: c === 0 ? "left" : "center",
        verticalAlignment: "middle",
        autoFit: "shrinkText",
        wrap: "square",
        insets: { top: 10, right: 10, bottom: 10, left: 12 },
      };
    }
  }
  return table;
}

function addNotes(slide, text) {
  slide.speakerNotes.text = text;
}

function addLearningCurve(slide, { title, rows, maxSize }) {
  const chart = slide.charts.add("line", {
    position: { left: 500, top: 162, width: 710, height: 410 },
    title,
    titlePlacement: "aboveChart",
    titleTextStyle: { fontSize: 21, fill: C.green, bold: true },
    categories: rows.map((row) => String(row.train_size)),
    series: [
      {
        name: "训练 F1",
        values: rows.map((row) => Number(Number(row.train_mean).toFixed(6))),
        line: { style: "solid", fill: C.green, width: 3 },
        marker: { symbol: "circle", size: 7, fill: C.green },
      },
      {
        name: "验证 F1",
        values: rows.map((row) => Number(Number(row.validation_mean).toFixed(6))),
        line: { style: "solid", fill: C.green3, width: 3 },
        marker: { symbol: "circle", size: 7, fill: C.green3 },
      },
    ],
    lineOptions: { grouping: "standard", smooth: false },
    hasLegend: true,
    legend: { position: "bottom", overlay: false, textStyle: { fontSize: 16, fill: C.muted } },
    xAxis: {
      title: { text: "训练样本数", textStyle: { fontSize: 15, fill: C.muted } },
      textStyle: { fontSize: 15, fill: C.muted },
      line: { style: "solid", fill: C.rule, width: 1 },
      majorGridlines: null,
    },
    yAxis: {
      title: { text: "F1（有毒类）", textStyle: { fontSize: 15, fill: C.muted } },
      min: 0,
      max: 1,
      majorUnit: 0.2,
      numberFormatCode: "0.0",
      textStyle: { fontSize: 15, fill: C.muted },
      line: { style: "solid", fill: C.rule, width: 1 },
      majorGridlines: { style: "solid", fill: C.rule, width: 1 },
    },
    chartFill: C.white,
    chartLine: { style: "solid", fill: C.rule, width: 1 },
    plotAreaFill: C.white,
    plotAreaLine: { style: "solid", fill: "none", width: 0 },
  });
  return chart;
}

function addSection(slide, label, body, y) {
  addText(slide, `${label}-label`, label, 66, y, 390, 30, { size: 22, color: C.green, bold: true });
  addText(slide, `${label}-body`, body, 66, y + 34, 398, 82, { size: 21, color: C.ink });
}

async function main() {
  if (await fs.stat(finalPath).then(() => true).catch(() => false)) {
    throw new Error(`Refusing to overwrite existing final deck: ${finalPath}`);
  }
  await Promise.all([ensureDir(buildDir), ensureDir(previewDir), ensureDir(outputDir)]);
  process.env.RUNTIME_NODE_MODULES = runtimeNodeModules;
  const linkPath = path.join(here, "node_modules");
  if (!(await fs.stat(linkPath).then(() => true).catch(() => false))) {
    await fs.symlink(runtimeNodeModules, linkPath, "junction");
  }
  ({ Presentation, PresentationFile } = await import("@oai/artifact-tool"));

  const [lrCurve, knnCurve, lrHoldout, lrCv, knnHoldout, knnCv, aprioriConfig] = await Promise.all([
    readCsv("artifacts/a2_mushroom/logistic_regression/logistic_regression_mushroom_f1_learning_curve.csv"),
    readCsv("artifacts/a2_mushroom/knn/knn_mushroom_f1_learning_curve.csv"),
    readJson("artifacts/a2_mushroom/logistic_regression/holdout_metrics.json"),
    readJson("artifacts/a2_mushroom/logistic_regression/cv_summary.json"),
    readJson("artifacts/a2_mushroom/knn/holdout_metrics.json"),
    readJson("artifacts/a2_mushroom/knn/cv_summary.json"),
    readJson("artifacts/a2_mushroom/apriori/run_config.json"),
  ]);

  const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });

  // 1. Experimental setup
  {
    const slide = presentation.slides.add();
    slide.background.fill = C.bg;
    addTitle(slide, "统一实验设置", "分类指标聚焦有毒类 p；Apriori 作为独立的无监督补充");
    addTable(slide, [
      ["环节", "统一口径"],
      ["数据与目标", "8,124 条样本，21 个有效名义属性；分类正类为有毒 p"],
      ["共享清洗", "stalk-root 缺失值众数补齐，删除单值 veil-type；清洗文件先于模型评估生成"],
      ["模型输入", "LR / KNN 按训练折 One-Hot 为 115 维；J48 保留名义输入并折内筛选 InfoGain top9"],
      ["验证与调参", "分层 10 折；主模型另做 80/20 holdout；seed=42；LR / KNN 外层 10 折、内层 5 折调参"],
      ["评价与边界", "有毒类 F1 为主、ROC-AUC 为辅；Weka 与 sklearn 折索引不同，仅比较汇总值"],
      ["Apriori", `全量数据描述性挖掘；support ≥ ${aprioriConfig.min_support.toFixed(2)}、confidence ≥ ${aprioriConfig.min_confidence.toFixed(2)}、项集长度 ≤ ${aprioriConfig.max_itemset_length}`],
    ], 64, 152, 1152, 460, [1.05, 4.95], [56, 60, 66, 72, 66, 64, 60]);
    addNotes(slide, `本页先统一口径。Mushroom 清洗后有 8124 条记录和 21 个有效名义属性，以有毒类 p 为正类。共享输入在建模前已经完成缺失填补和单值属性删除；逻辑回归与 KNN 的 One-Hot 编码、J48 的监督式 top9 特征筛选仍在训练折内完成。所有随机过程使用 seed 42。Weka 与 scikit-learn 的具体折索引不同，所以后面的四模型比较只看汇总值，不做逐样本配对推断。ZeroR 没有独立 holdout 结果。Apriori 用全量样本描述共现，不参与分类排名。\n本地来源：docs/a2_presentation.md；docs/mushroom_model_comparison.md；docs/mushroom_report.md；artifacts/a2_mushroom/summary/results_summary.md；artifacts/a2_mushroom/apriori/run_config.json。`);
  }

  // 2. Logistic regression
  {
    const slide = presentation.slides.add();
    slide.background.fill = C.bg;
    addTitle(slide, "逻辑回归", "线性加权已经足以分离当前基准数据中的两类");
    addSection(slide, "模型", "115 维 One-Hot 输入\nL2 正则与 lbfgs\nC 在 0.01–100 内搜索，holdout 选择 C=10", 162);
    addSection(slide, "结果", `10 折 F1 ${lrCv.metrics.f1.mean.toFixed(3)} ± ${lrCv.metrics.f1.std.toFixed(3)}\n10 折 ROC-AUC ${lrCv.metrics.roc_auc.mean.toFixed(3)}\nHoldout F1 ${lrHoldout.metrics.f1.toFixed(3)}`, 340);
    addLearningCurve(slide, { title: "F1 学习曲线", rows: lrCurve, maxSize: Number(lrCurve.at(-1).train_size) });
    addText(slide, "curve-caption", "当前子集顺序下，验证 F1 为 0.116–1.000；子集未 shuffle，曲线仅作描述，不作因果推断。", 505, 592, 700, 42, { size: 18, color: C.muted });
    addNotes(slide, `逻辑回归把 21 个名义属性转成 115 个 One-Hot 特征，用 L2 正则控制系数，并用 sigmoid 输出有毒概率。内层五折按 F1 选择 C；在独立 holdout 上记录 C=10。外层十折的 F1 和 ROC-AUC 均为 1.000，标准差为零，holdout F1 也为 1.000。曲线的训练 F1 始终为 1；当前训练规模子集顺序下，验证 F1 从 0.116 到 1.000。学习曲线使用未 shuffle 的顺序子集，因此这里只描述现有观测，不推断样本量带来的因果效果或强泛化。\n本地来源：docs/mushroom_report.md；artifacts/a2_mushroom/logistic_regression/cv_summary.json；artifacts/a2_mushroom/logistic_regression/holdout_metrics.json；artifacts/a2_mushroom/logistic_regression/logistic_regression_mushroom_f1_learning_curve.csv。`);
  }

  // 3. KNN
  {
    const slide = presentation.slides.add();
    slide.background.fill = C.bg;
    addTitle(slide, "KNN", "局部相似性也达到满分，但预测需要保留训练样本");
    addSection(slide, "模型", "One-Hot 后使用 Euclidean 距离\n搜索 k=1–20 与投票权重\nk=1–9 的验证 F1 并列为 1.000", 162);
    addSection(slide, "结果", `10 折 F1 ${knnCv.metrics.f1.mean.toFixed(3)} ± ${knnCv.metrics.f1.std.toFixed(3)}\n10 折 ROC-AUC ${knnCv.metrics.roc_auc.mean.toFixed(3)}\nHoldout F1 ${knnHoldout.metrics.f1.toFixed(3)}；记录 k=1、uniform`, 340);
    addLearningCurve(slide, { title: "F1 学习曲线", rows: knnCurve, maxSize: Number(knnCurve.at(-1).train_size) });
    addText(slide, "curve-caption", "当前子集顺序下，验证 F1 为 0.211–1.000；未 shuffle，曲线仅作描述，不作因果推断。", 505, 592, 700, 42, { size: 18, color: C.muted });
    addNotes(slide, `KNN 在 One-Hot 空间用欧氏距离寻找近邻，并按邻居类别投票。搜索范围是 k 从 1 到 20，同时比较 uniform 和 distance 权重。k 从 1 到 9 时验证 F1 均为 1，因此网格搜索记录的 k=1、uniform 只是并列时的首个组合，不代表唯一最优。十折和 holdout 指标都达到满分。学习曲线的训练 F1 对 k=1 天然为 1；当前未 shuffle 的训练规模子集顺序下，验证 F1 为 0.211 至 1.000。这里只描述已有观测，不推断样本量带来的因果效果或强泛化。与 LR 相比，KNN 没有带来新的预测收益，部署时还要保存训练数据并计算距离。\n本地来源：docs/mushroom_report.md；artifacts/a2_mushroom/knn/cv_summary.json；artifacts/a2_mushroom/knn/holdout_metrics.json；artifacts/a2_mushroom/knn/knn_mushroom_f1_learning_curve.csv。`);
  }

  // 4. Apriori
  {
    const slide = presentation.slides.add();
    slide.background.fill = C.bg;
    addTitle(slide, "Apriori", "类别关联补充分类证据，不参与 F1 排名");
    addText(slide, "apriori-count", `${aprioriConfig.frequent_itemsets.toLocaleString("en-US")} 个频繁项集   ${aprioriConfig.class_rules} 条类别规则`, 66, 156, 1145, 48, { size: 30, bold: true, color: C.green });
    addText(slide, "apriori-setting", `Support ≥ ${aprioriConfig.min_support.toFixed(2)}   Confidence ≥ ${aprioriConfig.min_confidence.toFixed(2)}   最大项集长度 ${aprioriConfig.max_itemset_length}`, 66, 210, 1145, 38, { size: 21, color: C.muted });
    addTable(slide, [
      ["类别规则", "Support", "Confidence", "Lift"],
      ["odor=f → class=p", "0.2659", "1.0000", "2.0746"],
      ["odor=n → class=e", "0.4195", "0.9660", "1.8649"],
    ], 66, 286, 1148, 205, [3.25, 1.25, 1.45, 1.05], [56, 72, 72]);
    addText(slide, "apriori-definitions", "Support：组合出现比例     Confidence：条件成立时的类别比例     Lift：相对独立情形的关联倍数", 66, 520, 1145, 46, { size: 21, color: C.ink });
    addText(slide, "apriori-limitation", "共现关系不证明因果，也不能作为现实蘑菇鉴定规则。", 66, 582, 1145, 35, { size: 21, color: C.green, bold: true });
    addNotes(slide, `Apriori 以 Support 0.20、Confidence 0.80 和最大项集长度 3 搜索，得到 1568 个频繁项集，其中筛出 104 条后件为类别的规则。odor=f 指向有毒类时 support 为 0.2659，confidence 为 1，lift 为 2.0746。odor=n 指向可食类的 support 为 0.4195，confidence 为 0.966，lift 为 1.8649。Support 衡量组合覆盖全体样本的比例，Confidence 衡量条件出现时类别的比例，Lift 比较实际共现与独立情况下的预期。这里使用全量数据做描述性发现，没有交叉验证，也不加入分类模型的 F1 排名。关联不代表因果，更不能把规则当成现实食用建议。\n本地来源：docs/apriori_analysis.md；docs/mushroom_model_comparison.md；artifacts/a2_mushroom/apriori/run_config.json；artifacts/a2_mushroom/apriori/results_summary.md。`);
  }

  // 5. Four-model comparison
  {
    const slide = presentation.slides.add();
    slide.background.fill = C.bg;
    addTitle(slide, "四模型横向对比", "F1 与 ROC-AUC 以有毒类为正类；ZeroR 仅作为多数类基线");
    addTable(slide, [
      ["模型", "10 折 F1", "10 折 ROC-AUC", "有毒漏检 FN", "Holdout F1", "结构与成本"],
      ["ZeroR", "0.0000*", "0.5000", "3,916", "未提供", "不看属性；始终预测多数类 e"],
      ["J48-top9", "1.0000", "1.0000", "0", "1.0000", "9 个属性、28 个叶节点；规则直观"],
      ["逻辑回归", "1.0000 ± 0", "1.0000 ± 0", "0", "1.0000", "115 维线性加权；一次加权求和"],
      ["KNN", "1.0000 ± 0", "1.0000 ± 0", "0", "1.0000", "保留训练集；预测时逐样本算距离"],
    ], 56, 156, 1160, 350, [1.25, 1.2, 1.55, 1.25, 1.2, 3.15], [58, 69, 69, 69, 69]);
    addText(slide, "zeror-note", "* ZeroR 原始 F1 未定义；本表按 zero_division=0 约定记为 0。51.80% Accuracy 来自多数类比例，不能识别有毒样本。", 62, 536, 1155, 36, { size: 19, color: C.muted });
    addText(slide, "fold-note", "Weka 与 sklearn 的折索引不同；不做跨工具逐样本显著性判断。ZeroR 无独立 holdout。", 62, 580, 1155, 36, { size: 19, color: C.muted });
    addNotes(slide, `四模型比较显示，ZeroR 的 F1 在零分母时原始值未定义，本表按 zero_division=0 约定显示为 0；ROC-AUC 为 0.5，漏掉 3916 个有毒样本。它虽然有 51.80% Accuracy，但只是多数类比例，不能作为有效鉴别模型。J48-top9、逻辑回归与 KNN 的 10 折 F1、ROC-AUC 以及已提供的 holdout F1 全部为 1，没有有毒漏检。ZeroR 没有 holdout 结果。由于 J48/ZeroR 来自 Weka，LR/KNN 来自 scikit-learn，折索引不完全相同，横向表只做汇总比较。\n本地来源：docs/mushroom_model_comparison.md；docs/mushroom_report.md；artifacts/a2_mushroom/logistic_regression/cv_summary.json；artifacts/a2_mushroom/knn/cv_summary.json；artifacts/a2_mushroom/summary/results_summary.md。`);
  }

  // 6. Model selection
  {
    const slide = presentation.slides.add();
    slide.background.fill = C.bg;
    addTitle(slide, "模型选择结论", "性能并列后，按小组约定优先比较模型结构与预测成本");
    addText(slide, "selection-rule", "选择顺序：有毒类 F1 → ROC-AUC → 更简单、预测成本更低", 66, 170, 1120, 46, { size: 26, bold: true, color: C.green });
    addText(slide, "recommendation", "推荐逻辑回归", 66, 258, 480, 56, { size: 38, bold: true, color: C.green });
    addText(slide, "recommendation-reason", "与 J48-top9、KNN 同为满分；无需监督式特征筛选，线性加权即可预测，并能直接输出有毒概率。", 66, 326, 1090, 88, { size: 25, color: C.ink });
    addText(slide, "alternative", "可解释性优先时，选 J48-top9：9 个属性、28 个叶节点，规则更直观。", 66, 454, 1100, 54, { size: 23, color: C.ink });
    addText(slide, "scope", "适用范围：UCI Mushroom 基准数据与当前实验协议；满分结果不构成现实蘑菇鉴定的安全保证。", 66, 548, 1100, 62, { size: 23, bold: true, color: C.green });
    addNotes(slide, `按团队规则先看有毒类 F1，再看 ROC-AUC，最后比较更简单、预测成本更低的方案。三个有效候选在当前指标下完全并列，因此推荐逻辑回归。它使用直接的编码与线性预测流程，不依赖额外特征选择，能输出有毒概率，推理计算成本低。若需要一眼能展示的判断规则，J48-top9 是可解释性更强的替代。KNN 证明局部相似性也能达到满分，但没有提供额外预测收益，而且需要保存训练样本并逐条计算距离。最后要限定结论：这是 UCI Mushroom 基准数据上的实验结果，不能外推成现实蘑菇鉴别的安全保证。\n本地来源：docs/mushroom_model_comparison.md；docs/mushroom_report.md；docs/a2_presentation.md。`);
  }

  const chartFontUtil = await import(pathToFileURL(path.join(skillDir, "container_tools", "artifact_tool_utils.mjs")).href);
  for (const slide of presentation.slides.items) {
    for (const chart of slide.charts.items) {
      chartFontUtil.applyPresentationChartFont(chart, { fontFamily: font });
    }
  }

  for (const [index, slide] of presentation.slides.items.entries()) {
    const png = await presentation.export({ slide, format: "png", scale: 1 });
    await fs.writeFile(path.join(previewDir, `slide-${String(index + 1).padStart(2, "0")}.png`), new Uint8Array(await png.arrayBuffer()));
  }

  const stagingDir = path.join(buildDir, ".codex-finalizer");
  await ensureDir(stagingDir);
  const candidatePath = path.join(stagingDir, "candidate.pptx");
  await (await PresentationFile.exportPptx(presentation)).save(candidatePath);
  const { finalizePresentation } = await import(pathToFileURL(path.join(skillDir, "container_tools", "artifact_tool_utils.mjs")).href);
  await finalizePresentation({
    explicitTotalSlideCount: 6,
    requiredNativeTableOwnerSlides: [1, 4, 5],
    requiredNativeChartOwnerSlides: [2, 3],
    workspaceDir,
    candidatePath,
    finalPath,
    pythonExecutable: runtimePython,
    integrityValidatorPath: path.join(skillDir, "container_tools", "inspect_presentation_package_integrity.py"),
    layoutValidatorPath: path.join(skillDir, "container_tools", "inspect_presentation_layout_geometry.py"),
    layoutArgs: [
      "--expected-slide-size-emu", "12192000,6858000",
      "--validate-bullet-geometry",
      "--validate-heading-fit",
      "--require-native-table-slide", "1",
      "--require-native-table-slide", "4",
      "--require-native-table-slide", "5",
    ],
    fontPolicy: { basis: "design", families: [font] },
    verifyArtifactToolImport: true,
    materializeLiteralChartWorkbooks: true,
    receiptPath: path.join(stagingDir, "A2_Mushroom_validation.json"),
  });

  const inspection = await presentation.inspect({ kind: "slide,textbox,table,chart,notes", maxChars: 50000 });
  await fs.writeFile(path.join(buildDir, "deck-inspect.ndjson"), inspection.ndjson, "utf8");
  await fs.writeFile(path.join(buildDir, "build-summary.json"), JSON.stringify({
    finalPath,
    slides: presentation.slides.items.length,
    nativeTables: [1, 4, 5],
    nativeCharts: [2, 3],
    sourceCsvs: [
      "artifacts/a2_mushroom/logistic_regression/logistic_regression_mushroom_f1_learning_curve.csv",
      "artifacts/a2_mushroom/knn/knn_mushroom_f1_learning_curve.csv",
    ],
    sourceReports: ["docs/a2_presentation.md", "docs/mushroom_model_comparison.md", "docs/mushroom_report.md", "docs/apriori_analysis.md"],
  }, null, 2), "utf8");
  console.log(`Created ${finalPath}`);
  console.log(`Rendered ${presentation.slides.items.length} slide previews to ${previewDir}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
