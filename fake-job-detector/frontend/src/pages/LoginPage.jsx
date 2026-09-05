import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldCheck, ArrowLeft } from 'lucide-react';
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '../hooks/useAuth';
import { useToast } from '../hooks/useToast';
import { LanguageSelector } from '../components/navigation/LanguageSelector';

export const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { login, loginWithGoogle } = useAuth();
  const { success } = useToast();
  const navigate = useNavigate();

  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID?.trim();

  const handleGoogleSuccess = async (credentialResponse) => {
    const idToken = credentialResponse?.credential;
    if (!idToken) {
      setError('Google Sign-In was cancelled or failed to return token.');
      return;
    }

    try {
      setLoading(true);
      setError('');
      const loggedUser = await loginWithGoogle(idToken);
      success(`Welcome ${loggedUser?.full_name || 'back'}! Authenticated via Google.`);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Google authentication failed.');
    } finally {
      setLoading(false);
    }
  };


  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      success('Authenticated successfully. Welcome back.');
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Invalid email or password.');
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="min-h-screen bg-[#050a08] text-frost flex flex-col justify-between py-6 px-4 sm:px-6 relative selection:bg-emerald-500 selection:text-white">
      
      {/* Background blueprint and subtle spotlight */}
      <div className="pointer-events-none absolute inset-0" aria-hidden="true">
        <div className="absolute inset-0 bg-blueprint opacity-50" />
        <div className="absolute inset-0 bg-spotlight" />
      </div>

      {/* Top Bar with Language Selector on the top-right matching reference */}
      <div className="max-w-4xl w-full mx-auto flex justify-end relative z-10">
        <LanguageSelector />
      </div>

      {/* Center Main Card Container */}
      <div className="max-w-[400px] w-full mx-auto space-y-6 my-auto relative z-10">
        
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center w-11 h-11 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 shadow-emerald-glow mb-1">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-base font-semibold text-frost tracking-tight">
              SentinelJob AI
            </h1>
            <p className="text-[10px] font-mono font-medium uppercase tracking-[0.18em] text-fog">Job Scam Intelligence</p>
          </div>
          
          <h2 className="text-2xl sm:text-3xl font-medium text-frost tracking-tight pt-2">Sign in</h2>
          <p className="text-xs text-mist font-light">Welcome back to your account</p>

          <div className="pt-1">
            <Link
              to="/"
              className="inline-flex items-center gap-1.5 text-xs text-fog hover:text-frost bg-white/5 border border-white/10 rounded-full px-3.5 py-1.5 transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to landing page</span>
            </Link>
          </div>
        </div>

        {/* Glass Authentication Card */}
        <div className="rounded-2xl border border-white/10 bg-[#07100c]/90 backdrop-blur-xl p-6 sm:p-7 shadow-2xl space-y-4">
          
          {error && (
            <div className="p-3 rounded-xl bg-red-950/40 border border-red-500/30 text-xs text-red-300">
              {error}
            </div>
          )}

          {/* Real Google OAuth Button */}
          <div className="flex flex-col items-center justify-center w-full py-1">
            {googleClientId && (
              <GoogleLogin
                onSuccess={handleGoogleSuccess}
                onError={(err) => {
                  console.error('Google Sign-In Failed:', err);
                  setError('Google authentication failed. Please verify the origin in Google Cloud Console.');
                }}
                theme="filled_black"
                shape="pill"
                text="continue_with"
                width="340"
              />
            )}
          </div>




          {/* Divider */}
          <div className="relative flex items-center justify-center py-1">
            <div className="border-t border-white/10 w-full" />
            <span className="bg-[#07100c] px-3 text-[10px] uppercase font-mono text-fog tracking-wider absolute">
              Or continue with email
            </span>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-3.5">
            <div className="space-y-1.5">
              <label className="block text-xs font-medium text-mist">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                className="w-full px-4 py-2.5 rounded-xl bg-black/40 border border-white/10 text-frost placeholder-fog/60 text-xs sm:text-sm focus:outline-none focus:ring-1 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition-all font-sans"
              />
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-medium text-mist">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-4 py-2.5 rounded-xl bg-black/40 border border-white/10 text-frost placeholder-fog/60 text-xs sm:text-sm focus:outline-none focus:ring-1 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition-all font-sans"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full inline-flex items-center justify-center gap-2 rounded-full py-3 px-4 text-xs sm:text-sm font-semibold text-white bg-emerald-500 hover:bg-emerald-400 active:bg-emerald-600 shadow-emerald-button hover:shadow-emerald-glow transition-all duration-150 disabled:opacity-50"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          {/* Sign up link */}
          <div className="pt-2 text-center text-xs text-fog">
            Don't have an account?{' '}
            <Link to="/register" className="text-emerald-400 hover:text-emerald-300 font-semibold underline underline-offset-2">
              Sign up
            </Link>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="max-w-md w-full mx-auto text-center text-[10px] text-fog py-2 relative z-10 font-light">
        Protected by SentinelJob AI 8-Layer Signal Intelligence
      </div>
    </div>
  );
};


export default LoginPage;
