import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Camera, Lock, Mail, ArrowRight, ShieldCheck, UserCheck } from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const res = await api.post('/auth/login', {
        email: email.trim().toLowerCase(),
        password,
      });

      login(res.data.access_token, res.data.user);
      if (res.data.user.role === 'ADMIN') {
        navigate('/admin');
      } else {
        navigate('/team');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid email or password.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = async (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setError(null);
    setIsLoading(true);
    try {
      const res = await api.post('/auth/login', { email: demoEmail, password: demoPass });
      login(res.data.access_token, res.data.user);
      if (res.data.user.role === 'ADMIN') {
        navigate('/admin');
      } else {
        navigate('/team');
      }
    } catch (err: any) {
      setError('Demo login failed. Make sure database is seeded.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-slate-950">
      <div className="w-full max-w-md glass-card rounded-2xl p-8 border border-slate-800 shadow-2xl">
        <div className="text-center mb-8">
          <div className="inline-flex p-3 rounded-2xl bg-gradient-to-tr from-sky-500 to-indigo-600 shadow-xl shadow-sky-500/20 mb-4">
            <Camera className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-slate-100">Welcome to TrizenAI</h2>
          <p className="text-sm text-slate-400 mt-1">Collaborative Event Photography Platform</p>
        </div>

        {error && (
          <div className="mb-6 p-3.5 rounded-xl bg-red-950/60 border border-red-800/80 text-red-300 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-1">Email Address</label>
            <div className="relative">
              <Mail className="w-5 h-5 text-slate-500 absolute left-3.5 top-3" />
              <input
                type="email"
                placeholder="admin@trizen.ai"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-11 pr-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500 text-sm"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-1">Password</label>
            <div className="relative">
              <Lock className="w-5 h-5 text-slate-500 absolute left-3.5 top-3" />
              <input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-11 pr-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500 text-sm"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white font-bold shadow-lg shadow-sky-500/25 flex items-center justify-center gap-2 transition-all text-sm disabled:opacity-50 mt-6"
          >
            {isLoading ? 'Signing in...' : 'Sign In'} <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Demo Fast Login Buttons */}
        <div className="mt-8 pt-6 border-t border-slate-800/80">
          <p className="text-xs font-semibold text-slate-400 text-center mb-3">Quick Demo Access</p>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => handleDemoLogin('admin@trizen.ai', 'Admin123!')}
              className="py-2 px-3 rounded-lg bg-sky-950/40 hover:bg-sky-950/80 border border-sky-800/50 text-sky-300 text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
            >
              <ShieldCheck className="w-3.5 h-3.5" /> Demo Admin
            </button>
            <button
              onClick={() => handleDemoLogin('team@trizen.ai', 'Team123!')}
              className="py-2 px-3 rounded-lg bg-emerald-950/40 hover:bg-emerald-950/80 border border-emerald-800/50 text-emerald-300 text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
            >
              <UserCheck className="w-3.5 h-3.5" /> Demo Team
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
