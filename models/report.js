const mongoose = require("mongoose");

const reportSchema = new mongoose.Schema(
  {
    fileName: {
      type: String,
      required: true,
    },
    extractedText: {
      type: String,
      required: true,
    },
    explanation: {
      type: String,
      required: true,
    },
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User",
    }
  },
  {
    timestamps: true,
  }
);

module.exports = mongoose.model("Report", reportSchema);