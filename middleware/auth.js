const jwt = require("jsonwebtoken");

const auth = (req, res, next) => {
  try {
    // Get token from request header
    const authHeader = req.headers.authorization;

    if (!authHeader) {
      return res.status(401).json({
        success: false,
        message: "Token not found",
      });
    }
console.log(req.headers.authorization);
    // Remove "Bearer " from token
    const token = authHeader.split(" ")[1];

    console.log("Token:", token);
    console.log("Secret:", process.env.JWT_SECRET);

    // Verify token
    const decoded = jwt.verify(token, process.env.JWT_SECRET);

    // Save user information
    req.user = decoded;

    next();

  } catch (error) {
    console.log(error);

    return res.status(401).json({
      success: false,
      message: "Invalid Token",
      error: error.message,
    });
  }
};

module.exports = auth;