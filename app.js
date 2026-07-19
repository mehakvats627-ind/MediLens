const jwt = require("jsonwebtoken");
const bcrypt = require("bcrypt");
require("dotenv").config();

const express = require("express");
const { GoogleGenAI } = require("@google/genai");

require("./db");

const Report = require("./models/report");
const User = require("./models/users");

const auth = require("./middleware/auth");

const upload = require("./middleware/multer");
const extractText = require("./services/ocrService");

const app = express();

app.use(express.json());

// Gemini AI
const ai = new GoogleGenAI({
  apiKey: process.env.GEMINI_API_KEY,
});
// ============================
// POST REPORT
// ============================

app.post("/reports", auth, async (req, res) => {
  try {
    const { patientName, age, reportType } = req.body;

    if (!patientName || !age || !reportType) {
      return res.status(400).json({
        success: false,
        message: "Please fill all fields",
      });
    }

    // Generate AI Result
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash-lite",
      contents: `
Analyze this medical report.

Report Type: ${reportType}

Reply using ONLY ONE WORD.

Possible answers:
Normal
High
Low
Critical
      `,
    });

    const aiResult = response.text
      ? response.text.trim()
      : "No Response";

    // Save Report
    const newReport = new Report({
      patientName,
      age,
      reportType,
      aiResult,
      userId: req.user.userId,
    });

    await newReport.save();

    res.status(201).json({
      success: true,
      message: "Report saved successfully!",
      data: newReport,
    });
  } catch (err) {
    console.error("FULL ERROR:");
    console.error(err);

    res.status(500).json({
      success: false,
      message: "Error saving report",
      error: err.message,
    });
  }
});

// ============================
// GET ALL REPORTS
// ============================

app.get("/reports", auth, async (req, res) => {
  try {
    const reports = await Report.find({
      userId: req.user.userId,
    });

    res.json(reports);

  } catch (err) {
    res.status(500).json({
      success: false,
      error: err.message,
    });
  }
});

// UPDATE REPORT
app.put("/reports/:id", auth, async (req, res) => {
  try {
    const report = await Report.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true }
    );

    if (!report) {
      return res.status(404).json({
        success: false,
        message: "Report not found"
      });
    }

    res.status(200).json({
      success: true,
      data: report
    });

  } catch (err) {
    res.status(500).json({
      success: false,
      message: err.message
    });
  }
});

// DELETE REPORT
app.delete("/reports/:id", auth, async (req, res) => {
    try {
        const report = await Report.findByIdAndDelete(req.params.id);

        if (!report) {
            return res.status(404).json({
                success: false,
                message: "Report not found"
            });
        }

        res.status(200).json({
            success: true,
            message: "Report deleted successfully"
        });

    } catch (error) {
        res.status(500).json({
            success: false,
            message: error.message
        });
    }
});

// GET REPORT BY ID
app.get("/reports/:id", async (req, res) => {
  try {
    const report = await Report.findById(req.params.id);

    if (!report) {
      return res.status(404).json({
        success: false,
        message: "Report not found"
      });
    }

    res.status(200).json({
      success: true,
      data: report
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      message: error.message
    });
  }
});
// ============================
// USER SIGNUP
// ============================

app.post("/signup", async (req, res) => {
  try {
    const { name, email, password } = req.body;

    // Check if all fields are filled
    if (!name || !email || !password) {
      return res.status(400).json({
        success: false,
        message: "Please fill all fields",
      });
    }

    // Check if user already exists
    const existingUser = await User.findOne({ email });

    if (existingUser) {
      return res.status(400).json({
        success: false,
        message: "User already exists",
      });
    }

    // Hash the password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create user
    const newUser = new User({
      name,
      email,
      password: hashedPassword,
    });

    // Save user
    await newUser.save();

    res.status(201).json({
      success: true,
      message: "User registered successfully",
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});
// ============================
// USER LOGIN
// ============================

app.post("/login", async (req, res) => {
  try {
    const { email, password } = req.body;

    // Check if all fields are filled
    if (!email || !password) {
      return res.status(400).json({
        success: false,
        message: "Please fill all fields",
      });
    }

    // Find user by email
    const user = await User.findOne({ email });

    if (!user) {
      return res.status(404).json({
        success: false,
        message: "User not found",
      });
    }

    // Compare password
    const isMatch = await bcrypt.compare(password, user.password);

    if (!isMatch) {
      return res.status(401).json({
        success: false,
        message: "Invalid password",
      });
    }

    // Generate JWT Token
    const token = jwt.sign(
      { userId: user._id, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: "1h" }
    );

    res.status(200).json({
      success: true,
      message: "Login successful",
      token,
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

// Upload Report File
app.post("/upload", upload.single("report"), async (req, res) => {
    try {
        const extractedText = await extractText(req.file.path);
        const aiResponse = await ai.models.generateContent({
  model: "gemini-2.5-flash",
  contents: `
You are a medical assistant.

Explain this medical report in very simple English.

Medical Report:
${extractedText}

Also tell:
1. Which values look normal.
2. Which values look abnormal.
3. Give 3 simple health suggestions.

Do not diagnose diseases.
Always tell the user to consult a doctor.
`
});

const aiExplanation = aiResponse.text
  ? aiResponse.text.trim()
  : "No AI response";

        res.status(200).json({
            success: true,
            message: "File uploaded successfully",
            extractedText: extractedText,
            aiExplanation: aiExplanation
        });

    } catch (error) {
        res.status(500).json({
            success: false,
            message: error.message
        });
    }
});
// ============================
// START SERVER
// ============================

const PORT = 5000;

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});