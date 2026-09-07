import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  SearchCode,
  History,
  AlertTriangle,
  LogOut,
  ShieldCheck,
  Settings,
  Lock,
  FileText,
  HelpCircle,
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

  const displayName = user?.full_name || user?.username || (user?.email ? user.email.split('@')[0] : 'denvermh64');
  const scansCount = 1; // Or dynamic scan count

  const links = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/scan', label: 'Scan Job', icon: SearchCode },
    { to: '/history', label: 'History', icon: History },
    { to: '/report-scam', label: 'Report a scam', icon: AlertTriangle },
  ];

  return (
    <aside className="w-64 shrink-0 hidden lg:flex flex-col border-r border-white/10 bg-[#070b09] min-h-[calc(100vh-4rem)] p-4 justify-between select-none">
      <div className="space-y-6">
        {/* Brand Header */}
        <div className="px-2 pt-1 space-y-2">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shadow-sm">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <span className="text-base font-bold tracking-tight text-white font-sans">
                JobScam<span className="text-white">Score</span>
              </span>
            </div>
          </div>
          
          <div className="text-[10px] font-mono font-semibold text-slate-400 tracking-wider">
            FREE PLAN • 100 SCANS/MONTH
          </div>
        </div>

        {/* Navigation Section */}
        <div className="space-y-1.5 pt-1">
          {links.map((link) => {
            const Icon = link.icon;
            return (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all duration-150 ${
                    isActive
                      ? 'bg-white/10 text-white font-semibold shadow-inner'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <div className="flex items-center gap-3">
                      <Icon className={`w-4 h-4 ${isActive ? 'text-emerald-400' : 'text-slate-400'}`} />
                      <span>{link.label}</span>
                    </div>
                    {isActive && (
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399]" />
                    )}
                  </>
                )}
              </NavLink>
            );
          })}
        </div>
      </div>

      {/* Footer & User Profile Section */}
      <div className="space-y-4 pt-4">
        {/* User Card */}
        <div className="p-3.5 rounded-xl bg-white/[0.02] border border-white/10 space-y-2.5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-white truncate max-w-[110px] font-sans">
              {displayName}
            </span>
            <div className="flex items-center gap-1.5">
              <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-950/80 text-emerald-400 border border-emerald-500/30 uppercase tracking-wider font-mono">
                FREE
              </span>
              <button
                onClick={() => navigate('/settings')}
                className="text-slate-500 hover:text-slate-300 transition-colors p-0.5"
                title="Settings"
              >
                <Settings className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-[11px] text-slate-400">
              <span>Scans used</span>
              <span className="font-mono text-slate-300">1 / 100</span>
            </div>
            <div className="w-full h-1 rounded-full bg-white/10 overflow-hidden">
              <div className="h-full bg-emerald-400 rounded-full" style={{ width: '1%' }} />
            </div>
          </div>

          <button
            onClick={handleSignOut}
            type="button"
            className="w-full mt-2 flex items-center gap-2 py-1 text-xs font-medium text-slate-400 hover:text-red-400 transition-colors pt-2 border-t border-white/5"
          >
            <LogOut className="w-3.5 h-3.5 rotate-180" />
            <span>Sign Out</span>
          </button>
        </div>

        {/* Legal / Help Footer */}
        <div className="flex items-center justify-center gap-3 text-[11px] text-slate-500">
          <span className="hover:text-slate-400 cursor-pointer">Privacy</span>
          <span>•</span>
          <span className="hover:text-slate-400 cursor-pointer">Terms</span>
          <span>•</span>
          <span className="hover:text-slate-400 cursor-pointer">Help</span>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
