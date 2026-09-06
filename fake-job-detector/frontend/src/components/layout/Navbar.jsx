import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { ShieldCheck, User, LogOut, Menu, X, Shield, History } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { LanguageSelector } from '../navigation/LanguageSelector';
import { TopAdvisoryBar } from '../navigation/TopAdvisoryBar';

export const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <div className="sticky top-0 z-50 w-full">
      {/* Top Advisory Bar */}
      <TopAdvisoryBar />

      {/* Floating Navbar Container */}
      <header className="pt-3 px-4 sm:px-6 lg:px-10 max-w-[1400px] mx-auto">
        <nav className="flex rounded-full py-2.5 pl-4 pr-3.5 backdrop-blur-md bg-[#050a08]/85 border border-white/10 shadow-hairline-inset items-center justify-between transition-all">
          
          {/* Brand Logo & Title */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 group-hover:scale-105 transition-all">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-medium text-frost tracking-tight">SentinelJob AI</span>
            </div>
          </Link>

          {/* Center Navigation Links matching reference */}
          <div className="hidden md:flex items-center gap-7 text-sm font-medium text-fog">
            <Link
              to="/analyze"
              className={`hover:text-frost transition-colors ${
                isActive('/analyze') || isActive('/scan') ? 'text-frost font-semibold' : ''
              }`}
            >
              Job Scam Checker
            </Link>

            <Link
              to="/database"
              className={`hover:text-frost transition-colors ${
                isActive('/database') || isActive('/scams') ? 'text-frost font-semibold' : ''
              }`}
            >
              Scam Database
            </Link>

            <Link
              to="/guides/job-scam-red-flags"
              className={`hover:text-frost transition-colors ${
                isActive('/guides/job-scam-red-flags') ? 'text-frost font-semibold' : ''
              }`}
            >
              Red Flags Guide
            </Link>

            <Link
              to="/simulator"
              className={`flex items-center gap-1.5 hover:text-frost transition-colors ${
                isActive('/simulator') || isActive('/game') ? 'text-frost font-semibold' : ''
              }`}
            >
              <span>Scam Simulator</span>
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30">
                Game
              </span>
            </Link>
          </div>

          {/* Right Actions: Language Selector & Auth */}
          <div className="hidden md:flex items-center gap-3">
            <LanguageSelector />

            {isAuthenticated ? (
              <div className="relative">
                <button
                  onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                  className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 hover:bg-white/10 px-3 py-1.5 transition-all text-xs text-frost"
                >
                  <div className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-[10px]">
                    {user?.full_name?.charAt(0) || 'U'}
                  </div>
                  <span className="truncate max-w-[100px]">{user?.full_name || 'Analyst'}</span>
                </button>

                {userDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-52 rounded-2xl bg-[#07100c]/95 backdrop-blur-xl border border-white/15 shadow-2xl p-2 z-50">
                    <div className="px-3 py-2 border-b border-white/10">
                      <p className="text-xs font-semibold text-frost">{user?.full_name}</p>
                      <p className="text-[10px] text-fog truncate">{user?.email}</p>
                    </div>
                    <Link
                      to="/dashboard"
                      onClick={() => setUserDropdownOpen(false)}
                      className="flex items-center gap-2 px-3 py-2 text-xs text-mist hover:text-frost hover:bg-white/5 rounded-xl mt-1"
                    >
                      <Shield className="w-3.5 h-3.5 text-emerald-400" />
                      Dashboard
                    </Link>
                    <Link
                      to="/history"
                      onClick={() => setUserDropdownOpen(false)}
                      className="flex items-center gap-2 px-3 py-2 text-xs text-mist hover:text-frost hover:bg-white/5 rounded-xl"
                    >
                      <History className="w-3.5 h-3.5 text-emerald-400" />
                      Scan History & Vault
                    </Link>
                    <Link
                      to="/settings"
                      onClick={() => setUserDropdownOpen(false)}
                      className="flex items-center gap-2 px-3 py-2 text-xs text-mist hover:text-frost hover:bg-white/5 rounded-xl"
                    >
                      <User className="w-3.5 h-3.5 text-skywash" />
                      Settings & API
                    </Link>
                    <div className="border-t border-white/10 my-1" />
                    <button
                      onClick={handleLogout}
                      className="flex items-center gap-2 w-full px-3 py-2 text-xs text-danger-bright hover:bg-danger/10 rounded-xl transition-colors"
                    >
                      <LogOut className="w-3.5 h-3.5" />
                      Sign Out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="text-xs font-medium text-fog hover:text-frost px-3 py-1.5 rounded-full transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="text-xs font-semibold text-white bg-emerald-500 hover:bg-emerald-400 px-3.5 py-1.5 rounded-full shadow-sm hover:shadow-emerald-glow transition-all"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="flex md:hidden items-center gap-2">
            <LanguageSelector />
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-1.5 rounded-full bg-white/5 border border-white/10 text-mist hover:text-frost transition-colors"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </nav>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden mt-2 rounded-2xl border border-white/10 bg-[#07100c]/95 backdrop-blur-xl p-4 space-y-3 shadow-2xl animate-in fade-in duration-150">
            <nav className="flex flex-col space-y-1">
              <Link
                to="/"
                onClick={() => setMobileMenuOpen(false)}
                className="px-3 py-2 rounded-xl text-xs text-mist hover:text-frost hover:bg-white/5"
              >
                Overview
              </Link>
              <Link
                to="/analyze"
                onClick={() => setMobileMenuOpen(false)}
                className="px-3 py-2 rounded-xl text-xs text-mist hover:text-frost hover:bg-white/5"
              >
                Job Scam Checker
              </Link>
              <Link
                to="/database"
                onClick={() => setMobileMenuOpen(false)}
                className="px-3 py-2 rounded-xl text-xs text-mist hover:text-frost hover:bg-white/5"
              >
                Scam Database
              </Link>
              <Link
                to="/guides/job-scam-red-flags"
                onClick={() => setMobileMenuOpen(false)}
                className="px-3 py-2 rounded-xl text-xs text-mist hover:text-frost hover:bg-white/5"
              >
                Red Flags Guide
              </Link>
              <Link
                to="/simulator"
                onClick={() => setMobileMenuOpen(false)}
                className="px-3 py-2 rounded-xl text-xs text-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/10 font-semibold"
              >
                🎮 Scam Hunter Simulator
              </Link>
              <Link
                to="/dashboard"
                onClick={() => setMobileMenuOpen(false)}
                className="px-3 py-2 rounded-xl text-xs text-mist hover:text-frost hover:bg-white/5"
              >
                Threat Dashboard
              </Link>
              <Link
                to="/history"
                onClick={() => setMobileMenuOpen(false)}
                className="px-3 py-2 rounded-xl text-xs text-mist hover:text-frost hover:bg-white/5"
              >
                Scan Vault
              </Link>
              <Link
                to="/settings"
                onClick={() => setMobileMenuOpen(false)}
                className="px-3 py-2 rounded-xl text-xs text-mist hover:text-frost hover:bg-white/5"
              >
                Settings
              </Link>
            </nav>

            <div className="pt-2 border-t border-white/10 flex flex-col gap-2">
              {isAuthenticated ? (
                <button
                  onClick={() => {
                    setMobileMenuOpen(false);
                    handleLogout();
                  }}
                  className="w-full flex items-center justify-center gap-2 py-2 rounded-xl text-xs text-danger-bright bg-danger/10"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  Sign Out
                </button>
              ) : (
                <div className="grid grid-cols-2 gap-2">
                  <Link
                    to="/login"
                    onClick={() => setMobileMenuOpen(false)}
                    className="flex items-center justify-center py-2 rounded-full border border-white/10 text-xs text-frost hover:bg-white/5"
                  >
                    Sign In
                  </Link>
                  <Link
                    to="/register"
                    onClick={() => setMobileMenuOpen(false)}
                    className="flex items-center justify-center py-2 rounded-full bg-emerald-500 text-xs font-semibold text-white hover:bg-emerald-400"
                  >
                    Get Started
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}
      </header>
    </div>
  );
};

export default Navbar;
