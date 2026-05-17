import { useState } from "react"
import '../index.css'
const backendURL = import.meta.env.VITE_BACKEND_URL;

export default function Page() {
  const [sensorId, setSensorId] = useState("");
  const [licensePlate, setLicensePlate] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [message, setMessage] = useState("");

  const handleSensorDetect = async () => {
    setErrorMessage("")
    setMessage("")

    try {
      const response = await fetch(backendURL + "/sensor/detect", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          "sensorId": sensorId,
          "licensePlate": licensePlate,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        if (licensePlate == "") {
            window.location.href = "/exit";
        }
        setMessage("Success");
      } else {
        setErrorMessage(data.detail || "Failed");
      }
    } catch (error) {
      console.error("Error:", error);
      setErrorMessage("Unable to connect to server");
    }
  };

   return (
    <div className="flex flex-col gap-4 max-w-sm mx-auto min-h-screen justify-center">
        {errorMessage && (
            <p className="text-red-500 text-center text-sm">
                {errorMessage}
            </p>
        )}
        {message && (
            <p className="text-white text-center text-sm">
                {message}
            </p>
        )}
      <input
        type="text"
        placeholder="Sensor ID"
        className="border rounded-lg px-4 py-2 bg-white"
        value={sensorId}
        onChange={(e) => setSensorId(e.target.value)}
      />

      <input
        type="text"
        placeholder="License plate"
        className="border rounded-lg px-4 py-2 bg-white"
        value={licensePlate}
        onChange={(e) => setLicensePlate(e.target.value)}
      />

      <button
        onClick={handleSensorDetect}
        className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 rounded-lg"
      >
        Gửi dữ liệu
      </button>
    </div>
  );
}