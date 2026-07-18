import "../styles/upload.css";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaCloudUploadAlt } from "react-icons/fa";

function Upload() {
  const navigate = useNavigate();

  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = () => {
    if (!file) {
      alert("Please select a medical report first.");
      return;
    }

    setLoading(true);

    // Fake AI Processing
    setTimeout(() => {
      setLoading(false);
      navigate("/results");
    }, 3000);
  };

  return (
    <div className="upload-page">
      <div className="upload-card">

        <h1>Upload Medical Report</h1>

        <p>
          Upload your PDF or image report and let our AI
          analyze it within seconds.
        </p>

        <div className="upload-box">

          <FaCloudUploadAlt
            size={70}
            color="#3b82f6"
            style={{ marginBottom: "20px" }}
          />

          <input
            type="file"
            accept=".pdf,.jpg,.jpeg,.png"
            onChange={(e) => setFile(e.target.files[0])}
          />

          {!file ? (
            <h3>No file selected</h3>
          ) : (
            <h3>{file.name}</h3>
          )}

        </div>

        <button
          onClick={handleUpload}
          disabled={loading}
        >
          {loading
            ? "🤖 AI is Analyzing..."
            : "Analyze Report"}
        </button>

      </div>
    </div>
  );
}

export default Upload;