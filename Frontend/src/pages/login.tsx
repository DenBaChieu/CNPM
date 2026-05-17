import { useState } from "react";
import "../index.css";

const backendURL = import.meta.env.VITE_BACKEND_URL;

export default function Login() {
  const [id, setId] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const handleLogin = async () => {
    setErrorMessage("");

    try {
      const response = await fetch(backendURL + "/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          id,
          password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        console.log("Login success:", data);
        localStorage.setItem("token", data.token);
        if (data.role == "Admin") {
          window.location.href = "/admin";
        } else if (data.role == "Staff") {
          window.location.href = "/staff";
        } else {
          window.location.href = "/";
        }
      } else {
        console.log("Login failed:", data);
        setErrorMessage(data.detail || "Login failed");
      }
    } catch (error) {
      console.error("Error:", error);
      setErrorMessage("Unable to connect to server");
    }
  };

  return (
    <div className="flex flex-col gap-4 max-w-sm mx-auto min-h-screen justify-center">
      <h1 className="text-3xl font-bold text-center mb-4 text-white">
        Đăng nhập
      </h1>

      {errorMessage && (
        <p className="text-red-500 text-center text-sm">
          {errorMessage}
        </p>
      )}

      <input
        type="text"
        placeholder="MSSV"
        className="border rounded-lg px-4 py-2 bg-white"
        value={id}
        onChange={(e) => setId(e.target.value)}
      />

      <input
        type="password"
        placeholder="Mật khẩu"
        className="border rounded-lg px-4 py-2 bg-white"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <button
        onClick={handleLogin}
        className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 rounded-lg"
      >
        Đăng nhập
      </button>
    </div>
  );
}