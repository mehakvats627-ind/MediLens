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

    status: {
      type: String,
      default: "Normal",
    },

    abnormalValues: [
      {
        test: String,
        value: String,
        reason: String,
      },
    ],

    normalValues: [
      {
        test: String,
        value: String,
      },
    ],

    disclaimer: {
      type: String,
      default:
        "This is not a diagnosis. Please consult a qualified doctor.",
    },

    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User",
    },
  },
  {
    timestamps: true,
  }
);

module.exports = mongoose.model("Report", reportSchema);