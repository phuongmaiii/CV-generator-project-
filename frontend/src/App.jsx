import { useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { AuthProvider, AuthContext } from './context/AuthContext';
import Auth from './components/Auth';
import RoleSelect from './pages/RoleSelect';
import UploadCv from './pages/UploadCv';
import CandidateDashboard from './pages/CandidateDashboard';
import CandidateMatches from './pages/CandidateMatches';
import CandidateDetails from './pages/CandidateDetails';
import CreateJob from './pages/CreateJob';
import HRMatches from './pages/HRMatchesPage';
import HRDashboard from './pages/HRDashboard';

const PrivateRoute = ({ children, allowedRole }) => {
    const { user, loading } = useContext(AuthContext);
    if (loading) return <div>Đang tải...</div>;
    if (!user) return <Navigate to="/" />;
    
    if (allowedRole && user.role?.toLowerCase() !== allowedRole.toLowerCase()) {
        return <Navigate to="/" />;
    }
    return children;
};

function AppRoutes() {
    return (
        <Routes>
            <Route path="/" element={<Auth />} />
            <Route path="/role-select" element={<RoleSelect />} />
            
            <Route path="/candidate" element={<Navigate to="/candidate-dashboard" />} />
            <Route path="/hr" element={<Navigate to="/hr-dashboard" />} />
            
            <Route path="/hr-dashboard" element={
                <PrivateRoute allowedRole="hr">
                    <HRDashboard />
                </PrivateRoute>
            } />

            <Route path="/candidate-dashboard" element={
                <PrivateRoute allowedRole="candidate">
                    <CandidateDashboard />
                </PrivateRoute>
            } />

            <Route path="/upload-cv" element={
                <PrivateRoute allowedRole="candidate">
                    <UploadCv />
                </PrivateRoute>
            } />
            
            <Route path="/candidate/matches/:candidateId" element={
                <PrivateRoute allowedRole="candidate">
                    <CandidateMatches />
                </PrivateRoute>
            } />

            <Route path="/create-job" element={
                <PrivateRoute allowedRole="hr">
                    <CreateJob />
                </PrivateRoute>
            } />
            
            {/* Đã sửa lại cú pháp chuẩn tại đây */}
            <Route path="/hr-matches/:jobPostingId" element={
                <PrivateRoute allowedRole="hr">
                    <HRMatches />
                </PrivateRoute>
            } />
            
            <Route path="/candidate-details/:id" element={
                <PrivateRoute allowedRole="hr">
                    <CandidateDetails />
                </PrivateRoute>
            } />
        </Routes>
    );
}

export default function App() {
    return (
        <ConfigProvider
            theme={{
                token: {
                    colorPrimary: '#23433A',
                    colorLink: '#23433A',
                    colorLinkHover: '#2F6B4F',
                    fontFamily: "'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif",
                    borderRadius: 6,
                    colorBgLayout: '#F3F4EF',
                },
                components: {
                    Button: {
                        colorPrimary: '#23433A',
                        algorithm: true,
                    },
                    Tag: {
                        defaultBg: '#F3F4EF',
                    },
                },
            }}
        >
            <AuthProvider>
                <BrowserRouter>
                    <AppRoutes />
                </BrowserRouter>
            </AuthProvider>
        </ConfigProvider>
    );
}