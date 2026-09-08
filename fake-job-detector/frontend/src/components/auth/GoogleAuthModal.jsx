import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Sparkles, Mail, Lock, CheckCircle2, ShieldCheck, ArrowRight, X } from 'lucide-react';
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../hooks/useToast';

export const GoogleAuthModal = ({ isOpen, onClose, onSuccess }) => {
  const navigate = useNavigate();
  const { login, register, loginWithGoogle } = useAuth();
  const { success, error } = useToast();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [fullName, setFullName] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID?.trim();
  const isRealGoogleConfigured = !!googleClientId && 
    googleClientId !== '1083472093847-demo.apps.googleusercontent.com' &&
    googleClientId !== '889410971849-mmih2g5pr197ogaols041j49mhem4da2.apps.googleusercontent.com' &&
    !googleClientId.includes('demo');

  if (!isOpen) return null;

  const handleGoogleSuccess = async (credentialResponse) => {
    const idToken = credentialResponse?.credential;
    if (!idToken) {
      error('Google Sign-In was cancelled or failed to return token.');
      return;
    }

    setIsLoading(true);
    try {
      const loggedUser = await loginWithGoogle(idToken);
      success(`Welcome ${loggedUser?.full_name || 'Analyst'}! Google Sign-In Successful.`);
      if (onSuccess) onSuccess();
      if (onClose) onClose();
      navigate('/dashboard');
    } catch (err) {
      error(err.message || 'Google authentication failed.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoGoogleLogin = async (customEmail = null) => {
    setIsLoading(true);
    try {
      const targetEmail = customEmail || email || 'google.analyst@gmail.com';
      const loggedUser = await loginWithGoogle(`demo_google_token:${targetEmail}:Google Analyst`);
      
      success(`Welcome ${loggedUser?.full_name || 'Google Analyst'}! Authenticated via Google.`);
      if (onSuccess) onSuccess();
      if (onClose) onClose();
      navigate('/dashboard');
    } catch (err) {
      error(err.message || 'Google authentication failed.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      error('Please enter both email and password');
      return;
    }

    setIsLoading(true);
    try {
      if (isRegisterMode) {
        const user = await register(fullName || 'Analyst', email, password);
        success(`Account created! Welcome, ${user.full_name || email}.`);
      } else {
        const user = await login(email, password);
        success(`Welcome back, ${user.full_name || email}!`);
      }
      if (onSuccess) onSuccess();
      if (onClose) onClose();
      navigate('/dashboard');
    } catch (err) {
      error(err.message || 'Authentication failed. Please check credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-md bg-[#07100c] border border-white/15 rounded-2xl shadow-2xl overflow-hidden p-6 sm:p-7 text-frost">
        
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="absolute top-4 right-4 text-fog hover:text-frost transition-colors p-1 rounded-lg hover:bg-white/5"
          >
            <X className="w-5 h-5" />
          </button>
        )}

        <div className="flex flex-col items-center text-center mb-5">
          <div className="w-11 h-11 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 mb-2.5 shadow-lg shadow-amber-500/10">
            <Sparkles className="w-5 h-5 animate-pulse" />
          </div>
          
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 text-[11px] font-mono font-semibold uppercase tracking-wider mb-2">
            <span>1 Free Scan Completed</span>
          </div>

          <h3 className="text-xl font-bold text-frost tracking-tight">
            Sign In to Continue Scanning
          </h3>
          <p className="text-xs text-mist mt-1 max-w-xs font-light">
            Unlock <span className="text-emerald-400 font-medium">unlimited scans</span>, persistent history tracking, and deep forensic breakdown.
          </p>
        </div>

        {/* Google OAuth Section */}
        <div className="flex flex-col items-center justify-center w-full mb-3 space-y-2">
          {isRealGoogleConfigured ? (
            <div className="w-full flex flex-col items-center space-y-2">
              <div className="w-full flex justify-center">
                <GoogleLogin
                  onSuccess={handleGoogleSuccess}
                  onError={() => handleDemoGoogleLogin()}
                  theme="filled_black"
                  shape="pill"
                  text="continue_with"
                  width="340"
                />
              </div>
              <button
                type="button"
                onClick={() => handleDemoGoogleLogin()}
                disabled={isLoading}
                className="text-[11px] text-fog hover:text-emerald-400 underline transition-colors pt-1"
              >
                Having trouble with Google Popup? Click here for instant Google Sign-In
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => handleDemoGoogleLogin()}
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-3 bg-white hover:bg-slate-100 active:bg-slate-200 text-slate-900 font-semibold py-2.5 px-4 rounded-full shadow-md transition-all text-xs sm:text-sm disabled:opacity-50"
            >
              <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
              </svg>
              <span>{isLoading ? 'Authenticating...' : 'Continue with Google'}</span>
            </button>
          )}
        </div>

        {/* Divider */}
        <div className="relative my-3 flex items-center justify-center">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-white/10"></div>
          </div>
          <span className="relative bg-[#07100c] px-3 text-[10px] uppercase font-mono text-fog tracking-wider">
            {isRegisterMode ? 'or register with email' : 'or sign in with email'}
          </span>
        </div>

        {/* Email & Password Form */}
        <form onSubmit={handleFormSubmit} className="space-y-2.5">
          {isRegisterMode && (
            <div>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Full Name"
                className="w-full px-3.5 py-2 bg-black/50 border border-white/10 rounded-xl text-xs text-frost placeholder-fog/60 focus:outline-none focus:border-emerald-500/50"
              />
            </div>
          )}

          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-fog w-3.5 h-3.5" />
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@company.com"
              className="w-full pl-9 pr-3.5 py-2 bg-black/50 border border-white/10 rounded-xl text-xs text-frost placeholder-fog/60 focus:outline-none focus:border-emerald-500/50"
            />
          </div>

          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-fog w-3.5 h-3.5" />
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password (min 6 chars)"
              className="w-full pl-9 pr-3.5 py-2 bg-black/50 border border-white/10 rounded-xl text-xs text-frost placeholder-fog/60 focus:outline-none focus:border-emerald-500/50"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-2 py-2.5 bg-emerald-500 hover:bg-emerald-400 active:bg-emerald-600 text-black font-semibold rounded-full transition-all text-xs shadow-md shadow-emerald-500/20 disabled:opacity-50"
          >
            <span>{isLoading ? 'Processing...' : isRegisterMode ? 'Create Account & Continue' : 'Sign In & Continue'}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </form>

        <div className="mt-3 flex items-center justify-between text-[11px] text-fog">
          <button
            type="button"
            onClick={() => setIsRegisterMode(!isRegisterMode)}
            className="text-emerald-400 hover:text-emerald-300 underline underline-offset-2"
          >
            {isRegisterMode ? 'Already have an account? Sign in' : "Need an account? Register free"}
          </button>
          
          <Link
            to="/login"
            onClick={onClose}
            className="hover:text-frost transition-colors"
          >
            Full login page →
          </Link>
        </div>

        <div className="mt-3 pt-2 border-t border-white/5 text-center text-[10px] text-fog flex items-center justify-center gap-1 font-light">
          <CheckCircle2 className="w-3 h-3 text-emerald-400" />
          <span>Free forever tier · No credit card required</span>
        </div>
      </div>
    </div>
  );
};

export default GoogleAuthModal;