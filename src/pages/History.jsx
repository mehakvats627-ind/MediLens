import "../styles/history.css";
import { useNavigate } from "react-router-dom";
import { FaSearch, FaEye } from "react-icons/fa";
import { useState } from "react";

function History() {
  const navigate = useNavigate();

  const reports = [
    {
      id: 1,
      name: "Blood Test Report",
      date: "20 June 2026",
      status: "Normal",
    },
    {
      id: 2,
      name: "CBC Report",
      date: "18 June 2026",
      status: "Abnormal",
    },
    {
      id: 3,
      name: "X-Ray Report",
      date: "15 June 2026",
      status: "Normal",
    },
    {
      id: 4,
      name: "MRI Scan",
      date: "10 June 2026",
      status: "Pending",
    },
  ];

  const [search, setSearch] = useState("");

  const filteredReports = reports.filter((report) =>
    report.name.toLowerCase().includes(search.toLowerCase())
  );

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
                <tr key={report.id}>

                  <td>{report.name}</td>

                  <td>{report.date}</td>

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
                    <button onClick={() => navigate("/results")}>
                      <FaEye /> View
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