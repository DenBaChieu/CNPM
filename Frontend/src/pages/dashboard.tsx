import { useState } from "react";
import { Link } from "react-router-dom";
import "../index.css";

const backendURL = import.meta.env.VITE_BACKEND_URL;

type Log = {
    id: number;
    event: string;
    timestamp: string;
};

export default function LogPage() {
    const [keyword, setKeyword] = useState("");
    const [logs, setLogs] = useState<Log[]>([]);
    const [loading, setLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");

    const searchLogs = async () => {
        setLoading(true);
        setErrorMessage("");

        try {
            const token = localStorage.getItem("token");

            const response = await fetch(
                `${backendURL}/logs/search?keyword=${keyword}`,
                {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`,
                    },
                }
            );

            const data = await response.json();

            if (response.ok) {
                setLogs(data);
            } else {
                setErrorMessage(data.detail || "Tìm kiếm thất bại");
            }
        } catch (err) {
            console.error(err);
            setErrorMessage("Không kết nối được tới máy chủ");
        } finally {
            setLoading(false);
        }
    };

    const exportLogs = async (format: "json" | "csv") => {
        try {
            const token = localStorage.getItem("token");

            const response = await fetch(
                `${backendURL}/logs/export`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token}`,
                    },
                    body: JSON.stringify({ format }),
                }
            );

            const data = await response.json();

            if (response.ok) {
                alert(`Exported: ${data.message}`);
            } else {
                setErrorMessage(data.detail || "Xuất bị lỗi");
            }
        } catch (err) {
            console.error(err);
            setErrorMessage("Không kết nối được tới máy chủ");
        }
    };

    return (
        <div className="min-h-screen px-4 py-10 bg-slate-950">
            <Link to="/admin">
                <button
                    className="absolute top-4 left-4 bg-blue-500 hover:bg-blue-600 text-white font-semibold p-2 rounded-lg"
                >
                    Back
                </button>
            </Link>

            <div className="mx-auto max-w-6xl rounded-4xl border border-white/10 bg-slate-900/95 p-6 shadow-2xl shadow-slate-950/40 backdrop-blur-xl">
                <header className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
                    <div>
                        <p className="text-sm uppercase tracking-[0.24em] text-sky-300/80">Dashboard</p>
                        <h1 className="mt-2 text-3xl font-semibold text-white">Quản lý nhật ký</h1>
                    </div>
                    <div className="flex flex-col gap-3 sm:flex-row">
                        <button
                            onClick={() => searchLogs()}
                            className="inline-flex items-center justify-center rounded-2xl bg-sky-500 px-4 py-3 text-sm font-semibold text-white transition hover:bg-sky-400"
                        >
                            Tìm kiếm nhật ký
                        </button>
                        <div className="inline-flex gap-2">
                            <button
                                onClick={() => exportLogs("json")}
                                className="rounded-2xl bg-emerald-500 px-4 py-3 text-sm font-semibold text-white transition hover:bg-emerald-400"
                            >
                                Xuất JSON
                            </button>
                            <button
                                onClick={() => exportLogs("csv")}
                                className="rounded-2xl bg-amber-500 px-4 py-3 text-sm font-semibold text-white transition hover:bg-amber-400"
                            >
                                Xuất CSV
                            </button>
                        </div>
                    </div>
                </header>

                <div className="mb-6 grid gap-4 sm:grid-cols-[1fr_260px]">
                    <input
                        className="w-full rounded-3xl border border-slate-700 bg-slate-800 px-4 py-3 text-slate-100 shadow-inner focus:border-sky-500"
                        placeholder="Tìm kiếm bằng từ khóa..."
                        value={keyword}
                        onChange={(e) => setKeyword(e.target.value)}
                    />
                    <div className="rounded-3xl border border-slate-700 bg-slate-800 p-4 text-sm text-slate-300">
                        Nhập một từ khóa để lọc nhật ký. Sau đó nhấn nút tìm kiếm.
                    </div>
                </div>

                {errorMessage && (
                    <div className="mb-4 rounded-3xl bg-red-500/10 px-4 py-3 text-sm text-red-200">
                        {errorMessage}
                    </div>
                )}

                {loading && (
                    <div className="mb-4 rounded-3xl bg-slate-800 px-4 py-3 text-sm text-slate-200">
                        Đang tải nhật ký...
                    </div>
                )}

                <div className="overflow-hidden rounded-[28px] border border-slate-700 bg-slate-950">
                    <table className="w-full border-collapse text-left text-sm">
                        <thead className="bg-slate-900 text-slate-300">
                            <tr>
                                <th className="p-4">ID</th>
                                <th className="p-4">Sự kiện</th>
                                <th className="p-4">Thời gian</th>
                            </tr>
                        </thead>
                        <tbody>
                            {logs.map((log) => (
                                <tr key={log.id} className="border-t border-slate-800 hover:bg-slate-900/80">
                                    <td className="p-4 text-slate-100">{log.id}</td>
                                    <td className="p-4 text-slate-200">{log.event}</td>
                                    <td className="p-4 text-slate-400">{new Date(log.timestamp).toLocaleString()}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}