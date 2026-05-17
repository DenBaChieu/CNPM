import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import "../index.css";

const backendURL = import.meta.env.VITE_BACKEND_URL;

type Ticket = {
    ticketId: string;
    licensePlate: string;
    zoneId: string;
    amount: number;
    status: string;
    issuedTime: string;
    expirationTime: string;
};

export default function TicketPaymentPage() {
    const [ticket, setTicket] = useState<Ticket | null>(null);
    const [loading, setLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");

    // Load ticket from localStorage
    useEffect(() => {
        const stored = localStorage.getItem("ticket");

        if (stored) {
            setTicket(JSON.parse(stored));
        }
    }, []);

    const handleFakePay = async () => {
        if (!ticket) return;

        setLoading(true);
        setErrorMessage("");

        try {
            const token = localStorage.getItem("token");

            const response = await fetch(
                backendURL + "/ticket/pay",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`,
                    },
                    body: JSON.stringify({
                        paymentId: ticket.ticketId,
                    }),
                }
            );

            const data = await response.json();

            if (response.ok) {
                console.log("Payment success:", data);

                // Update UI instantly
                setTicket({
                    ...ticket,
                    status: "Paid",
                });

                // Clear localStorage (optional but recommended)
                localStorage.removeItem("ticket");
            } else {
                console.log("Payment failed:", data);
                setErrorMessage(data.detail || "Payment failed");
            }
        } catch (error) {
            console.error("Error:", error);
            setErrorMessage("Unable to connect to server");
        } finally {
            setLoading(false);
        }
    };

    if (!ticket) {
        return (
            <div className="p-4 text-center text-white">
                Không tìm thấy vé
            </div>
        );
    }

    return (
        <div className="flex flex-col gap-4 max-w-sm mx-auto min-h-screen justify-center">

            <h1 className="text-3xl font-bold text-center mb-4 text-white">
                Thanh toán vé xe
            </h1>

            {/* Error */}
            {errorMessage && (
                <p className="text-red-500 text-center text-sm">
                    {errorMessage}
                </p>
            )}

            {/* Ticket info */}
            <div className="bg-white p-4 rounded-lg space-y-2">
                <p><b>Mã vé:</b> {ticket.ticketId}</p>
                <p><b>Biển số:</b> {ticket.licensePlate}</p>
                <p><b>Khu vực:</b> {ticket.zoneId}</p>
                <p><b>Số tiền:</b> {ticket.amount} VNĐ</p>
                <p><b>Trạng thái:</b> {ticket.status}</p>
            </div>

            {/* Pay button */}
            {ticket.status !== "Paid" && (
                <button
                    onClick={handleFakePay}
                    disabled={loading}
                    className="bg-green-500 hover:bg-green-600 text-white font-semibold py-2 rounded-lg"
                >
                    {loading ? "Đang xử lý..." : "Thanh toán (demo)"}
                </button>
            )}

            {/* Success message */}
            {ticket.status === "Paid" && (
                <div className="bg-white p-3 rounded-lg text-green-600 text-center font-semibold">
                    ✔ Thanh toán thành công (demo)
                </div>
            )}

            {/* Back */}
            <Link to="/entrance">
                <button className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 rounded-lg w-full">
                    Quay lại
                </button>
            </Link>
        </div>
    );
}