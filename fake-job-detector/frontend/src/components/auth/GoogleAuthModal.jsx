import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, X, ChevronDown, ShieldCheck } from 'lucide-react';
import { GoogleLogin, useGoogleLogin } from '@react-oauth/google';
import axios from 'axios';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../hooks/useToast';

export const GoogleAuthModal = ({ isOpen, onClose, onSuccess, defaultEmail = '' }) => {
  const navigate = useNavigate();
  const { loginWithGoogle } = useAuth();
  const { success, error } = useToast();

  const [step, setStep] = useState('choose_account');
  const [emailOrPhone, setEmailOrPhone] = useState(defaultEmail || '');
  const [isLoading, setIsLoading] = useState(false);

  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID?.trim();
  const isRealGoogleConfigured = !!googleClientId && 
    googleClientId !== '1083472093847-demo.apps.googleusercontent.com' &&
    !googleClientId.includes('demo_placeholder');

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

  const handlePopupGoogleLogin = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      setIsLoading(true);
      try {
        const userInfo = await axios.get('https://www.googleapis.com/oauth2/v3/userinfo', {
          headers: { Authorization: `Bearer ${tokenResponse.access_token}` },
        });
        const { email, name } = userInfo.data;
        const emailPrefix = email.split('@')[0].replace(/[._-]/g, ' ');
        const safeName = name || (emailPrefix.charAt(0).toUpperCase() + emailPrefix.slice(1));
        const loggedUser = await loginWithGoogle(`demo_google_token:${email}:${safeName}`);
        
        success(`Welcome ${loggedUser?.full_name || safeName}! Authenticated via Google.`);
        if (onSuccess) onSuccess();
        if (onClose) onClose();
        navigate('/dashboard');
      } catch (err) {
        error(err.message || 'Google authentication failed.');
      } finally {
        setIsLoading(false);
      }
    },
    onError: () => {
      error('Google popup Sign-In was cancelled or closed.');
    },
  });

  if (!isOpen) return null;

  const handleAccountSelect = async (accountEmail, accountName) => {
    setIsLoading(true);
    try {
      const emailPrefix = accountEmail.split('@')[0].replace(/[._-]/g, ' ');
      const safeName = accountName || (emailPrefix.charAt(0).toUpperCase() + emailPrefix.slice(1));
      
      const loggedUser = await loginWithGoogle(`demo_google_token:${accountEmail}:${safeName}`);
      
      success(`Welcome ${loggedUser?.full_name || safeName}! Authenticated via Google.`);
      if (onSuccess) onSuccess();
      if (onClose) onClose();
      navigate('/dashboard');
    } catch (err) {
      error(err.message || 'Google authentication failed.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNextSubmit = (e) => {
    e.preventDefault();
    if (!emailOrPhone.trim()) {
      error('Please enter an email or phone number.');
      return;
    }
    const safeEmail = emailOrPhone.includes('@') ? emailOrPhone.trim() : `${emailOrPhone.trim().toLowerCase()}@gmail.com`;
    handleAccountSelect(safeEmail);
  };

  const defaultAccounts = [
    { name: 'Haripriya2027 Csd', email: 'haripriyacsd@gmail.com', initial: 'H', bg: 'bg-[#d81b60]' },
    { name: 'Denver MH', email: 'denvermh64@gmail.com', initial: 'D', bg: 'bg-[#e65100]' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fadeIn">
      
      {step === 'choose_account' ? (
        <div className="relative w-full max-w-2xl bg-[#141414] border border-white/10 rounded-3xl shadow-2xl overflow-hidden text-white font-sans">
          
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

          {/* Top Bar: Google G + Sign in with Google */}
          <div className="flex items-center gap-2.5 px-8 pt-7 pb-4">
            <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
            </svg>
            <span className="text-sm font-medium text-gray-200">Sign in with Google</span>
          </div>

          {/* Grid Layout */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6 px-8 pb-8 pt-2">
            
            {/* Left Column */}
            <div className="md:col-span-5 space-y-2 pt-2">
              <h2 className="text-3xl sm:text-4xl font-normal tracking-tight text-white">
                Choose an account
              </h2>
              <p className="text-sm font-medium text-[#8ab4f8]">
                to continue to jobscamscore.com
              </p>
            </div>

            {/* Right Column */}
            <div className="md:col-span-7 space-y-4">
              
              {/* Real Official Google Sign-In Button */}
              {isRealGoogleConfigured && (
                <div className="space-y-3 pb-2 border-b border-gray-800">
                  <button
                    type="button"
                    onClick={() => handlePopupGoogleLogin()}
                    disabled={isLoading}
                    className="w-full flex items-center justify-center gap-3 bg-white hover:bg-slate-100 text-slate-900 font-semibold py-3 px-4 rounded-full shadow-lg transition-all text-sm active:scale-[0.98] disabled:opacity-50"
                  >
                    <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24">
                      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
                      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
                    </svg>
                    <span>{isLoading ? 'Opening Google...' : 'Continue with Google Account'}</span>
                  </button>

                  <div className="flex justify-center">
                    <GoogleLogin
                      onSuccess={handleRealGoogleSuccess}
                      onError={() => error('Google Sign-In failed')}
                      theme="filled_black"
                      shape="pill"
                      text="continue_with"
                      width="320"
                    />
                  </div>
                </div>
              )}

              {/* Saved accounts / Demo selection */}
              <div className="divide-y divide-gray-800 border-b border-gray-800">
                {defaultAccounts.map((acc) => (
                  <button
                    key={acc.email}
                    type="button"
                    disabled={isLoading}
                    onClick={() => handleAccountSelect(acc.email, acc.name)}
                    className="w-full flex items-center gap-4 py-3.5 px-2 hover:bg-white/[0.04] transition-colors rounded-xl text-left group disabled:opacity-50"
                  >
                    <div className={`w-9 h-9 rounded-full ${acc.bg} text-white flex items-center justify-center font-medium text-base shrink-0 shadow-md`}>
                      {acc.initial}
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-white group-hover:text-blue-300 transition-colors truncate">
                        {acc.name}
                      </p>
                      <p className="text-xs text-gray-400 truncate">
                        {acc.email}
                      </p>
                    </div>
                  </button>
                ))}

                {/* Use another account option */}
                <button
                  type="button"
                  onClick={() => setStep('enter_email')}
                  className="w-full flex items-center gap-4 py-3.5 px-2 hover:bg-white/[0.04] transition-colors rounded-xl text-left group"
                >
                  <div className="w-9 h-9 rounded-full bg-gray-800 border border-gray-700 text-gray-300 flex items-center justify-center shrink-0">
                    <User className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white group-hover:text-blue-300 transition-colors">
                      Enter Gmail or phone manually
                    </p>
                  </div>
                </button>
              </div>

              {/* Disclaimer text */}
              <p className="text-[11px] text-gray-400 pt-4 leading-relaxed">
                Before using this app, you can review jobscamscore.com's{' '}
                <a href="#" onClick={(e) => e.preventDefault()} className="text-[#8ab4f8] hover:underline">
                  Privacy Policy
                </a>{' '}
                and{' '}
                <a href="#" onClick={(e) => e.preventDefault()} className="text-[#8ab4f8] hover:underline">
                  Terms of Service
                </a>.
              </p>
            </div>
          </div>

          {/* Footer bar */}
          <div className="bg-[#0f0f0f] border-t border-gray-800/80 px-8 py-3 flex items-center justify-between text-xs text-gray-400">
            <button type="button" className="flex items-center gap-1 hover:text-gray-200">
              <span>English (United States)</span>
              <ChevronDown className="w-3.5 h-3.5" />
            </button>
            <div className="flex items-center gap-6">
              <a href="#" onClick={(e) => e.preventDefault()} className="hover:text-gray-200">Help</a>
              <a href="#" onClick={(e) => e.preventDefault()} className="hover:text-gray-200">Privacy</a>
              <a href="#" onClick={(e) => e.preventDefault()} className="hover:text-gray-200">Terms</a>
            </div>
          </div>

        </div>
      ) : (
        <div className="relative w-full max-w-3xl bg-[#0e1117] text-white border border-white/10 rounded-3xl shadow-2xl overflow-hidden font-sans">
          
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

          {/* Top Bar */}
          <div className="flex items-center gap-2.5 px-8 pt-7 pb-4">
            <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
            </svg>
            <span className="text-sm font-medium text-gray-200">Sign in with Google</span>
          </div>

          {/* Grid Layout */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start px-8 pb-10 pt-4">
            
            {/* Left Column */}
            <div className="md:col-span-5 space-y-2 pt-1">
              <h2 className="text-3xl sm:text-4xl font-normal text-white tracking-tight">
                Sign in
              </h2>
              <p className="text-sm font-medium text-[#8ab4f8]">
                to continue to jobscamscore.com
              </p>
            </div>

            {/* Right Column */}
            <div className="md:col-span-7 space-y-5">
              
              <form onSubmit={handleNextSubmit} className="space-y-4">
                <div className="relative border border-[#8ab4f8] rounded-md bg-[#0e1117] px-3.5 py-3 focus-within:ring-1 focus-within:ring-[#8ab4f8] transition-all">
                  <label className="absolute -top-2.5 left-3 bg-[#0e1117] px-1 text-xs font-medium text-[#8ab4f8]">
                    Email or phone
                  </label>
                  <input
                    type="text"
                    required
                    autoFocus
                    value={emailOrPhone}
                    onChange={(e) => setEmailOrPhone(e.target.value)}
                    className="w-full text-base text-white bg-transparent outline-none pt-0.5"
                  />
                </div>

                <div>
                  <button
                    type="button"
                    onClick={() => error('Please enter your Gmail address above to proceed.')}
                    className="text-xs font-medium text-[#8ab4f8] hover:underline"
                  >
                    Forgot email?
                  </button>
                </div>

                <p className="text-xs text-gray-300 leading-relaxed pt-3">
                  Before using this app, you can review jobscamscore.com's{' '}
                  <a href="#" onClick={(e) => e.preventDefault()} className="text-[#8ab4f8] hover:underline font-medium">
                    Privacy Policy
                  </a>{' '}
                  and{' '}
                  <a href="#" onClick={(e) => e.preventDefault()} className="text-[#8ab4f8] hover:underline font-medium">
                    Terms of Service
                  </a>.
                </p>

                <div className="flex items-center justify-end gap-6 pt-6">
                  <button
                    type="button"
                    onClick={() => setStep('choose_account')}
                    className="text-xs font-medium text-[#8ab4f8] hover:underline"
                  >
                    Choose an account
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      if (emailOrPhone.trim()) {
                        handleNextSubmit({ preventDefault: () => {} });
                      } else {
                        setStep('choose_account');
                      }
                    }}
                    className="text-xs font-medium text-[#8ab4f8] hover:underline"
                  >
                    Create account
                  </button>

                  <button
                    type="submit"
                    disabled={isLoading}
                    className="px-6 py-2 rounded-full bg-[#a8c7fa] hover:bg-[#8ab4f8] active:bg-[#669df6] text-[#040e25] text-xs font-medium transition-all shadow-sm disabled:opacity-50"
                  >
                    {isLoading ? 'Signing in...' : 'Next'}
                  </button>
                </div>
              </form>

            </div>
          </div>

          {/* Outer Footer Bar */}
          <div className="bg-[#080a0e] border-t border-gray-800/80 px-8 py-3 flex items-center justify-between text-xs text-gray-400">
            <button type="button" className="flex items-center gap-1 hover:text-gray-200">
              <span>English (United States)</span>
              <ChevronDown className="w-3.5 h-3.5" />
            </button>
            <div className="flex items-center gap-6">
              <a href="#" onClick={(e) => e.preventDefault()} className="hover:text-gray-200">Help</a>
              <a href="#" onClick={(e) => e.preventDefault()} className="hover:text-gray-200">Privacy</a>
              <a href="#" onClick={(e) => e.preventDefault()} className="hover:text-gray-200">Terms</a>
            </div>
          </div>

        </div>
      )}

    </div>
  );
};

export default GoogleAuthModal;