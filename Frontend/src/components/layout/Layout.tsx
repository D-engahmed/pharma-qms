import React from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export const Layout: React.FC = () => {
    const { user, logout, hasPermission } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        await logout();
        navigate('/login');
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <nav className="bg-slate-900 text-white px-6 py-3 flex items-center justify-between">
                <div className="font-bold text-lg">Pharma QMS</div>
                <div className="flex gap-4 text-sm">
                    <Link to="/dashboard" className="hover:text-blue-300">Dashboard</Link>
                    {hasPermission('receiving.view') && <Link to="/receiving" className="hover:text-blue-300">Receiving</Link>}
                    {hasPermission('sampling.view') && <Link to="/sampling" className="hover:text-blue-300">Sampling</Link>}
                    {hasPermission('analysis.view') && <Link to="/analysis" className="hover:text-blue-300">Analysis</Link>}
                    {hasPermission('certificate.view') && <Link to="/certificates" className="hover:text-blue-300">Certificates</Link>}
                    {hasPermission('audit.view') && <Link to="/audit" className="hover:text-blue-300">Audit</Link>}
                </div>
                <div className="flex items-center gap-3 text-sm">
                    <span className="text-gray-300">{user?.full_name}</span>
                    <button onClick={handleLogout} className="bg-red-600 px-3 py-1 rounded hover:bg-red-700">Logout</button>
                </div>
            </nav>
            <main className="p-6 max-w-7xl mx-auto">
                <Outlet />
            </main>
        </div>
    );
};