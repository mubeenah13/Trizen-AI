import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Camera, LogOut, ShieldCheck, UserCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Navbar: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="sticky top-0 z-40 glass-nav px-6 py-4 flex items-center justify-between">
      <Link to={user?.role === 'ADMIN' ? '/admin' : '/team'} className="flex items-center gap-3 group">
        <div className="p-2 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 shadow-lg shadow-sky-500/20 group-hover:scale-105 transition-transform">
          <Camera className="w-6 h-6 text-white" />
        </div>
        <div>
          <span className="text-xl font-bold tracking-tight gradient-text">TrizenAI</span>
          <span className="ml-2 text-xs text-slate-400 font-medium px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700">Studio</span>
        </div>
      </Link>

      {isAuthenticated && user && (
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60">
            {user.role === 'ADMIN' ? (
              <span className="flex items-center gap-1 text-xs font-semibold text-sky-400 bg-sky-950/60 px-2 py-0.5 rounded-md border border-sky-800/50">
                <ShieldCheck className="w-3.5 h-3.5" /> LEAD ADMIN
              </span>
            ) : (
              <span className="flex items-center gap-1 text-xs font-semibold text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded-md border border-emerald-800/50">
                <UserCheck className="w-3.5 h-3.5" /> TEAM MEMBER
              </span>
            )}
            <span className="text-sm font-medium text-slate-200">{user.name}</span>
          </div>

          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-slate-300 hover:text-red-400 bg-slate-800/50 hover:bg-red-950/40 border border-slate-700 hover:border-red-900/50 rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4" /> Logout
          </button>
        </div>
      )}
    </nav>
  );
};
