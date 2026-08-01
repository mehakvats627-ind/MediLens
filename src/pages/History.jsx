import "../styles/history.css";
import { useNavigate } from "react-router-dom";
import { FaSearch, FaEye, FaTrash} from "react-icons/fa";
import { useState , useEffect } from "react";
import api from "../api";

function History() {
  const navigate = useNavigate();

  const [reports, setReports] = useState([]);

  useEffect(() => {
  const fetchReports = async () => {
    try {
      const response = await api.get("/reports");
      setReports(response.data.data);
    } catch (error) {
      console.log(error);
      alert("Failed to load reports");
    }
  };

  fetchReports();
}, []);

  const [search, setSearch] = useState("");

  const filteredReports = reports.filter((report) =>
  (
    report.fileName ||
    report.status ||
    report.explanation ||
    ""
  )
    .toLowerCase()
    .includes(search.toLowerCase())
);

const deleteReport = async (id) => {

  const confirmDelete = window.confirm(
    "Are you sure you want to delete this report?"
  );

  if (!confirmDelete) return;

  try {

    await api.delete(`/reports/${id}`);

    setReports(reports.filter((report) => report._id !== id));

    alert("Report deleted successfully");

  } catch (error) {

    console.log(error);

    alert("Delete failed");

  }

};
  return (
    <div className="history-page">
      <div className="history-card">

        <h1>📄 Medical Report History</h1>
        <p>View all previously analyzed reports.</p>

        <div className="search-box">
          <FaSearch />
          <input
            type="text"
            placeholder="Search reports..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <table>

          <thead>
            <tr>
              <th>Report</th>
              <th>Date</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>

          <tbody>

            {filteredReports.length > 0 ? (
              filteredReports.map((report) => (
                <tr key={report._id}>

                  <td>{report.fileName}</td>

                  <td>{new Date(report.createdAt).toLocaleDateString()}</td>

                  <td>
                    <span
                      className={
                        report.status === "Normal"
                          ? "normal"
                          : report.status === "Abnormal"
                          ? "abnormal"
                          : "pending"
                      }
                    >
                      {report.status}
                    </span>
                  </td>

                  <td>

<button
onClick={() =>
navigate("/results", {
state: report,
})
}
>
<FaEye /> View
</button>

<button
onClick={() => deleteReport(report._id)}
style={{
marginLeft:"10px",
background:"#dc3545"
}}
>
<FaTrash /> Delete
</button>

</td>

                </tr>
              ))
            ) : (
              <tr>
                <td
                  colSpan="4"
                  style={{
                    textAlign: "center",
                    padding: "30px",
                    color: "white",
                  }}
                >
                  No reports found.
                </td>
              </tr>
            )}

          </tbody>

        </table>

      </div>
    </div>
  );
}

export default History;