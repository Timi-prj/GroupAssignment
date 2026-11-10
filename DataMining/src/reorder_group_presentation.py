from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "deliverables" / "CDS535_Group.pptx"
ORDER = [
    1, 2, 3,
    5, 6, 17, 18, 7, 8, 9, 19, 11, 12, 15, 13, 14,
    20, 22, 23, 24, 25, 27, 28, 29, 30, 31, 32, 34, 35, 36, 37,
    39, 40, 41, 26, 42, 43,
    44, 45, 46,
]
SPEAKERS = {
    **{n: "A1 · HE HAODONG" for n in range(5, 10)},
    **{n: "A2 · BEI XUECHENG" for n in range(11, 16)},
    17: "A3 · GU RUIQI",
    18: "A3 · GU RUIQI",
    19: "A3 · GU RUIQI",
    **{n: "B1 · GONG TINGLU" for n in range(22, 33)},
    **{n: "B2 · HE MINGEN" for n in range(34, 38)},
    **{n: "B3 · HU SHUAISHUAI" for n in range(39, 44)},
    44: "GROUP",
    45: "GROUP",
}


def set_text(shape, text):
    if shape.has_text_frame and len(shape.text_frame.paragraphs) == 1:
        paragraph = shape.text_frame.paragraphs[0]
        if len(paragraph.runs) == 1:
            paragraph.runs[0].text = text
            return
    shape.text = text


def delete_shape(shape):
    element = shape._element
    element.getparent().remove(element)


def add_badge(slide, label):
    badge = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(10.72), Inches(0.20), Inches(2.10), Inches(0.34),
    )
    badge.name = f"Presenter badge - {label}"
    badge.fill.solid()
    badge.fill.fore_color.rgb = RGBColor(37, 99, 235)
    badge.line.fill.background()
    badge.text_frame.clear()
    badge.text_frame.margin_left = Inches(0.08)
    badge.text_frame.margin_right = Inches(0.08)
    badge.text_frame.margin_top = 0
    badge.text_frame.margin_bottom = 0
    badge.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    paragraph = badge.text_frame.paragraphs[0]
    paragraph.alignment = PP_ALIGN.CENTER
    run = paragraph.add_run()
    run.text = label
    run.font.name = "Aptos"
    run.font.size = Pt(9)
    run.font.bold = True
    run.font.color.rgb = RGBColor(255, 255, 255)


prs = Presentation(DECK)
assert len(prs.slides) == 46, "The raw 46-slide deck is required"
slides = list(prs.slides)

contents = {
    "·  Dataset introduction & preprocessing — A1 He Haodong": "·  Dataset, preprocessing & ZeroR baseline",
    "·  KNN classification & Apriori association rules — A2 Bei Xuecheng": "·  J48, Logistic Regression, KNN & model comparison",
    "·  ZeroR baseline & logistic regression — A3 Gu Ruiqi": "·  Apriori association rules",
    "·  Dataset · Preprocessing · Four-model comparison · J48 — B1 Gong Tinglu": "·  Dataset, preprocessing & J48 analysis",
    "·  Random Forest vs Logistic Regression — B2 He Mingen": "·  Random Forest, Logistic Regression & RBF-SVM",
    "·  Feature scan · PCA · Evaluation protocols · KMeans — B3 Hu Shuaishuai": "·  Model comparison, evaluation protocols & KMeans",
}
for shape in slides[1].shapes:
    if hasattr(shape, "text") and shape.text in contents:
        set_text(shape, contents[shape.text])

for slide_number, workflow in (
    (3, "Data  →  Preprocessing  →  Classification  →  Association Rules"),
    (20, "Data  →  Preprocessing  →  Classification  →  Clustering"),
):
    slide = slides[slide_number - 1]
    for shape in list(slide.shapes):
        if not hasattr(shape, "text"):
            continue
        if shape.text == "Presenters":
            set_text(shape, "Presentation Flow")
        elif shape.text.strip().startswith(("A1", "A2", "A3", "B1", "B2", "B3")):
            delete_shape(shape)
    textbox = slide.shapes.add_textbox(Inches(0.83), Inches(3.72), Inches(7.3), Inches(0.8))
    textbox.text_frame.word_wrap = True
    run = textbox.text_frame.paragraphs[0].add_run()
    run.text = workflow
    run.font.name = "Aptos"
    run.font.size = Pt(20)
    run.font.color.rgb = RGBColor(25, 73, 66)

