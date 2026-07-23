const express = require("express");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
require("dotenv").config();

require("./db");

const User = require("./models/users");
const Report = require("./models/report");
console.log(Report.schema.obj);

const auth = require("./middleware/auth");

const extractText = require("./services/ocrservice");

const app = express();


app.use(express.json());


// ===============================
// OPENROUTER AI FUNCTION
// ===============================

async function askAI(prompt) {
  const response = await fetch(
    "https://openrouter.ai/api/v1/chat/completions",
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${process.env.OPENROUTER_API_KEY}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: "google/gemini-2.0-flash-exp:free",
        messages: [
          {
            role: "user",
            content: prompt
          }
        ]
      })
    }
  );

  const data = await response.json();

  if (data.error) {
    throw new Error(data.error.message);
  }

  return data.choices[0].message.content;
}



// ===============================
// SIGNUP
// ===============================

app.post("/signup", async(req,res)=>{
try{

const {name,email,password}=req.body;

if(!name || !email || !password){
return res.status(400).json({
success:false,
message:"Fill all fields"
});
}


const exist=await User.findOne({email});

if(exist){
return res.status(400).json({
success:false,
message:"User already exists"
});
}


const hash=await bcrypt.hash(password,10);


const user=new User({
name,
email,
password:hash
});


await user.save();


res.json({
success:true,
message:"Signup successful"
});


}catch(error){

res.status(500).json({
success:false,
message:error.message
});

}

});



// ===============================
// LOGIN
// ===============================

app.post("/login", async(req,res)=>{

try{

const {email,password}=req.body;


const user=await User.findOne({email});


if(!user){

return res.status(404).json({
success:false,
message:"User not found"
});

}


const match=await bcrypt.compare(
password,
user.password
);


if(!match){

return res.status(401).json({
success:false,
message:"Wrong password"
});

}


const token=jwt.sign(
{
userId:user._id,
email:user.email
},
process.env.JWT_SECRET,
{
expiresIn:"1h"
  }
  );

  res.json({
  success:true,
  token
  });


  }catch(error){

  res.status(500).json({
  success:false,
  message:error.message
  });

}

});
const multer = require("multer");
const Tesseract = require("tesseract.js");
const axios = require("axios");
const fs = require("fs");


// File upload setup
const upload = multer({
    dest: "uploads/"
});


// Upload + OCR + OpenRouter AI Explanation API

app.post("/upload", upload.single("report"), async (req, res) => {

    try {

        const filePath = req.file.path;

        // OCR Reading
        const result = await Tesseract.recognize(
            filePath,
            "eng"
        );

        const extractedText = result.data.text;


        // OpenRouter AI Call
        const aiResponse = await axios.post(
            "https://openrouter.ai/api/v1/chat/completions",
            {
                model: "openai/gpt-4o-mini",

                messages: [
                    {
                        role: "system",
                        content:
                        "You are a medical report assistant. Explain reports in simple language. Give disclaimer that this is not a diagnosis."
                    },
                    {
                        role: "user",
                        content:
                        `Explain this medical report:\n${extractedText}`
                    }
                ]
            },
            {
                headers: {
                    Authorization:
                    `Bearer ${process.env.OPENROUTER_API_KEY}`,

                    "Content-Type":
                    "application/json"
                }
            }
        );


        const explanation =
        aiResponse.data.choices[0].message.content;

await Report.create({
    fileName: req.file.originalname,
    extractedText: extractedText,
    explanation: explanation
});
        fs.unlinkSync(filePath);


        res.json({
            success:true,
            extractedText,
            explanation
        });


    } catch(error){

        console.log(error.message);

        res.status(500).json({
            success:false,
            message:error.message
        });

    }

});

// ===============================
// GET ALL REPORTS
// ===============================

app.get("/reports", async (req, res) => {

    try {

        const reports = await Report.find();

        res.json({
            success: true,
            data: reports
        });

    } catch (error) {

        res.status(500).json({
            success: false,
            message: error.message
        });

    }

});

// ===============================
// GET SINGLE REPORT
// ===============================

app.get("/reports/:id", async (req, res) => {

    try {

        const report = await Report.findById(req.params.id);

        if (!report) {

            return res.status(404).json({
                success: false,
                message: "Report not found"
            });

        }

        res.json({
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

// ===============================
// DELETE REPORT
// ===============================

app.delete("/reports/:id", async (req, res) => {

    try {

        const report = await Report.findByIdAndDelete(req.params.id);

        if (!report) {
            return res.status(404).json({
                success: false,
                message: "Report not found"
            });
        }

        res.json({
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
const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
