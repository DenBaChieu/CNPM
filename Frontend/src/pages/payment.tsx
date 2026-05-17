import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { QRCodeCanvas } from "qrcode.react";
import "../index.css";

const backendURL = import.meta.env.VITE_BACKEND_URL;

type Payment = {
    paymentId: number,
    userId: number,
    amount: number,
    paymentDate: string,
    dueDate: string,
    status: string,
    QRCode: string
};

function formatVNDate(iso: string) {
    if (!iso) return "Không có";

    const date = new Date(iso);

    return new Intl.DateTimeFormat("vi-VN", {
        dateStyle: "short",
        timeStyle: "short",
    }).format(date);
}

export default function Page() {
    const [payments, setPayment] = useState<Payment[]>([]);

    useEffect(() => {
        async function getPaymentInfo() {
            const token = localStorage.getItem("token");

            try {
                const response = await fetch(
                    backendURL + "/payment/getInfo",
                    {
                        method: "GET",
                        headers: {
                            "Content-Type": "application/json",
                            "Authorization": `Bearer ${token}`,
                        }
                    }
                );

                const data = await response.json();

                if (response.ok) {
                    setPayment(data);
                }
            } catch (error) {
                console.error("Error:", error);
            }
        }

        getPaymentInfo();
    }, []);

    async function handleFakePay(paymentId: number) {
        const token = localStorage.getItem("token");

        try {
            const res = await fetch(
                `${backendURL}/payment/pay`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`,
                    },
                    body: JSON.stringify({
                        "paymentId": paymentId,
                    }),
                }
            );

            if (res.ok) {
                setPayment((prev) =>
                    prev.map((p) =>
                        p.paymentId === paymentId
                            ? { ...p, status: "Paid", paymentDate: new Date().toISOString() }
                            : p
                    )
                );
            }
        } catch (err) {
            console.error("Payment error:", err);
        }
    }

    return (
        <div className="p-4 relative">

            <Link to="/">
                <button className="absolute top-4 right-4 bg-blue-500 hover:bg-blue-600 text-white font-semibold p-2 rounded-lg">
                    Quay lại
                </button>
            </Link>

            <h1 className="text-2xl font-bold mb-4">Danh sách thanh toán</h1>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {payments.map((payment) => (
                    <div
                        key={payment.paymentId}
                        className="border rounded-2xl shadow-md p-4 bg-white"
                    >
                        <div className="flex justify-between items-center mb-2">
                            <p className="text-sm">
                                <b>Mã:</b>{" "}
                                <span className="inline-block max-w-35 truncate align-bottom">
                                    {payment.paymentId}
                                </span>
                            </p>

                            <span
                                className={`text-xs px-2 py-1 rounded-full ${
                                    payment.status === "Paid"
                                        ? "bg-green-100 text-green-700"
                                        : "bg-yellow-100 text-yellow-700"
                                }`}
                            >
                                {payment.status === "Paid" ? "Đã thanh toán" : "Chưa thanh toán"}
                            </span>
                        </div>

                        <div className="text-sm space-y-1">
                            <p><b>Mã người dùng:</b> {payment.userId}</p>
                            <p><b>Số tiền:</b> {payment.amount} VNĐ</p>
                            <p><b>Hạn thanh toán:</b> {formatVNDate(payment.dueDate)}</p>
                            <p><b>Ngày thanh toán:</b> {formatVNDate(payment.paymentDate)}</p>
                        </div>

                        {payment.QRCode && (
                            <div className="mt-4 flex flex-col items-center">
                                <QRCodeCanvas value={payment.QRCode} size={120} />
                                <p className="text-xs text-gray-500 mt-2">
                                    Quét để thanh toán
                                </p>
                            </div>
                        )}

                        {payment.status !== "Paid" && (
                            <button
                                onClick={() => handleFakePay(payment.paymentId)}
                                className="mt-4 w-full bg-green-500 hover:bg-green-600 text-white py-2 rounded-lg"
                            >
                                Thanh toán (demo)
                            </button>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}