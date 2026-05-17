import { Routes, Route } from "react-router-dom"

import Login from "./pages/login"
import Test from "./pages/test"
import CreateAccount from "./pages/createAccount"
import Admin from "./pages/admin"
import Home from "./pages/home"
import Payment from "./pages/payment"
import Staff from "./pages/staff"
import ProtectedRoute from "./ProtectedRoute"
import Guidance from "./pages/guidance"

export default function App() {
  return (
    <Routes>
        <Route path="/" element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
        } />
        <Route path="/login" element={<Login />} />
        <Route path="/createaccount" element={
            <ProtectedRoute>
              <CreateAccount />
            </ProtectedRoute>
        } />
        <Route path="/admin" element={
            <ProtectedRoute>
              <Admin />
            </ProtectedRoute>
        } />
        <Route path="/payment" element={
            <ProtectedRoute>
                <Payment />
            </ProtectedRoute>
        } />
        <Route path="/staff" element={
            <ProtectedRoute>
                <Staff />
            </ProtectedRoute>
        } />
        <Route path="/test" element={<Test />} />
        <Route path="/guidance" element={
            <ProtectedRoute>
                <Guidance />
            </ProtectedRoute>
        } />
    </Routes>
  )
}