import xml.etree.ElementTree as ET
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


def evaluate_causality(narrative):
  """Evaluates WHO-UMC causality terms in clinical narratives."""
  text = narrative.lower()
  if "confirmed" in text or "certain" in text:
    return "Certain"
  elif "likely" in text or "probable" in text:
    return "Probable / Likely"
  elif "possible" in text:
    return "Possible"
  return "Unlikely / Unclassified"


def generate_e2b_xml(case_id, drug, reaction, causality):
  """Generates structured E2B(R3) XML draft format."""
  root = ET.Element("ichicsr", lang="en")
  safetyreport = ET.SubElement(root, "safetyreport")

  ET.SubElement(safetyreport, "safetyreportid").text = case_id
  patient = ET.SubElement(safetyreport, "patient")
  ET.SubElement(patient, "patientonsetage").text = "45"

  drug_node = ET.SubElement(safetyreport, "drug")
  ET.SubElement(drug_node, "medicinalproduct").text = drug

  reaction_node = ET.SubElement(safetyreport, "reaction")
  ET.SubElement(reaction_node, "primarysourcereaction").text = reaction

  evaluation = ET.SubElement(safetyreport, "causalityevaluation")
  ET.SubElement(evaluation, "whocausality").text = causality

  return ET.tostring(root, encoding="unicode")


@app.route("/", methods=["GET", "POST"])
def index():
  if request.method == "POST":
    narrative = request.form.get("narrative", "")
    causality = evaluate_causality(narrative)
    xml_draft = generate_e2b_xml(
        "AE-2026-001", "Suspect-Drug-A", "Acute Adverse Event", causality
    )
    return jsonify({
        "meddra_suggestion": "Hepatic enzyme increased (10019805)",
        "causality_score": causality,
        "e2b_xml_preview": xml_draft,
    })
  return render_template("index.html")


if __name__ == "__main__":
  app.run(debug=True)
