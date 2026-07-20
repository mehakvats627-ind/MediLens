import "../styles/login.css";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FaEye, FaEyeSlash } from "react-icons/fa";

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = () => {
    if (email === "" || password === "") {
      alert("Please fill all fields");
      return;
    }

    navigate("/dashboard");
  };

  return (
    <div className="login-page">

      {/* Left Side */}

      <div className="left-side">

        <div className="brand-logo">
          🩺 MediLens
        </div>

        <h1>AI Medical Report Analyzer</h1>

        <p>
          Securely upload your medical reports and receive
          AI-powered analysis in seconds.
        </p>

        <img
          src="https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=900"
          alt="Medical"
        />

      </div>

      {/* Right Side */}

      <div className="right-side">

        <div className="login-card">

          <h2>Welcome Back 👋</h2>

          <p>Sign in to continue using MediLens.</p>

          <input
            type="email"
            placeholder="Enter your Email Address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <div
            style={{
              position: "relative",
              marginBottom: "18px",
            }}
          >

            <input
              type={showPassword ? "text" : "password"}
              placeholder="Enter your Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                paddingRight: "50px",
                marginBottom: "0",
              }}
            />

            <span
              onClick={() =>
                setShowPassword(!showPassword)
              }
              style={{
                position: "absolute",
                right: "18px",
                top: "50%",
                transform: "translateY(-50%)",
                cursor: "pointer",
                color: "#94a3b8",
                fontSize: "18px",
              }}
            >
              {showPassword ? (
                <FaEyeSlash />
              ) : (
                <FaEye />
              )}
            </span>

          </div>

          <button onClick={handleLogin}>
            Login
          </button>

          <p className="register-text">
            Don't have an account?{" "}
            <Link to="/register">
              Create Account
            </Link>
          </p>

        </div>

      </div>

    </div>
  );
}

export default Login;