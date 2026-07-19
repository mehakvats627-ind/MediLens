require("dotenv").config();

const { GoogleGenAI } = require("@google/genai");

async function listModels() {
  const ai = new GoogleGenAI({
    apiKey: process.env.GEMINI_API_KEY,
  });

  try {
    const models = await ai.models.list();

    for await (const model of models) {
      console.log(model.name);
    }
  } catch (err) {
    console.log(err);
  }
}

listModels();
const bcrypt = require("bcrypt");

async function test() {
    const hash = await bcrypt.hash("123456", 10);
    console.log(hash);
}

test();