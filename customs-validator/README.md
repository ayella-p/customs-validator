# 🚢 GreenLane AI — Customs Selectivity & Document Validator

**Turns raw import documents into automated customs lane recommendations (Green/Yellow/Red).**

## What It Does

GreenLane AI is an automated logistics and document intelligence tool that:
* **Extracts** key fields from images of Commercial Invoices and Bills of Lading using Vision AI.
* **Cross-references** the extracted data between documents to ensure absolute consistency.
* **Evaluates** the shipment against Philippine Bureau of Customs (BOC) logic for restricted items.
* **Outputs** an automated selectivity lane assignment (Green, Yellow, or Red) with a clear explanation.

## Fields Extracted & Compared

| Field | Document Source | Example |
| :--- | :--- | :--- |
| **Consignee Name** | Invoice & BOL | Ayella IT Solutions |
| **Total Value / Weight** | Invoice & BOL | 250 kg / $ 5000.00 |
| **Commodity Description** | Invoice & BOL | Standard Computer Keyboards |
| **Restricted Status** | Evaluated via AI | Clear (No restricted items) |

## Validation Checks

* ✅ **Identity Match:** Consignee name matches perfectly across all shipping documents.
* ✅ **Completeness:** Required values (Weights/Totals) and descriptions are present.
* ⚠️ **Yellow Lane Flag:** Any mismatch in data or missing fields triggers a Document Review requirement.
* 🚨 **Red Lane Flag:** Detection of restricted items (chemicals, unprocessed meat, firearms) triggers a mandatory Physical Inspection.

## Tech Stack

* **Python 3.10+**
* **Google Gemini API (gemini-2.5-flash)** — Multimodal AI for image-to-text extraction and logical reasoning.
* **Streamlit** — Interactive web interface and dashboard.
* **Pillow (PIL)** — Image handling and processing.
* **python-dotenv** — Secure environment variable management.

## Demo Output Example

**Input:** Uploaded images of a Commercial Invoice and a Bill of Lading.

**Output:**
```json
{
  "analysis_report": {
    "status": "🟢 GREEN LANE: Approved",
    "extracted_data": {
      "consignee_invoice": "Datos Solutions",
      "consignee_bol": "Datos Solutions",
      "commodity": "Standard Computer Keyboards",
      "restricted_items_detected": "None"
    },
    "explanation": "All key fields match perfectly between the Commercial Invoice and the Bill of Lading. No restricted commodities were detected in the description. Cleared for fast-tracked release."
  }
}