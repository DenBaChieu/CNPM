import { Routes, Route } from "react-router-dom"

import Login from "./pages/login"
import Test from "./pages/test"
import CreateAccount from "./pages/createAccount"
import RegisterVehicle from "./pages/registerVehicle"
import Admin from "./pages/admin"
import Home from "./pages/home"
import Payment from "./pages/payment"
import Ticket from "./pages/ticket"
import Staff from "./pages/staff"
import Entrance from "./pages/entrance"
import Dashboard from "./pages/dashboard"
import Exit from "./pages/exit"
import Sensor from "./pages/sensor"
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
        <Route path="/entrance" element={<Entrance />} />
        <Route path="/sensor" element={<Sensor />} />
        <Route path="/exit" element={<Exit />} />
        <Route path="/ticket" element={<Ticket />} />
        <Route path="/createaccount" element={
            <ProtectedRoute>
              <CreateAccount />
            </ProtectedRoute>
        } />
        <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
        } />
        <Route path="/registervehicle" element={
            <ProtectedRoute>
              <RegisterVehicle />
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
        <Route path="/guidance" element={<Guidance />} />
    </Routes>
  )
}