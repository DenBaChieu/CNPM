import { useState } from "react";
import { Link } from "react-router-dom";
import "../index.css";

const backendURL = import.meta.env.VITE_BACKEND_URL;

export default function CreateAccount() {
  const [ownerId, setOwnerId] = useState("");
  const [vehicleType, setVehicleType] = useState("");
  const [licensePlate, setLicensePlate] = useState("");

  const handleCreateAccount = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(backendURL + "/registerVehicle", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          licensePlate: licensePlate,
          vehicleType: vehicleType,
          ownerId: ownerId,
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
        Tạo phương tiện
      </h1>

      <Link to="/admin">
        <button
          className="absolute top-4 left-4 bg-blue-500 hover:bg-blue-600 text-white font-semibold p-2 rounded-lg"
        >
          Quay lại
        </button>
      </Link>

      <input
        type="text"
        placeholder="Biển số xe"
        className="border rounded-lg px-4 py-2 bg-white"
        value={licensePlate}
        onChange={(e) => setLicensePlate(e.target.value)}
      />

      <input
        type="text"
        placeholder="Loại phương tiện"
        className="border rounded-lg px-4 py-2 bg-white"
        value={vehicleType}
        onChange={(e) => setVehicleType(e.target.value)}
      />

      <input
        type="text"
        placeholder="MSSV"
        className="border rounded-lg px-4 py-2 bg-white"
        value={ownerId}
        onChange={(e) => setOwnerId(e.target.value)}
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