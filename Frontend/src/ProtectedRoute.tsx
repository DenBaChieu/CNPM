import { Navigate } from "react-router-dom";
import type { ReactNode } from "react";
import { useEffect, useState } from "react";

const backendURL = import.meta.env.VITE_BACKEND_URL;

type ProtectedRouteProps = {
  children: ReactNode;
};

function ProtectedRoute({ children }: ProtectedRouteProps) {
  const token = localStorage.getItem("token");

  const [isValid, setIsValid] = useState<boolean | null>(null);

  useEffect(() => {
    const checkSessionValidity = async () => {
      if (!token) {
        setIsValid(false);
        return;
      }

      try {
        const response = await fetch(
          `${backendURL}/validateSession`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          localStorage.removeItem("token");
          setIsValid(false);
          return;
        }

        setIsValid(true);
      } catch (error) {
        console.error("Error:", error);
        setIsValid(false);
      }
    };

    checkSessionValidity();
  }, [token]);

  if (isValid === null) {
    return <div>Loading...</div>;
  }

  if (!isValid) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

export default ProtectedRoute;