import { useState } from "react";
import "../index.css";

const backendURL = import.meta.env.VITE_BACKEND_URL;

export default function Login() {
  const [zoneId, setZoneId] = useState("");
  const [licensePlate, setLicensePlate] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const handle = async () => {
    setErrorMessage("");

    try {
      const response = await fetch(backendURL + "/sensor/exit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          zoneId: zoneId,
          licensePlate: licensePlate
        }),
      });

      const data = await response.json();

      if (response.ok) {
        console.log("Success:", data);
        if (data.ticket) {
          localStorage.setItem("ticket", JSON.stringify(data.ticket));
          window.location.href = "/ticket"
        } else {
          window.location.href = "/entrance"
        }
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
        Cổng ra
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
        placeholder="Biển số xe (IoT tự quét)"
        className="border rounded-lg px-4 py-2 bg-white"
        value={licensePlate}
        onChange={(e) => setLicensePlate(e.target.value)}
      />

      <button
        onClick={handle}
        className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 rounded-lg"
      >
        Ra cổng
      </button>
    </div>
  );
}