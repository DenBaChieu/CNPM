import '../index.css'
import { Link } from "react-router-dom";
const backendURL = import.meta.env.VITE_BACKEND_URL;

export default function Page() {
  const startBillingPeriod = async () => {
    const token = localStorage.getItem("token");
    try {
      fetch(backendURL + "/payment/startBillingPeriod", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        }
      });
    } catch (error) {
      console.error("Error:", error);
    }
  };

  const stopBillingPeriod = async () => {
    const token = localStorage.getItem("token");
    try {
      fetch(backendURL + "/payment/stopBillingPeriod", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        }
      });
    } catch (error) {
      console.error("Error:", error);
    }
  };

   return (
    <div className="flex flex-col gap-4 max-w-sm mx-auto min-h-screen justify-center">
        <Link to="/login">
            <button
                className="absolute top-4 right-4 bg-blue-500 hover:bg-blue-600 text-white font-semibold p-2 rounded-lg"
            >
                Back to login
            </button>
        </Link>
      <button
        onClick={startBillingPeriod}
        className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 rounded-lg"
      >
        Bắt đầu chu kỳ thanh toán
      </button>

      <button
        onClick={stopBillingPeriod}
        className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 rounded-lg"
      >
        Dừng chu kỳ thanh toán
      </button>

      <Link to="/createaccount">
        <button
            className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 rounded-lg w-sm"
        >
          Tạo tài khoản
        </button>
      </Link>
      <Link to="/registervehicle">
        <button
            className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 rounded-lg w-sm"
        >
          Đăng ký xe
        </button>
      </Link>
      <Link to="/dashboard">
        <button
            className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 rounded-lg w-sm"
        >
          Dashboard
        </button>
      </Link>
    </div>
  );
}