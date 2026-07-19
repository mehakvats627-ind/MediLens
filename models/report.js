const mongoose = require("mongoose");

const reportSchema = new mongoose.Schema(
  {
    patientName: {
      type: String,
      required: true,
    },
    age: {
      type: Number,
      required: true,
    },
    reportType: {
      type: String,
      required: true,
    },
    aiResult: {
      type: String,
      required: true,
    },
    userId: {
  type: mongoose.Schema.Types.ObjectId,
  ref: "User"
}
  },
  {
    timestamps: true,
  }
);

module.exports = mongoose.model("Report", reportSchema);