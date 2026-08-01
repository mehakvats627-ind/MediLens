import "../styles/upload.css";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaCloudUploadAlt } from "react-icons/fa";
import api from "../api";
 
function Upload() {
  const navigate = useNavigate();

  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

const handleUpload = async () => {
  if (!file) {
    alert("Please select a file to upload");
    return;
  }

  setLoading(true);

  try {
    const formData = new FormData();
    formData.append("report", file);

    const response = await api.post("/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    console.log(response.data);

    setLoading(false);

    alert("Report Uploaded Successfully!");

    navigate("/results", {
      state: response.data,
    });

  } catch (error) {
    setLoading(false);

    alert(error.response?.data?.message || "Upload Failed");
  }
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