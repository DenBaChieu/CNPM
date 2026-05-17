import { useState } from "react";
import { Link } from "react-router-dom";
import "../index.css";

const backendURL = import.meta.env.VITE_BACKEND_URL;

export default function CreateAccount() {
  const [userId, setUserId] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState("");
  const [email, setEmail] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [password, setPassword] = useState("");

  const handleCreateAccount = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(backendURL + "/createaccount", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          userId,
          fullName,
          role,
          email,
          phoneNumber,
          password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        console.log("Create account success:", data);
        window.location.href = "/admin";
      } else {
        console.log("Create account failed:", data);
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <div className="flex flex-col gap-4 max-w-sm mx-auto min-h-screen justify-center">
      <h1 className="text-3xl font-bold text-center mb-4 text-white">
        Tạo tài khoản
      </h1>

      <Link to="/admin">
        <button
          className="absolute top-4 left-4 bg-blue-500 hover:bg-blue-600 text-white font-semibold p-2 rounded-lg"
        >
          Back
        </button>
      </Link>

      <input
        type="text"
        placeholder="MSSV"
        className="border rounded-lg px-4 py-2 bg-white"
        value={userId}
        onChange={(e) => setUserId(e.target.value)}
      />

      <input
        type="text"
        placeholder="Họ và tên"
        className="border rounded-lg px-4 py-2 bg-white"
        value={fullName}
        onChange={(e) => setFullName(e.target.value)}
      />

      <input
        type="text"
        placeholder="Vai trò"
        className="border rounded-lg px-4 py-2 bg-white"
        value={role}
        onChange={(e) => setRole(e.target.value)}
      />

      <input
        type="email"
        placeholder="Email"
        className="border rounded-lg px-4 py-2 bg-white"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />

      <input
        type="text"
        placeholder="Số điện thoại"
        className="border rounded-lg px-4 py-2 bg-white"
        value={phoneNumber}
        onChange={(e) => setPhoneNumber(e.target.value)}
      />

      <input
        type="text"
        placeholder="Mật khẩu"
        className="border rounded-lg px-4 py-2 bg-white"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <button
        onClick={handleCreateAccount}
        className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 rounded-lg"
      >
        Tạo
      </button>
    </div>
  );
}