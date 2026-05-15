import { useState } from "react"
import '../index.css'
const backendURL = import.meta.env.VITE_BACKEND_URL;

export default function Login() {
  const [sensorId, setSensorId] = useState("");
  const [licensePlate, setLicensePlate] = useState("");
  const [zoneId, setZoneId] = useState("");

  const handleSensorDetect = async () => {
    try {
      fetch(backendURL + "/sensor/detect", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          "sensorId": sensorId,
          "licensePlate": licensePlate,
        }),
      });
    } catch (error) {
      console.error("Error:", error);
    }
  };

  const handleSlot = async () => {
    try {
      
      const response = await fetch(
        `${backendURL}/parking/getAvailableSlots?zoneId=${zoneId}`,
        {
          method: "GET",
        }
      );

      const data = await response.json();

      if (response.ok) {
        const permission = await Notification.requestPermission();

        if (permission === "granted") {
            new Notification("Available slots:", {
                body: data.availableSlots.length,
            });
        }
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

   return (
    <div className="flex flex-col gap-4 max-w-sm mx-auto min-h-screen justify-center">
      <input
        className="border rounded-lg px-4 py-2 bg-white"
        value={sensorId}
        onChange={(e) => setSensorId(e.target.value)}
      />

      <input
        className="border rounded-lg px-4 py-2 bg-white"
        value={licensePlate}
        onChange={(e) => setLicensePlate(e.target.value)}
      />

      <button
        onClick={handleSensorDetect}
        className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 rounded-lg"
      >
        Send Data
      </button>

      <input
        className="border rounded-lg px-4 py-2 bg-white"
        value={zoneId}
        onChange={(e) => setZoneId(e.target.value)}
      />
      <button
        onClick={handleSlot}
        className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 rounded-lg"
      >
        Get number of slots left
      </button>
    </div>
  );
}