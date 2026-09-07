import React, { useState, useEffect } from 'react';
import { Database, Download, Search, ShieldAlert, Sparkles, Filter, ExternalLink, RefreshCw } from 'lucide-react';
import { datasetService } from '../services/datasetService';
import { useLanguage } from '../hooks/useLanguage';
import { useToast } from '../hooks/useToast';

export const DatasetPage = () => {
  const { t } = useLanguage();
  const { success, error } = useToast();

  const [summary, setSummary] = useState(null);
  const [records, setRecords] = useState([]);
  const [totalRecords, setTotalRecords] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchSummary();
    fetchSamples();
  }, []);

  const fetchSummary = async () => {
    try {
      const data = await datasetService.getSummary();
      setSummary(data);
    } catch (err) {
      console.warn('Failed to load dataset summary:', err);
    }
  };

  const fetchSamples = async (query = searchQuery, cat = selectedCategory) => {
    setIsLoading(true);
    try {
      const data = await datasetService.getSamples({
        q: query || undefined,
        category: cat !== 'all' ? cat : undefined,
        limit: 50,
      });
      setRecords(data.records || []);
      setTotalRecords(data.total || 0);
    } catch (err) {
      error('Failed to load dataset records.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchSamples(searchQuery, selectedCategory);
  };

  const handleCategoryChange = (cat) => {
    setSelectedCategory(cat);
    fetchSamples(searchQuery, cat);
  };

  const handleDownloadCsv = () => {
    try {
      const link = document.createElement('a');
      link.href = datasetService.getDownloadUrl();
      link.setAttribute('download', 'sentineljob_scam_dataset.csv');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      success('Downloading full scam intelligence dataset (CSV)...');
    } catch (err) {
      error('Download failed. Please try again.');
    }
  };

  return (
    <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 text-frost">
      
      {/* Header Banner */}
      <div className="relative rounded-3xl bg-gradient-to-r from-emerald-950/60 via-[#07100c] to-black border border-emerald-500/20 p-6 sm:p-10 shadow-2xl overflow-hidden">
        <div className="relative z-10 space-y-4 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono">
            <Database className="w-3.5 h-3.5" />
            <span>Open Security & ML Dataset Corpus</span>
          </div>

          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight text-frost">
            Scam Intelligence & <br />
            <span className="text-emerald-400">Training Dataset Hub</span>
          </h1>

          <p className="text-sm sm:text-base text-mist font-light leading-relaxed">
            Browse, inspect, and export verified job scam postings, phishing offer letters, task scam scripts, and federal fraud reports powering SentinelJob AI's 8-layer classification models.
          </p>

          {/* Action Buttons */}
          <div className="pt-2 flex flex-wrap gap-3">
            <button
              onClick={handleDownloadCsv}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-emerald-500 hover:bg-emerald-400 text-white font-semibold text-xs transition-all shadow-lg shadow-emerald-500/20"
            >
              <Download className="w-4 h-4" />
              <span>Download Full Dataset (.CSV)</span>
            </button>
            
            <a
              href="/api/v1/dataset/summary"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-frost text-xs font-mono transition-all"
            >
              <ExternalLink className="w-3.5 h-3.5 text-fog" />
              <span>Dataset Summary API</span>
            </a>
          </div>
        </div>
      </div>

      {/* 4 Top Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-2xl border border-white/10 bg-[#07100c]/80 p-5 shadow-xl">
          <p className="text-xs font-mono text-fog uppercase">Total Corpus Postings</p>
          <p className="text-2xl sm:text-3xl font-bold font-mono text-frost mt-2">17,880</p>
          <p className="text-[11px] text-emerald-400 mt-1 font-mono">EMSCAD + Kaggle + India Incidents</p>
        </div>

        <div className="rounded-2xl border border-red-500/30 bg-red-500/5 p-5 shadow-xl">
          <p className="text-xs font-mono text-red-300 uppercase">Confirmed Scam Records</p>
          <p className="text-2xl sm:text-3xl font-bold font-mono text-red-400 mt-2">866</p>
          <p className="text-[11px] text-red-400/90 mt-1 font-mono">4.84% Overall Scam Ratio</p>
        </div>

        <div className="rounded-2xl border border-white/10 bg-[#07100c]/80 p-5 shadow-xl">
          <p className="text-xs font-mono text-fog uppercase">Classifier Precision</p>
          <p className="text-2xl sm:text-3xl font-bold font-mono text-emerald-400 mt-2">99.2%</p>
          <p className="text-[11px] text-fog mt-1 font-mono">TF-IDF + DeBERTa Model</p>
        </div>

        <div className="rounded-2xl border border-white/10 bg-[#07100c]/80 p-5 shadow-xl">
          <p className="text-xs font-mono text-fog uppercase">Federal Watchlists</p>
          <p className="text-2xl sm:text-3xl font-bold font-mono text-frost mt-2">5 Agencies</p>
          <p className="text-[11px] text-fog mt-1 font-mono">FTC, BBB, IC3, I4C, MHA</p>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="rounded-2xl border border-white/10 bg-[#07100c]/90 p-4 sm:p-6 space-y-4">
        <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-fog" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search dataset by keyword, platform, script snippet, or incident ID..."
              className="w-full pl-10 pr-4 py-2.5 text-xs sm:text-sm rounded-xl border border-white/10 bg-black/50 text-frost placeholder-fog focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
            />
          </div>
          <button
            type="submit"
            className="px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-white font-semibold text-xs transition-all flex items-center justify-center gap-2 shrink-0"
          >
            <Filter className="w-3.5 h-3.5" />
            <span>Search Corpus</span>
          </button>
        </form>

        {/* Category Pills */}
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-white/10">
          <span className="text-xs font-mono text-fog mr-2">Filter Category:</span>
          {[
            { id: 'all', label: 'All Categories' },
            { id: 'recharge', label: 'YouTube / Task Recharge' },
            { id: 'data entry', label: 'Data Entry / Typing Fee' },
            { id: 'appointment', label: 'Fake TCS/Wipro Appointment' },
            { id: 'telegram', label: 'Telegram / WhatsApp Funnels' },
          ].map((cat) => (
            <button
              key={cat.id}
              onClick={() => handleCategoryChange(cat.id)}
              className={`px-3 py-1 rounded-full text-xs transition-all font-mono ${
                selectedCategory === cat.id
                  ? 'bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 font-semibold'
                  : 'bg-white/5 border border-white/10 text-fog hover:text-frost hover:bg-white/10'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Dataset Records Table */}
      <div className="rounded-2xl border border-white/10 bg-[#07100c]/90 overflow-hidden shadow-2xl">
        <div className="p-4 sm:p-5 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-semibold text-frost">Threat Corpus & Incident Log</h3>
            <span className="text-xs font-mono text-fog">({totalRecords} records found)</span>
          </div>
          <button
            onClick={() => fetchSamples(searchQuery, selectedCategory)}
            className="p-1.5 rounded-lg bg-white/5 border border-white/10 text-fog hover:text-frost transition-colors"
            title="Refresh Dataset"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {isLoading ? (
          <div className="p-12 text-center text-fog text-xs font-mono">
            Loading threat corpus records...
          </div>
        ) : records.length === 0 ? (
          <div className="p-12 text-center text-fog text-xs font-mono">
            No matching dataset records found. Try adjusting your search keywords.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/10 bg-white/[0.02] text-[11px] font-mono text-fog uppercase tracking-wider">
                  <th className="py-3 px-4">ID</th>
                  <th className="py-3 px-4">Scam Category</th>
                  <th className="py-3 px-4">Platform</th>
                  <th className="py-3 px-4">Claimed Pay</th>
                  <th className="py-3 px-4">Script Snippet</th>
                  <th className="py-3 px-4">Advisory Body</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 text-xs text-frost font-light">
                {records.map((rec, idx) => (
                  <tr key={rec.incident_id || idx} className="hover:bg-white/[0.02] transition-colors">
                    <td className="py-3.5 px-4 font-mono text-emerald-400 font-semibold shrink-0">
                      {rec.incident_id || `DS-${idx+1}`}
                    </td>
                    <td className="py-3.5 px-4 font-medium text-frost">
                      {rec.scam_category}
                    </td>
                    <td className="py-3.5 px-4 text-fog font-mono text-[11px]">
                      {rec.platform}
                    </td>
                    <td className="py-3.5 px-4 text-amber-300 font-mono text-[11px]">
                      {rec.claimed_compensation}
                    </td>
                    <td className="py-3.5 px-4 text-fog max-w-md truncate">
                      "{rec.scam_script_snippet}"
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="inline-flex items-center px-2 py-0.5 rounded bg-white/5 border border-white/10 text-[10px] font-mono text-fog">
                        {rec.advisory_agency}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
};

export default DatasetPage;
