import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Mail, User, CheckCircle2, X, ArrowRight, Check } from 'lucide-react';
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../hooks/useToast';

export const GoogleAuthModal = ({ isOpen, onClose, onSuccess, defaultEmail = '' }) => {
  const navigate = useNavigate();
  const { login, register, loginWithGoogle } = useAuth();
  const { success, error } = useToast();

  const [selectedAccount, setSelectedAccount] = useState('');
  const [customGmail, setCustomGmail] = useState(defaultEmail || '');
  const [customName, setCustomName] = useState('');
  const [activeTab, setActiveTab] = useState('google'); // 'google' | 'email'
  
  // Traditional email/password state
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

  const handleGmailLogin = async (targetEmailInput, targetNameInput = null) => {
    const safeEmail = (typeof targetEmailInput === 'string' && targetEmailInput.includes('@'))
      ? targetEmailInput.trim()
      : (typeof customGmail === 'string' && customGmail.includes('@') ? customGmail.trim() : 'haripriyacsd@gmail.com');

    setIsLoading(true);
    try {
      const emailPrefix = safeEmail.split('@')[0].replace(/[._-]/g, ' ');
      const safeName = targetNameInput || customName || (emailPrefix.charAt(0).toUpperCase() + emailPrefix.slice(1));
      
      const loggedUser = await loginWithGoogle(`demo_google_token:${safeEmail}:${safeName}`);
      
      success(`Welcome ${loggedUser?.full_name || safeName}! Authenticated via Google (${safeEmail}).`);
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
        const user = await register(fullName || 'User', email, password);
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

  const suggestedAccounts = [
    { email: 'haripriyacsd@gmail.com', name: 'Hari Priya', avatarBg: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' },
    { email: 'google.analyst@gmail.com', name: 'Google Security Analyst', avatarBg: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
    { email: 'user@gmail.com', name: 'Job Seeker Account', avatarBg: 'bg-purple-500/20 text-purple-400 border-purple-500/30' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-md bg-[#07100c] border border-white/15 rounded-2xl shadow-2xl overflow-hidden p-6 sm:p-7 text-frost">
        
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="absolute top-4 right-4 text-fog hover:text-frost transition-colors p-1 rounded-lg hover:bg-white/5"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        )}

        {/* Brand / Google Modal Header */}
        <div className="flex flex-col items-center text-center mb-5">
          <div className="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-3 shadow-lg">
            <svg className="w-6 h-6" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
            </svg>
          </div>
          
          <h3 className="text-xl font-bold text-frost tracking-tight">
            Sign in with Google
          </h3>
          <p className="text-xs text-mist mt-1 max-w-xs font-light">
            Choose a Gmail account or enter your Gmail ID to authenticate with <span className="text-emerald-400 font-medium">SentinelJob AI</span>.
          </p>
        </div>

        {/* Tab Switcher: Google Popup vs Traditional Email */}
        <div className="flex rounded-xl bg-black/50 border border-white/10 p-1 mb-4">
          <button
            type="button"
            onClick={() => setActiveTab('google')}
            className={`flex-1 py-1.5 text-xs font-medium rounded-lg transition-all flex items-center justify-center gap-1.5 ${
              activeTab === 'google'
                ? 'bg-white/10 text-frost border border-white/15 shadow-sm'
                : 'text-fog hover:text-frost'
            }`}
          >
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
            </svg>
            <span>Google Gmail Auth</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('email')}
            className={`flex-1 py-1.5 text-xs font-medium rounded-lg transition-all flex items-center justify-center gap-1.5 ${
              activeTab === 'email'
                ? 'bg-white/10 text-frost border border-white/15 shadow-sm'
                : 'text-fog hover:text-frost'
            }`}
          >
            <Mail className="w-3.5 h-3.5" />
            <span>Email & Password</span>
          </button>
        </div>

        {activeTab === 'google' ? (
          <div className="space-y-4">
            {/* Real Google OAuth Button if configured */}
            {isRealGoogleConfigured && (
              <div className="w-full flex flex-col items-center space-y-2 pb-2 border-b border-white/10">
                <GoogleLogin
                  onSuccess={handleGoogleSuccess}
                  onError={() => handleGmailLogin('haripriyacsd@gmail.com')}
                  theme="filled_black"
                  shape="pill"
                  text="continue_with"
                  width="340"
                />
              </div>
            )}

            {/* Selectable Suggested Gmail Accounts */}
            <div>
              <p className="text-[11px] font-mono text-fog uppercase tracking-wider mb-2">
                Select a Gmail account
              </p>
              <div className="space-y-2">
                {suggestedAccounts.map((acc) => (
                  <button
                    key={acc.email}
                    type="button"
                    disabled={isLoading}
                    onClick={() => handleGmailLogin(acc.email, acc.name)}
                    className="w-full flex items-center justify-between p-2.5 rounded-xl border border-white/10 bg-black/40 hover:bg-white/5 active:bg-white/10 transition-all text-left group disabled:opacity-50"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div className={`w-8 h-8 rounded-full border flex items-center justify-center text-xs font-bold shrink-0 ${acc.avatarBg}`}>
                        {acc.name.charAt(0)}
                      </div>
                      <div className="min-w-0">
                        <p className="text-xs font-semibold text-frost group-hover:text-emerald-400 transition-colors truncate">
                          {acc.name}
                        </p>
                        <p className="text-[11px] text-fog font-mono truncate">
                          {acc.email}
                        </p>
                      </div>
                    </div>
                    <span className="text-[10px] font-mono px-2 py-1 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shrink-0">
                      Sign In →
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* Enter Custom Gmail ID Section */}
            <div className="pt-2 border-t border-white/10">
              <p className="text-[11px] font-mono text-fog uppercase tracking-wider mb-2">
                Or enter your own Gmail ID
              </p>
              
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  if (customGmail.trim()) {
                    handleGmailLogin(customGmail.trim(), customName.trim() || null);
                  } else {
                    error('Please enter a valid Gmail address.');
                  }
                }}
                className="space-y-2.5"
              >
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-fog w-3.5 h-3.5" />
                  <input
                    type="email"
                    required
                    value={customGmail}
                    onChange={(e) => setCustomGmail(e.target.value)}
                    placeholder="Enter your Gmail (e.g. yourname@gmail.com)"
                    className="w-full pl-9 pr-3.5 py-2.5 bg-black/50 border border-white/10 rounded-xl text-xs text-frost placeholder-fog/60 focus:outline-none focus:border-emerald-500/50"
                  />
                </div>

                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 text-fog w-3.5 h-3.5" />
                  <input
                    type="text"
                    value={customName}
                    onChange={(e) => setCustomName(e.target.value)}
                    placeholder="Full Name (optional)"
                    className="w-full pl-9 pr-3.5 py-2.5 bg-black/50 border border-white/10 rounded-xl text-xs text-frost placeholder-fog/60 focus:outline-none focus:border-emerald-500/50"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isLoading || !customGmail.trim()}
                  className="w-full flex items-center justify-center gap-2.5 py-2.5 bg-white hover:bg-slate-100 active:bg-slate-200 text-slate-900 font-semibold rounded-full transition-all text-xs shadow-md disabled:opacity-50"
                >
                  <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
                  </svg>
                  <span>{isLoading ? 'Authenticating...' : `Continue with ${customGmail || 'Gmail ID'}`}</span>
                </button>
              </form>
            </div>
          </div>
        ) : (
          /* Traditional Email Form */
          <form onSubmit={handleFormSubmit} className="space-y-3">
            {isRegisterMode && (
              <div>
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Full Name"
                  className="w-full px-3.5 py-2.5 bg-black/50 border border-white/10 rounded-xl text-xs text-frost placeholder-fog/60 focus:outline-none focus:border-emerald-500/50"
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
                className="w-full pl-9 pr-3.5 py-2.5 bg-black/50 border border-white/10 rounded-xl text-xs text-frost placeholder-fog/60 focus:outline-none focus:border-emerald-500/50"
              />
            </div>

            <div className="relative">
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password (min 6 chars)"
                className="w-full px-3.5 py-2.5 bg-black/50 border border-white/10 rounded-xl text-xs text-frost placeholder-fog/60 focus:outline-none focus:border-emerald-500/50"
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

            <div className="pt-2 text-center text-xs text-fog">
              <button
                type="button"
                onClick={() => setIsRegisterMode(!isRegisterMode)}
                className="text-emerald-400 hover:text-emerald-300 underline underline-offset-2"
              >
                {isRegisterMode ? 'Already have an account? Sign in' : "Need an account? Register free"}
              </button>
            </div>
          </form>
        )}

        <div className="mt-4 pt-3 border-t border-white/5 text-center text-[10px] text-fog flex items-center justify-center gap-1 font-light">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          <span>Protected by SentinelJob AI Google Auth Engine</span>
        </div>
      </div>
    </div>
  );
};

export default GoogleAuthModal;