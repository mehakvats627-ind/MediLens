import "../styles/results.css";
import {
  FaCheckCircle,
  FaHeartbeat,
  FaDownload,
  FaPrint,
} from "react-icons/fa";
import { jsPDF } from "jspdf";
import { useLocation } from "react-router-dom";

function Results() {
  const location = useLocation();

const report = location.state || {};

const explanation = report.explanation || "No AI analysis available.";

const extractedText = report.extractedText || "No extracted text available.";

const status = report.status || "Normal";

const abnormalValues = report.abnormalValues || [];

const normalValues = report.normalValues || [];

const disclaimer =
  report.disclaimer ||
  "This is not a diagnosis. Please consult a qualified doctor.";

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
    doc.text(status.toUpperCase(), 60, 50);

    doc.setTextColor(0, 0, 0);

    doc.text("AI Summary:", 20, 70);

doc.text(
  explanation.substring(0, 100),
  20,
  80
);


    doc.text("AI Summary:", 20, 100);

    doc.text(
  [
   explanation.substring(0,100),
  ],
   20,
   110
  );

    doc.text("Abnormal Values:",20,140);

    abnormalValues.forEach((item,index)=>{
    doc.text(
    `${item.test}: ${item.value}`,
    20,
    150 + index*10
    );
  });

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
          {status === "Normal" ? "🟢" :
         status === "Low" ? "🟡" :
         status === "High" ? "🟠" :
         "🔴"} {status}
          </span>

          <p>
            AI analyzed health status based on uploaded medical report.
          </p>

        </div>

        <div className="result-box">

          <h2>📋 AI Summary</h2>
          <p>{explanation}</p>

        </div>
          <div className="result-box">

         <h2>⚠️ Abnormal Values</h2>

         <ul>
        {
         abnormalValues.length > 0 ? (
         abnormalValues.map((item,index)=>(
         <li key={index}>
         <b>{item.test}</b> : {item.value}
         <br/>
          Reason: {item.reason}
         </li>
         ))
         )
         :
         (
         <li>No abnormal values found</li>
         )
         }

         </ul>

         </div>
         
         <div className="result-box">

           <h2>📄 Extracted Report Text</h2>

            <p>{extractedText}</p>

         </div>

        <div className="result-box">

          <h2>
            <FaCheckCircle /> Key Findings
          </h2>

          <ul>
         {
          normalValues.length > 0 ? (
          normalValues.map((item,index)=>(
          <li key={index}>
          ✔ {item.test} : {item.value}
        </li>
       ))
        ) : (
       <li>No normal values detected</li>
       )
       }
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
        <div className="result-box">

        <h2>⚠️ Disclaimer</h2>

       <p>
       {disclaimer}
       </p>

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