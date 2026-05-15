import { useState } from "react"
import '../index.css'
const backendURL = import.meta.env.VITE_BACKEND_URL;

export default function Login() {
  const [id, setId] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async () => {
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
        window.location.href = "/";
      } else {
        console.log("Login failed:", data);
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

   return (
    <div className="flex flex-col gap-4 max-w-sm mx-auto min-h-screen justify-center">
      <input
        type="email"
        placeholder="Email"
        className="border rounded-lg px-4 py-2 bg-white"
        value={id}
        onChange={(e) => setId(e.target.value)}
      />

      <input
        type="password"
        placeholder="Password"
        className="border rounded-lg px-4 py-2 bg-white"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <button
        onClick={handleLogin}
        className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 rounded-lg"
      >
        Login
      </button>
    </div>
  );
}