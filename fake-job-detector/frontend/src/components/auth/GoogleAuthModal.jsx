import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { X, ShieldCheck } from 'lucide-react';
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../hooks/useToast';

export const GoogleAuthModal = ({ isOpen, onClose, onSuccess }) => {
  const navigate = useNavigate();
  const { loginWithGoogle } = useAuth();
  const { success, error } = useToast();
  const [isLoading, setIsLoading] = useState(false);

  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID?.trim();
  const isRealGoogleConfigured = !!googleClientId && 
    googleClientId !== '1083472093847-demo.apps.googleusercontent.com' &&
    !googleClientId.includes('demo_placeholder');

  if (!isOpen) return null;

  const handleRealGoogleSuccess = async (credentialResponse) => {
    const idToken = credentialResponse?.credential;
    if (!idToken) {
      error('Google Sign-In was cancelled or failed to return token.');
      return;
    }

    setIsLoading(true);
    try {
      const loggedUser = await loginWithGoogle(idToken);
      success(`Welcome ${loggedUser?.full_name || 'User'}! Authenticated via Google.`);
      if (onSuccess) onSuccess();
      if (onClose) onClose();
      navigate('/dashboard');
    } catch (err) {
      error(err.message || 'Google authentication failed.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-md bg-[#0e1117] text-white border border-white/10 rounded-3xl shadow-2xl overflow-hidden font-sans p-6 sm:p-8 space-y-6">
        
        {/* Close button */}
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors p-1.5 rounded-full hover:bg-white/10 z-10"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        )}

        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 shadow-emerald-glow mb-1">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-semibold text-white tracking-tight">Sign in with Google</h2>
          <p className="text-xs text-gray-400">Choose your Google account to access SentinelJob AI</p>
        </div>

        {/* Real Official Google Sign-In Button */}
        <div className="flex flex-col items-center justify-center w-full py-3 space-y-4">
          {isRealGoogleConfigured ? (
            <div className="w-full flex justify-center">
              <GoogleLogin
                onSuccess={handleRealGoogleSuccess}
                onError={() => error('Google Sign-In popup was cancelled or failed.')}
                theme="filled_black"
                shape="pill"
                text="continue_with"
                size="large"
                width="320"
              />
            </div>
          ) : (
            <div className="p-4 rounded-xl bg-amber-950/40 border border-amber-500/30 text-amber-300 text-xs text-center">
              Google Client ID is missing. Please set VITE_GOOGLE_CLIENT_ID in your frontend .env file.
            </div>
          )}

          {isLoading && (
            <p className="text-xs text-emerald-400 animate-pulse font-mono">Authenticating with Google...</p>
          )}
        </div>

        {/* Terms disclaimer */}
        <p className="text-[11px] text-gray-500 text-center leading-relaxed font-light">
          By signing in, you agree to our Privacy Policy and Terms of Service.
        </p>

      </div>
    </div>
  );
};

export default GoogleAuthModal;