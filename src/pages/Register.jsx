import "../styles/login.css";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FaEye, FaEyeSlash } from "react-icons/fa";

function Register() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const handleRegister = () => {
    if (name === "" || email === "" || password === "") {
      alert("Please fill all fields");
      return;
    }

    alert("Registration Successful!");
    navigate("/");
  };

  return (
    <div className="login-page">

      <div className="left-side">

        <div className="brand-logo">
          🩺 MediLens
        </div>

        <h1>Create Your Account</h1>

        <p>
          Join MediLens and securely manage, upload,
          and analyze your medical reports using AI.
        </p>

        <img
          src="https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=900"
          alt="Medical"
        />

      </div>

      <div className="right-side">

        <div className="login-card">

          <h2>Create Account 🚀</h2>

          <p>Register to start using MediLens.</p>

          <input
            type="text"
            placeholder="Full Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />

          <input
            type="email"
            placeholder="Email Address"
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
              placeholder="Create Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                paddingRight: "50px",
                marginBottom: "0",
              }}
            />

            <span
              onClick={() => setShowPassword(!showPassword)}
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
              {showPassword ? <FaEyeSlash /> : <FaEye />}
            </span>

          </div>

          <button onClick={handleRegister}>
            Create Account
          </button>

          <p className="register-text">
            Already have an account?{" "}
            <Link to="/">Login</Link>
          </p>

        </div>

      </div>

    </div>
  );
}

export default Register;