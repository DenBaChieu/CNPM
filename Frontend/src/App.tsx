import { Routes, Route } from "react-router-dom"

import Login from "./pages/login"
import Test from "./pages/test"
import CreateAccount from "./pages/createAccount"
import RegisterVehicle from "./pages/registerVehicle"
import Admin from "./pages/admin"
import Home from "./pages/home"
import Payment from "./pages/payment"
import Staff from "./pages/staff"
import Entrance from "./pages/entrance"
import Exit from "./pages/exit"
import Sensor from "./pages/sensor"
import ProtectedRoute from "./ProtectedRoute"

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
        <Route path="/createaccount" element={
            <ProtectedRoute>
              <CreateAccount />
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
    </Routes>
  )
}