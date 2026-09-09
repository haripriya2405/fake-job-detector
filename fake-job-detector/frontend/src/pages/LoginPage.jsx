import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldCheck, ArrowLeft } from 'lucide-react';
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '../hooks/useAuth';
import { useToast } from '../hooks/useToast';
import { LanguageSelector } from '../components/navigation/LanguageSelector';
import { GoogleAuthModal } from '../components/auth/GoogleAuthModal';

export const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showGoogleModal, setShowGoogleModal] = useState(false);

  const { login, loginWithGoogle } = useAuth();
  const { success } = useToast();
  const navigate = useNavigate();

  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID?.trim() || '889410971849-mmih2g5pr197ogaols041j49mhem4da2.apps.googleusercontent.com';
  const isRealGoogleConfigured = !!googleClientId && 
    googleClientId !== '1083472093847-demo.apps.googleusercontent.com' &&
    !googleClientId.includes('demo_placeholder');

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
        
        {/* Brand Header matching Image 1 */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center gap-2 mb-1">
            <div className="w-8 h-8 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shadow-emerald-glow">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div className="text-left">
              <h1 className="text-sm font-semibold text-frost tracking-tight leading-none">
                SentinelJob AI
              </h1>
              <p className="text-[9px] font-mono font-medium uppercase tracking-wider text-fog">Scam Intelligence</p>
            </div>
          </div>
          
          <h2 className="text-2xl sm:text-3xl font-medium text-frost tracking-tight pt-1">Sign in</h2>
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

        {/* Glass Authentication Card matching Image 1 */}
        <div className="rounded-2xl border border-white/10 bg-[#07100c]/90 backdrop-blur-xl p-6 sm:p-7 shadow-2xl space-y-4">
          
          {error && (
            <div className="p-3 rounded-xl bg-red-950/40 border border-red-500/30 text-xs text-red-300">
              {error}
            </div>
          )}

          {/* Real Google OAuth Button or Interactive Google Gmail Modal */}
          <div className="flex flex-col items-center justify-center w-full py-1">
            {isRealGoogleConfigured ? (
              <div className="w-full flex flex-col items-center space-y-2">
                <div className="w-full flex justify-center">
                  <GoogleLogin
                    onSuccess={handleGoogleSuccess}
                    onError={() => setShowGoogleModal(true)}
                    theme="filled_black"
                    shape="pill"
                    text="continue_with"
                    width="340"
                  />
                </div>
                <button
                  type="button"
                  onClick={() => setShowGoogleModal(true)}
                  disabled={loading}
                  className="text-[11px] text-fog hover:text-emerald-400 underline transition-colors pt-1"
                >
                  Click here to select your Gmail account
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => setShowGoogleModal(true)}
                disabled={loading}
                className="w-full flex items-center justify-center gap-3 bg-white hover:bg-slate-100 text-slate-800 font-semibold py-2.5 px-4 rounded-full shadow-md transition-all text-xs sm:text-sm active:scale-[0.99] disabled:opacity-50"
              >
                <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
                </svg>
                <span>{loading ? 'Authenticating...' : 'Continue with Google'}</span>
              </button>
            )}
          </div>

          {/* Divider */}
          <div className="relative flex items-center justify-center py-1">
            <div className="border-t border-white/10 w-full" />
            <span className="bg-[#07100c] px-3 text-[10px] uppercase font-mono text-fog tracking-wider absolute">
              Or continue with email
            </span>
          </div>

          {/* Form matching Image 1 */}
          <form onSubmit={handleSubmit} className="space-y-3.5">
            <div className="space-y-1.5">
              <label className="block text-xs font-medium text-mist">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
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

      {/* Google OAuth Modal */}
      <GoogleAuthModal
        isOpen={showGoogleModal}
        defaultEmail={email}
        onClose={() => setShowGoogleModal(false)}
        onSuccess={() => navigate('/dashboard')}
      />
    </div>
  );
};


export default LoginPage;
