import '../index.css'
import { Link } from "react-router-dom";

export default function Page() {
    return (
        <div className="flex flex-col gap-4 max-w-sm mx-auto min-h-screen justify-center">
            <Link to="/login">
                <button
                    className="absolute top-4 right-4 bg-blue-500 hover:bg-blue-600 text-white font-semibold p-2 rounded-lg"
                >
                    Back to login
                </button>
            </Link>

            <Link to="/payment">
                <button
                    className="bg-blue-500 hover:bg-blue-600 text-white font-semibold p-2 rounded-lg"
                >
                    Payments
                </button>
            </Link>
        </div>
    );
}