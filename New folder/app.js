const express = require("express");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
const connectMongoDB = require("./db");
require("dotenv").config();

connectMongoDB();

console.log("API Key exists:", !!process.env.OPENROUTER_API_KEY);

const User = require("./models/users");
const Report = require("./models/report");
console.log(Report.schema.obj);

const auth = require("./middleware/auth");

const extractText = require("./services/ocrservice");
const cors = require("cors");
const app = express();

app.use(cors());
app.use(express.json());

app.use(express.json());

app.get("/", (req, res) => {
  res.send("MediLens Backend is Running ✅");
});


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

c