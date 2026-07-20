require("dotenv").config();

const { GoogleGenAI } = require("@google/genai");

const ai = new GoogleGenAI({
  apiKey: process.env.GEMINI_API_KEY,
});

async function test() {
  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.5-pro",
      contents: "Say Hello",
    });

    console.log(response.text);
  } catch (err) {
    console.error(err);
  }
}

test();