import "../styles/dashboard.css";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import {
  FaHome,
  FaUpload,
  FaHistory,
  FaSignOutAlt,
} from "react-icons/fa";

import ChartSection from "../components/ChartSection";

function Dashboard() {
  const navigate = useNavigate();

  return (
    <div className="dashboard-container">

      {/* Sidebar */}
      <div className="sidebar">
        <h2>MediLens</h2>

        <hr />

        <p onClick={() => navigate("/dashboard")}>
          <FaHome /> Dashboard
        </p>

        <p onClick={() => navigate("/upload")}>
          <FaUpload /> Upload Report
        </p>

        <p onClick={() => navigate("/history")}>
          <FaHistory /> History
        </p>

        <p onClick={() => navigate("/")}>
          <FaSignOutAlt /> Logout
        </p>
      </div>

      {/* Main Content */}
      <div className="dashboard-content">

        <motion.div
          className="header"
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1>Welcome, Kanya 👋</h1>
          <p>AI Powered Medical Report Analyzer</p>
        </motion.div>

        {/* Dashboard Cards */}
        <div className="cards">

          <motion.div
            className="card"
            whileHover={{ scale: 1.05 }}
          >
            <h2>25</h2>
            <span>Total Reports</span>
          </motion.div>

          <motion.div
            className="card"
            whileHover={{ scale: 1.05 }}
          >
            <h2>18</h2>
            <span>AI Analyses</span>
          </motion.div>

          <motion.div
            className="card"
            whileHover={{ scale: 1.05 }}
          >
            <h2>3</h2>
            <span>Abnormal Reports</span>
          </motion.div>

        </div>

        {/* Action Buttons */}
        <div className="actions">

          <button onClick={() => navigate("/upload")}>
            📄 Upload Medical Report
          </button>

          <button onClick={() => navigate("/results")}>
            📊 View Analysis
          </button>

          <button onClick={() => navigate("/history")}>
            🕒 View History
          </button>

        </div>

        {/* Charts */}
        <ChartSection />

      </div>

    </div>
  );
}

export default Dashboard;