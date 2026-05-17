import { useState } from "react";
import { Link } from "react-router-dom";
import "../index.css";

const backendURL = import.meta.env.VITE_BACKEND_URL;

export default function Login() {
  const [id, setId] = useState("");
  const [zoneId, setZoneId] = useState("");
  const [licensePlate, setLicensePlate] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const handle = async () => {
    setErrorMessage("");

    try {
      const response = await fetch(backendURL + "/sensor/studentEnter", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          "id": id,
          "zoneId": zoneId,
          "licensePlate": licensePlate,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        console.log("Success:", data);
        window.location.href = "/sensor"
      } else {
        console.log("Failed:", data);
        setErrorMessage(data.detail || "Failed");
      }
    } catch (error) {
      console.error("Error:", error);
      setErrorMessage("Unable to connect to server");
    }
  };

  const handleTemporaryTicket = async () => {
    setErrorMessage("");

    try {
      const response = await fetch(backendURL + "/visitor/requestTempTicket", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          "zoneId": zoneId,
          "licensePlate": licensePlate,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        console.log("Success:", data);
        window.location.href = "/sensor"
      } else {
        console.log("Failed:", data);
        setErrorMessage(data.detail || "Failed");
      }
    } catch (error) {
      console.error("Error:", error);
      setErrorMessage("Unable to connect to server");
    }
  };

  return (
    <div className="flex flex-col gap-4 max-w-sm mx-auto min-h-screen justify-center">
      <h1 className="text-3xl font-bold text-center mb-4 text-white">
        Cổng vào
      </h1>

      {errorMessage && (
        <p className="text-red-500 text-center text-sm">
          {errorMessage}
        </p>
      )}

      <input
        type="text"
        placeholder="Cơ sở (CS1/CS2)"
        className="border rounded-lg px-4 py-2 bg-white"
        value={zoneId}
        onChange={(e) => setZoneId(e.target.value)}
      />

      <input
        type="text"
        placeholder="MSSV (IoT tự quét thẻ)"
        className="border rounded-lg px-4 py-2 bg-white"
        value={id}
        onChange={(e) => setId(e.target.value)}
      />

      <input
        type="text"
        placeholder="Biển số xe (IoT tự quét)"
        className="border rounded-lg px-4 py-2 bg-white"
        value={licensePlate}
        onChange={(e) => setLicensePlate(e.target.value)}
      />

      <button
        onClick={handle}
        className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 rounded-lg"
      >
        Vào cổng
      </button>

      <button
        onClick={handleTemporaryTicket}
        className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 rounded-lg"
      >
        Cấp vé tạm
      </button>

      <Link to="/login">
        <button
            className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 rounded-lg w-sm"
        >
            Đăng nhập
        </button>
      </Link>
    </div>
  );
}