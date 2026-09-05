import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  History,
  Search,
  Filter,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  ExternalLink,
  Building2,
  Calendar,
  ChevronRight,
  Download,
} from 'lucide-react';
import { analysisService } from '../services/analysisService';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { formatDate } from '../utils/formatters';

export const AnalysisHistoryPage = () => {
  const [loading, setLoading] = useState(true);
  const [history, setHistory] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRisk, setFilterRisk] = useState('ALL');
  const [isExporting, setIsExporting] = useState(false);

  const handleExportCsv = async () => {
    try {
      setIsExporting(true);
      await analysisService.exportCsv();
    } catch (err) {
      console.error('Export failed:', err);
    } finally {
      setIsExporting(false);
    }
  };

  useEffect(() => {
    let isMounted = true;
    const fetchHistory = async () => {
      try {
        setLoading(true);
        const data = await analysisService.getHistory();
        if (isMounted) {
          setHistory(Array.isArray(data) ? data : []);
        }
      } catch (err) {
        console.error('Failed to load history:', err);
        if (isMounted) {
          const local = JSON.parse(localStorage.getItem('sentinel_scan_history') || '[]');
          setHistory(local);
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchHistory();
    return () => { isMounted = false; };
  }, []);

  const filteredHistory = history.filter((item) => {
    const matchesSearch =
      item.job_title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.company_name?.toLowerCase().includes(searchTerm.toLowerCase());
    
    if (filterRisk === 'ALL') return matchesSearch;
    if (filterRisk === 'SAFE') return matchesSearch && item.risk_score < 30;
    if (filterRisk === 'MODERATE') return matchesSearch && item.risk_score >= 30 && item.risk_score < 70;
    if (filterRisk === 'RISKY') return matchesSearch && item.risk_score >= 70;
    return matchesSearch;
  });

  const totalScans = history.length;
  const safeScans = history.filter(i => i.risk_score < 30).length;
  const moderateScans = history.filter(i => i.risk_score >= 30 && i.risk_score < 70).length;
  const riskyScans = history.filter(i => i.risk_score >= 70).length;

  return (
    <div className="max-w-5xl mx-auto space-y-6 py-2 select-none">
      {/* Header matching PDF Page 10 */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-emerald-400 font-mono text-xs font-semibold uppercase tracking-wider">
            <History className="w-4 h-4" />
            <span>Audit Log & Threat Index</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Every job you've checked, saved for your protection
          </h1>
          <p className="text-xs text-slate-400 font-light">
            Review previous forensic scans, threat reports, and verification details anytime.
          </p>
        </div>
        <button
          type="button"
          onClick={handleExportCsv}
          disabled={isExporting || history.length === 0}
          className="self-start sm:self-auto flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10 hover:border-emerald-500/40 text-xs font-medium text-slate-200 hover:text-white transition-all disabled:opacity-50"
        >
          <Download className="w-4 h-4 text-emerald-400" />
          <span>{isExporting ? 'Exporting...' : 'Export CSV'}</span>
        </button>
      </div>

      {/* 4 Summary Stat Cards matching PDF Page 10 */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-4 rounded-xl glass-card border border-white/10 space-y-1">
          <span className="text-[11px] text-slate-400 font-medium">Total scans performed</span>
          <div className="text-2xl font-bold text-white font-mono">{totalScans}</div>
        </div>
        <div className="p-4 rounded-xl glass-card border border-emerald-500/30 bg-emerald-950/20 space-y-1">
          <span className="text-[11px] text-emerald-400 font-medium">Rated safe</span>
          <div className="text-2xl font-bold text-emerald-400 font-mono">{safeScans}</div>
        </div>
        <div className="p-4 rounded-xl glass-card border border-amber-500/30 bg-amber-950/20 space-y-1">
          <span className="text-[11px] text-amber-400 font-medium">Need review</span>
          <div className="text-2xl font-bold text-amber-400 font-mono">{moderateScans}</div>
        </div>
        <div className="p-4 rounded-xl glass-card border border-red-500/30 bg-red-950/20 space-y-1">
          <span className="text-[11px] text-red-400 font-medium">Flagged risky</span>
          <div className="text-2xl font-bold text-red-400 font-mono">{riskyScans}</div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-4 rounded-xl glass-card border border-white/10">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search history by job title or company..."
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-black/50 border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500/50"
          />
        </div>

        <div className="flex items-center gap-2 text-xs">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={filterRisk}
            onChange={(e) => setFilterRisk(e.target.value)}
            className="px-3 py-2 rounded-xl bg-black/50 border border-white/10 text-xs text-white focus:outline-none focus:border-emerald-500/50"
          >
            <option value="ALL">All risk levels</option>
            <option value="SAFE">Safe Verdicts</option>
            <option value="MODERATE">Moderate Risk</option>
            <option value="RISKY">High Risk Only</option>
          </select>
        </div>
      </div>

      {/* History List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner text="Loading scan audit logs..." size="md" />
        </div>
      ) : filteredHistory.length === 0 ? (
        <div className="text-center py-12 glass-card rounded-2xl border border-white/10 space-y-3">
          <History className="w-10 h-10 text-slate-500 mx-auto" />
          <h3 className="text-sm font-bold text-white">No Matching History Found</h3>
          <p className="text-xs text-slate-400">Try adjusting your search keywords or risk level filters.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredHistory.map((scan) => {
            const isSafe = scan.risk_score < 30;
            const isModerate = scan.risk_score >= 30 && scan.risk_score < 70;
            return (
              <div
                key={scan.id}
                className="p-4 sm:p-5 rounded-2xl glass-card border border-white/10 hover:border-white/20 transition-all flex flex-wrap items-center justify-between gap-4 group"
              >
                <div className="space-y-1.5 min-w-[260px] flex-1">
                  <div className="flex items-center gap-2">
                    <span className={
                      'px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase tracking-wider border ' +
                      (isSafe ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' :
                       isModerate ? 'bg-amber-500/20 text-amber-400 border-amber-500/30' :
                       'bg-red-500/20 text-red-400 border-red-500/30')
                    }>
                      {isSafe ? 'SAFE' : isModerate ? 'CAUTION' : 'HIGH RISK'} ({100 - scan.risk_score}% LEGIT)
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono">Source: {scan.source_type || 'Text'}</span>
                  </div>

                  <h3 className="text-base font-bold text-white group-hover:text-emerald-400 transition-colors">
                    {scan.job_title}
                  </h3>

                  <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400">
                    <span className="flex items-center gap-1.5 text-slate-300 font-medium">
                      <Building2 className="w-3.5 h-3.5 text-emerald-400" />
                      {scan.company_name}
                    </span>
                    <span>•</span>
                    <span className="flex items-center gap-1.5 font-mono text-[11px]">
                      <Calendar className="w-3.5 h-3.5 text-slate-500" />
                      {formatDate(scan.created_at)}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <Link
                    to={'/analysis/' + scan.id}
                    className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-xs font-semibold text-emerald-300 transition-all"
                  >
                    <span>View Report</span>
                    <ChevronRight className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default AnalysisHistoryPage;
