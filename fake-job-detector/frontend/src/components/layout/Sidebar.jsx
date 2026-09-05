import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  SearchCode,
  History,
  ShieldAlert,
  LogOut,
  Shield,
  HelpCircle,
  FileText,
  Lock
} from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';

export const Sidebar = () => {
  const { user, logout, hasUsedGuestScan } = useAuth();
  const navigate = useNavigate();

  const handleSignOut = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (err) {
      console.error('Logout error:', err);
    }
  };

  const links = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/scan', label: 'Scan Job', icon: SearchCode, isScan: true },
    { to: '/history', label: 'History', icon: History },
    { to: '/report-scam', label: 'Report a scam', icon: ShieldAlert },
  ];

  return (
    <aside className="w-64 shrink-0 hidden lg:flex flex-col border-r border-white/10 bg-[#08090c] min-h-[calc(100vh-4rem)] p-3.5 justify-between select-none">
      <div className="space-y-5">
        {/* Brand Header */}
        <div className="px-2 py-1 space-y-2">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 shadow-sm">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <span className="text-base font-bold tracking-tight text-white font-sans">
                JobScam<span className="text-emerald-400">Score</span>
              </span>
            </div>
          </div>
          
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-950/60 border border-emerald-500/30 text-[10px] font-semibold text-emerald-300 uppercase tracking-wider">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>FREE PLAN • 100 SCANS/MONTH</span>
          </div>
        </div>

        {/* Navigation Section */}
        <div className="space-y-1 pt-2">
          {links.map((link) => {
            const Icon = link.icon;
            return (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition-all duration-150 ${
                    isActive
                      ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-white/5 border border-transparent'
                  }`
                }
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4" />
                  <span>{link.label}</span>
                </div>
                {link.isScan && (
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_#34d399]" />
                )}
              </NavLink>
            );
          })}
        </div>
      </div>

      {/* Footer & User Section */}
      <div className="space-y-4 pt-4 border-t border-white/10">
        {/* User Quota Card */}
        <div className="p-3.5 rounded-xl bg-white/[0.03] border border-white/10 space-y-2.5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 min-w-0">
              <div className="w-7 h-7 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-xs font-bold text-emerald-300 shrink-0 font-mono">
                {(user ? (user?.username || user?.email || "U") : "G").charAt(0).toUpperCase()}
              </div>
              <div className="min-w-0">
                <p className="text-xs font-semibold text-white truncate font-mono">
                  {user ? (user?.username || user?.email?.split("@")[0]) : "Guest Visitor"}
                </p>
              </div>
            </div>
            <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 uppercase tracking-wider font-mono">
              {user ? "FREE" : "GUEST"}
            </span>
          </div>

          <div className="space-y-1 pt-1">
            <div className="flex items-center justify-between text-[11px]">
              <span className="text-slate-400 font-light">{user ? "0 / 100 Scans used" : (hasUsedGuestScan ? "1 / 1 Guest scan used" : "0 / 1 Guest scan used")}</span>
              <span className="text-emerald-400 font-mono font-medium">0%</span>
            </div>
            <div className="w-full h-1.5 rounded-full bg-white/10 overflow-hidden">
              <div className="h-full bg-emerald-400 rounded-full transition-all duration-300" style={{ width: user ? "0%" : (hasUsedGuestScan ? "100%" : "0%") }} />
            </div>
          </div>

          <button
            onClick={handleSignOut}
            type="button"
            className="w-full mt-2 flex items-center justify-center gap-2 py-1.5 px-3 rounded-lg bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-[11px] font-medium text-red-300 transition-colors"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Sign Out</span>
          </button>
        </div>

        {/* Legal Links */}
        <div className="flex items-center justify-center gap-3 text-[11px] text-slate-500 pt-1">
          <span className="hover:text-slate-300 cursor-pointer flex items-center gap-1"><Lock className="w-3 h-3" /> Privacy</span>
          <span>•</span>
          <span className="hover:text-slate-300 cursor-pointer flex items-center gap-1"><FileText className="w-3 h-3" /> Terms</span>
          <span>•</span>
          <span className="hover:text-slate-300 cursor-pointer flex items-center gap-1"><HelpCircle className="w-3 h-3" /> Help</span>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
