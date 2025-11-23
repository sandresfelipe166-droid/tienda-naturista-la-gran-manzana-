import { ErrorBoundary } from '@/components/ErrorBoundary'
import ForgotPasswordPage from '@/pages/ForgotPasswordPage'
import LoginPage from '@/pages/LoginPage'
import RegisterPage from '@/pages/RegisterPage'
import ResetPasswordPage from '@/pages/ResetPasswordPage'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import './App.css'

import { OnlineStatus } from '@/components/OnlineStatus'
function App() {
    return (
        <ErrorBoundary>
            <BrowserRouter>
                <OnlineStatus />
                <Routes>
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/register" element={<RegisterPage />} />
                    <Route path="/forgot-password" element={<ForgotPasswordPage />} />
                    <Route path="/reset-password" element={<ResetPasswordPage />} />
                    {/* Temporal: Forzar login en / y cualquier ruta */}
                    <Route path="/" element={<LoginPage />} />
                    <Route path="*" element={<LoginPage />} />
                </Routes>
            </BrowserRouter>
        </ErrorBoundary>
    )
}

export default App
