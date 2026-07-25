const mongoose = require("mongoose");
require("dotenv").config();


console.log(process.env.MONGODB_URI);
async function connectMongoDB() {
  try {
    await mongoose.connect(process.env.MONGODB_URI, )
    console.log("Connected to MongoDB");
  } catch (error) {
    console.log(error);
    process.exit(1);
  }
}
module.exports = connectMongoDB;