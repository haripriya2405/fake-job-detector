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
      // If login fails because user doesn't exist, offer quick register or show error
      error(err.message || 'Authentication failed. Please check credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-md bg-[#07100c] border border-white/15 rounded-2xl shadow-2xl overflow-hidden p-6 sm:p-7">
        
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

        {/* Real Google OAuth Button */}
        <div className="flex flex-col items-center justify-center w-full mb-3">
          <div className="w-full flex justify-center">
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={() => error('Google Sign-In failed or was cancelled.')}
              theme="filled_black"
              shape="pill"
              text="continue_with"
              width="340"
            />
          </div>
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