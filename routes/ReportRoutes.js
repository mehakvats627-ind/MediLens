const express = require("express");

const router = express.Router();

const {
    createReport,
    getReports,
    updateReport,
    deleteReport
} = require("../controllers/reportcontroller");

router.post("/reports", createReport);

router.get("/reports", getReports);

router.put("/reports/:id", updateReport);

router.delete("/reports/:id", deleteReport);

module.exports = router;