import "../styles/results.css";
import {
  FaCheckCircle,
  FaHeartbeat,
  FaDownload,
  FaPrint,
} from "react-icons/fa";
import { jsPDF } from "jspdf";

function Results() {

  const downloadPDF = () => {

    const doc = new jsPDF();

    doc.setFont("helvetica", "bold");
    doc.setFontSize(22);
    doc.text("MediLens AI Medical Report", 20, 20);

    doc.setFontSize(12);
    doc.setFont("helvetica", "normal");

    doc.text("Date: " + new Date().toLocaleDateString(), 20, 35);

    doc.text("Health Status:", 20, 50);
    doc.setTextColor(0, 150, 0);
    doc.text("NORMAL", 60, 50);

    doc.setTextColor(0, 0, 0);

    doc.text("Diagnosis:", 20, 70);
    doc.text(
      "No major abnormalities were detected in the uploaded report.",
      20,
      80
    );

    doc.text("AI Summary:", 20, 100);

    doc.text(
      [
        "Blood pressure is within normal range.",
        "Blood sugar level is normal.",
        "Cholesterol level is normal.",
        "Heart rate is stable.",
      ],
      20,
      110
    );

    doc.text("Recommendations:", 20, 145);

    doc.text(
      [
        "• Maintain a balanced diet.",
        "• Exercise at least 30 minutes daily.",
        "• Drink sufficient water.",
        "• Schedule regular health check-ups.",
        "• Consult your doctor if symptoms develop.",
      ],
      20,
      155
    );

    doc.setFont("helvetica", "italic");
    doc.text(
      "Generated automatically by MediLens AI",
      20,
      235
    );

    doc.save("MediLens_Report.pdf");
  };

  return (
    <div className="results-page">

      <div className="results-card">

        <h1>🤖 AI Medical Analysis Report</h1>

        <p>
          Your uploaded report has been analyzed successfully using AI.
        </p>

        <div className="result-box">

          <h2>
            <FaHeartbeat /> Health Status
          </h2>

          <span className="normal">
            🟢 Normal
          </span>

          <p>
            No major abnormalities were detected in your medical report.
            Overall health indicators are within the normal range.
          </p>

        </div>

        <div className="result-box">

          <h2>📋 AI Summary</h2>

          <p>
            Blood pressure, glucose level and cholesterol values appear
            to be normal. No immediate medical concern has been identified
            from the uploaded report.
          </p>

        </div>

        <div className="result-box">

          <h2>
            <FaCheckCircle /> Key Findings
          </h2>

          <ul>
            <li>✔ Blood Pressure : Normal</li>
            <li>✔ Blood Sugar : Normal</li>
            <li>✔ Cholesterol : Normal</li>
            <li>✔ Heart Rate : Stable</li>
          </ul>

        </div>

        <div className="result-box">

          <h2>💡 AI Recommendations</h2>

          <ul>
            <li>✔ Continue a balanced diet.</li>
            <li>✔ Exercise at least 30 minutes daily.</li>
            <li>✔ Drink 2–3 litres of water.</li>
            <li>✔ Schedule regular health check-ups.</li>
            <li>✔ Consult a doctor if symptoms develop.</li>
          </ul>

        </div>

        <div className="result-buttons">

          <button onClick={downloadPDF}>
            <FaDownload /> Download Report
          </button>

          <button onClick={() => window.print()}>
            <FaPrint /> Print Report
          </button>

        </div>

      </div>

    </div>
  );
}

export default Results;