for shape in slides[8].shapes:
    if not hasattr(shape, "text"):
        continue
    if shape.text == "05 · CONCLUSION & HANDOFF":
        set_text(shape, "05 · CONCLUSION")
    elif shape.text == "Three takeaways for my part, and the interface I hand over":
        set_text(shape, "Three takeaways from the J48 internal selection")
    elif shape.text == "HANDOFF":
        set_text(shape, "SHARED PROTOCOL")
    elif shape.text.startswith("Over to A2"):
        set_text(shape, "The same cleaned data, stratified folds and seed are reused for logistic regression and KNN, keeping the subsequent model comparison consistent.")

for shape in slides[31].shapes:
    if hasattr(shape, "text") and shape.text.startswith("That concludes my section"):
        set_text(shape, "J48 provides the interpretable baseline for the following model comparison.")

for slide_number in range(5, 10):
    for shape in list(slides[slide_number - 1].shapes):
        if getattr(shape, "text", "") == "CDS535 · DATAWARTS":
            delete_shape(shape)
for slide_number in range(11, 16):
    for shape in list(slides[slide_number - 1].shapes):
        if getattr(shape, "text", "") == "A2 · MUSHROOM":
            delete_shape(shape)
for slide_number in range(34, 38):
    for shape in list(slides[slide_number - 1].shapes):
        if getattr(shape, "text", "") == "Model Card  ·  B2 HE Mingen":
            delete_shape(shape)

comparison = slides[43]
comparison_text = {
    "Mushroom × Ionosphere Comparison Report": "Mushroom × Ionosphere Shared-Model Comparison",
    "Dimension": "Shared model / dimension",
    "Scale": "J48 / Decision Tree · F1 / ROC-AUC",
    "8,124 samples × 22 attributes": "1.000 / 1.000",
    "351 samples × 34 attributes": "0.933 / 0.907",
    "Attribute Type": "Logistic Regression · F1 / ROC-AUC",
    "All nominal (multi-valued)": "1.000 / 1.000",
    "Continuous numeric (17 × 2 complex pulses)": "0.914 / 0.897",
    "Class Distribution": "Why J48 changes",
    "51.8 : 48.2; nearly balanced": "Strong nominal rules split easily",
    "64 : 36; mildly imbalanced": "Single tree is less stable on small numeric data",
    "Representative Methods": "Why Logistic Regression changes",
    "KNN · Apriori · ZeroR · Logistic Regression": "Linear weighting is sufficient",
    "RBF-SVM · J48 · Random Forest · KMeans": "The boundary is more complex and nonlinear",
    "Best Results": "Final selection",
    "J48-top9 / Logistic Regression / KNN: F1 = 1.000": "Logistic Regression · F1 = 1.000",
    "SVM(smote) accuracy 0.943 | RF ROC-AUC 0.9497": "RBF-SVM · F1 = 0.956 · ROC-AUC = 0.980",
    "Key Bottleneck": "Is extra complexity worthwhile?",
    "Feature redundancy — top-9 features suffice for perfect classification": "No additional gain; choose the simpler model after perfect ties",
    "Small-sample, high-dimensional nonlinearity — preprocessing and evaluation protocols matter significantly": "Yes; the nonlinear kernel matches the numeric boundary",
}
for shape in comparison.shapes:
    text = getattr(shape, "text", "")
    if text in comparison_text:
        set_text(shape, comparison_text[text])
    elif text.startswith("Shared conclusion:"):
        set_text(shape, "Shared conclusion: model advantage depends on whether its inductive bias matches the data structure—not on complexity alone. Both datasets use stratified 10-fold CV and seed = 42.")

for original_number, slide in enumerate(slides, 1):
    if original_number in SPEAKERS:
        add_badge(slide, SPEAKERS[original_number])

slide_ids = list(prs.slides._sldIdLst)
for slide_id in slide_ids:
    prs.slides._sldIdLst.remove(slide_id)
for original_number in ORDER:
    prs.slides._sldIdLst.append(slide_ids[original_number - 1])

output = DECK.with_suffix(".tmp.pptx")
prs.save(output)
output.replace(DECK)
print(f"Saved {len(ORDER)} slides to {DECK}; all original content slides retained")
