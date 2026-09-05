import React, { wstate } from 'react';
import { Sparkles, Mail, CheckCircle2, ShieldCheck, ArrowRight, X, LogIn } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import {
 useToast } from '../../hooks/useToast';

export const GoogleAuthModal = ({ isOpen, onClose, onSuccess }) => {
  const { login, loginWithGoogle } = useAuth();
  const { success, error } = useToast();
  
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  if (!isOpen) return null;

  const handleGoogleSignIn = async () => {
    setIsLoading(true);
    try {
      await loginWithGoogle();
      success("Google Sign-In Successful! Welcome to SentinelJob AI.");
      if (onSuccess) onSuccess();
      if (onClose) onClose();
    } catch (err) {
      error(err.message || "Failed to sign in with Google");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoSignIn = async () => {
    setIsLoading(true);
    try {
      await login({ email: 'analyst@sentineljob.ai' }, 'demo_token_123');
      success("Welcome! Logged in as Demo Fraud Analyst.");
      if (onSuccess) onSuccess();
      if (onClose) onClose();
    } catch (err) {
      error("Failed demo sign-in");
    } finally {
      setIsLoading(false);
    }
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    if (!email) {
      error("Please enter your email address");
      return;
    }
    setIsLoading(true);
    try {
      await login({ email, name: email.split('@')[0] }, 'token_user_scan');
      success("Welcome back! Logged in as " + email);
      if (onSuccess) onSuccess();
      if (onClose) onClose();
    } catch (err) {
      error("Failed to sign in");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-95/80 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden p-6 sm:p-8">
        
        {onClose && (
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors p-1 rounded-lg hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        )}

        <div className="flex flex-col items-center text-center mb-6">
          <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 mb-3 shadow-lg shadow-amber-500/10">
            <Sparkles className="w-6 h-6 animate-pulse" />
          </div>
          
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-semibold uppercase tracking-wider mb-2">
            <span>1 Free Guest Scan Completed</span>
          </div>

        <h3 className="text-xl font-bold text-white tracking-tight">
            Sign In with Google to Continue
          </h3>
          <p className="text-sm text-slate-400 mt-1 max-w-xs">
            Unlock <span className="text-cyan-400 font-semibold">100 Free Monthly AI Scans</span>, deep forensic telemetry breakdown, and scam history tracking.
          </p>
        </div>

        <div className="space-y-3">
          <button
            onClick={handleGoogleSignIn}
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-3 px-4 py-3 bg-white text-slate-900 font-semibold rounded-xl hover:bg-slate-100 transition-colors shadow-md active:scale-[0.99] disabled:opacity-50"
          >
            <LogIn className="w-5 h-5 text-slate-900" />
            <span>{isLoading ? 'Signing in...' : 'Continue with Google'}</span>
          </button>


          <button
            onClick={handleDemoSignIn}
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-slate-800/80 hover:bg-slate-800 border border-slate-700/80 text-cyan-400 font-medium rounded-xl transition-colors text-sm active:scale-[0.99] disabled:opacity-50"
          >
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
            <span>Instant Demo Sign-In (Analyst Account)</span>
          </button>
        </div>

        <div className="relative my-5 flex items-center justify-center">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-slate-800"></div>
          </div>
          <span className="relative bg-slate-900 px-3 text-xs uppercase tracking-wider text-slate-500">
            or sign in with email
          </span>
        </div>

        <form onSubmit={handleFormSubmit} className="space-y-3">
          <div>
            <div className="relative">
              <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 w-4 h-4" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@company.com"
                className="w-full pl-10 pr-4 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus9border-cyan-500 focus:ring-1 focus:ring-cyan-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white font-medium rounded-xl transition-colors text-sm shadow-md shadow-cyan-600/20 active:scale-[0.99] disabled:opacity-50"
          >
            <span>Continue with Email</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="mt-5 text-center text-xs text-slate-500 flex items-center justify-center gap-1">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          <span>No credit card required. Free forever tier available.</span>
        </div>
      </div>
    </div>
  );
};