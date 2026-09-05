import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  AlertTriangle,
  ArrowLeft,
  ShieldAlert,
  Calendar,
  MapPin,
  PlusCircle,
  ExternalLink,
  Search,
  CheckCircle,
  X,
} from 'lucide-react';
import { LanguageSelector } from '../components/navigation/LanguageSelector';
import { Modal } from '../components/ui/Modal';
import { useToast } from '../hooks/useToast';

const INITIAL_ALERTS = [
  {
    id: 'alert-1',
    title: 'Delivery Operations Specialist',
    company_or_pattern: 'Fake logistics / reshipping scam',
    tag: 'RESHIPPING',
    tag_color: 'bg-red-500/10 text-red-400 border-red-500/30',
    location: 'Remote (US)',
    date: 'Dec 2025',
    description: 'Victims are sent stolen goods to re-label and ship abroad under the guise of an "e-commerce quality inspector" role. You become a package mule liable for stolen mail.',
  },
  {
    id: 'alert-2',
    title: 'Quality Control Manager – Work From Home',
    company_or_pattern: 'Scammers impersonating major retailers',
    tag: 'RESHIPPING',
    tag_color: 'bg-red-500/10 text-red-400 border-red-500/30',
    location: 'Remote (Worldwide)',
    date: 'Dec 2025',
    description: 'Fraudsters impersonate Target and Walmart logistics teams offering $32/hr. Demands candidates receive packages at home and ship them via prepaid labels.',
  },
  {
    id: 'alert-3',
    title: 'Remote Data Entry / Task-Based Pay',
    company_or_pattern: 'Unsolicited WhatsApp/Telegram job offers',
    tag: 'TASK SCAM',
    tag_color: 'bg-red-500/10 text-red-400 border-red-500/30',
    location: 'Remote',
    date: 'Nov 2025',
    description: 'Direct WhatsApp/SMS messages promising $200–$500/day for liking YouTube videos, rating hotel apps, or boosting products. Requires crypto deposits to unlock commissions.',
  },
  {
    id: 'alert-4',
    title: 'HR Recruiter – "Instant offer" via personal email',
    company_or_pattern: 'Fake recruiter (Gmail/Yahoo, not corporate)',
    tag: 'FAKE RECRUITER',
    tag_color: 'bg-orange-500/10 text-orange-400 border-orange-500/30',
    location: 'Remote (US)',
    date: 'Jul 2025',
    description: 'Email claiming to represent Fortune 500 companies offering immediate employment without an interview. Asks candidate to fill out an onboarding form requesting SSN and banking routing.',
  },
  {
    id: 'alert-5',
    title: 'Operations Coordinator – Repackage & ship',
    company_or_pattern: 'Package mule / reshipping scheme',
    tag: 'RESHIPPING',
    tag_color: 'bg-red-500/10 text-red-400 border-red-500/30',
    location: 'Remote',
    date: 'Nov 2025',
    description: 'Posting on job aggregators for "Logistics Coordinator". The job involves receiving electronics purchased with stolen credit cards and reshipping them overseas.',
  },
  {
    id: 'alert-6',
    title: 'Boss imposter after new job announced',
    company_or_pattern: 'Social media-based impersonation',
    tag: 'IMPERSONATION',
    tag_color: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    location: 'Varies',
    date: '2025',
    description: 'After updating LinkedIn with a new role, scammers text pretending to be the company CEO or VP asking to purchase Apple/Google Play gift cards for a "client emergency".',
  },
  {
    id: 'alert-7',
    title: 'call operator',
    company_or_pattern: 'Azad digital media',
    tag: 'PAYMENT SCAM',
    tag_color: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
    community: true,
    location: 'Remote',
    date: 'Jun 2026',
    description: 'Candidate hired as phone support, given check to purchase proprietary VoIP softphone and headsets from specific vendor. The check bounces after transfer.',
  },
  {
    id: 'alert-8',
    title: 'Bespoke Technologies Inc scam',
    company_or_pattern: 'Bespoke Technologies Inc',
    tag: 'IMPERSONATION',
    tag_color: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    community: true,
    location: 'Varies',
    date: 'Mar 2026',
    description: 'Scammers cloning legitimate IT consultancy domain, conducting text interviews on Microsoft Teams, and issuing fake cashier checks for office setup.',
  },
];

export const LiveScamAlertsPage = () => {
  const navigate = useNavigate();
  const { success } = useToast();

  const [alerts, setAlerts] = useState(INITIAL_ALERTS);
  const [reportModalOpen, setReportModalOpen] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState(null);

  // Form states
  const [reportTitle, setReportTitle] = useState('');
  const [reportCompany, setReportCompany] = useState('');
  const [reportType, setReportType] = useState('TASK_SCAM');
  const [reportDetails, setReportDetails] = useState('');

  const handleReportSubmit = (e) => {
    e.preventDefault();
    const newAlert = {
      id: `alert-${Date.now()}`,
      title: reportTitle,
      company_or_pattern: reportCompany,
      tag: reportType.replace('_', ' '),
      tag_color: 'bg-red-500/10 text-red-400 border-red-500/30',
      community: true,
      location: 'Remote',
      date: 'Just now',
      description: reportDetails,
    };
    setAlerts([newAlert, ...alerts]);
    success('Scam report submitted to SentinelJob AI Intelligence Network.');
    setReportModalOpen(false);
    setReportTitle('');
    setReportCompany('');
    setReportDetails('');
  };

  return (
    <div className="min-h-screen bg-[#050a08] text-frost py-6 px-4 sm:px-6 lg:px-8 relative selection:bg-emerald-500 selection:text-white">
      
      {/* Background blueprint grid and ambient glow */}
      <div className="pointer-events-none absolute inset-0" aria-hidden="true">
        <div className="absolute inset-0 bg-blueprint opacity-50" />
        <div className="absolute inset-0 bg-spotlight" />
      </div>

      <div className="max-w-6xl mx-auto space-y-8 relative z-10">
        
        {/* Top Header matching Page 19 */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-white/10">
          <Link
            to="/"
            className="inline-flex items-center gap-1.5 text-xs font-medium text-fog hover:text-frost transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Home</span>
          </Link>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setReportModalOpen(true)}
              className="inline-flex items-center gap-1.5 rounded-full border border-red-500/30 bg-red-500/10 hover:bg-red-500/20 px-3.5 py-1.5 text-xs text-red-300 font-medium transition-all"
            >
              <AlertTriangle className="w-3.5 h-3.5 text-red-400" />
              <span>Report a scam</span>
            </button>
            <LanguageSelector />
          </div>
        </div>

        {/* Title & Subtitle matching Page 19 */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <h1 className="text-2xl sm:text-3xl font-semibold text-frost tracking-tight">
              Live Job Scam Alerts & Fraud Warnings
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-mist font-light">
            Verified reports of fake job postings, ghost jobs, and recruitment scams — updated in real time.
          </p>
        </div>

        {/* Filter / Status Bar */}
        <div className="flex items-center justify-between text-xs text-fog border-y border-white/10 py-3">
          <span className="font-mono">{alerts.length} alerts • System verified + community reports</span>
          <span className="text-[11px]">Updated every 15 minutes</span>
        </div>

        {/* Grid of Alert Cards matching Pages 19 & 20 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              onClick={() => setSelectedAlert(alert)}
              className="glass-card glass-card-hover rounded-2xl p-5 border border-white/10 flex flex-col justify-between cursor-pointer space-y-4 shadow-xl"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="p-1 rounded-md bg-red-500/10 text-red-400">
                    <AlertTriangle className="w-3.5 h-3.5" />
                  </div>
                  <div className="flex items-center gap-1.5">
                    {alert.community && (
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase bg-blue-500/15 text-blue-400 border border-blue-500/30">
                        Community
                      </span>
                    )}
                    <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase border ${alert.tag_color}`}>
                      {alert.tag}
                    </span>
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-semibold text-frost leading-snug">{alert.title}</h3>
                  <p className="text-xs text-mist font-light mt-0.5">{alert.company_or_pattern}</p>
                </div>
              </div>

              <div className="pt-3 border-t border-white/10 flex items-center justify-between text-[11px] text-fog font-mono">
                <span className="flex items-center gap-1">
                  <MapPin className="w-3 h-3 text-emerald-400" />
                  {alert.location}
                </span>
                <span className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  {alert.date}
                </span>
              </div>

              <div className="text-xs text-emerald-400 hover:text-emerald-300 font-medium pt-1">
                View details →
              </div>
            </div>
          ))}
        </div>

      </div>

      {/* Alert Detail Modal */}
      {selectedAlert && (
        <Modal
          isOpen={!!selectedAlert}
          onClose={() => setSelectedAlert(null)}
          title={selectedAlert.title}
        >
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-mono font-bold uppercase border ${selectedAlert.tag_color}`}>
                {selectedAlert.tag}
              </span>
              <span className="text-xs text-fog font-mono">• {selectedAlert.location}</span>
            </div>

            <div className="p-4 rounded-xl bg-black/50 border border-white/10 text-xs text-mist leading-relaxed space-y-2">
              <p className="font-semibold text-frost">Pattern Signature:</p>
              <p>{selectedAlert.description}</p>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => {
                  setSelectedAlert(null);
                  navigate('/analyze');
                }}
                className="px-4 py-2 rounded-full text-xs font-semibold text-white bg-emerald-500 hover:bg-emerald-400 transition-all"
              >
                Scan a Job Against This Pattern
              </button>
            </div>
          </div>
        </Modal>
      )}

      {/* Report a Scam Modal */}
      <Modal
        isOpen={reportModalOpen}
        onClose={() => setReportModalOpen(false)}
        title="Report a Job Scam to Sentinel Intelligence"
      >
        <form onSubmit={handleReportSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="block text-xs font-medium text-mist">Job Title / Role</label>
            <input
              type="text"
              required
              value={reportTitle}
              onChange={(e) => setReportTitle(e.target.value)}
              placeholder="e.g. Remote Data Entry Clerk"
              className="w-full px-3.5 py-2 text-xs rounded-xl bg-black/40 border border-white/10 text-frost placeholder-fog/60 focus:outline-none focus:border-emerald-500/50"
            />
          </div>

          <div className="space-y-1">
            <label className="block text-xs font-medium text-mist">Company Name / Impersonated Brand</label>
            <input
              type="text"
              required
              value={reportCompany}
              onChange={(e) => setReportCompany(e.target.value)}
              placeholder="e.g. StemPar Sciences / Target Logistics"
              className="w-full px-3.5 py-2 text-xs rounded-xl bg-black/40 border border-white/10 text-frost placeholder-fog/60 focus:outline-none focus:border-emerald-500/50"
            />
          </div>

          <div className="space-y-1">
            <label className="block text-xs font-medium text-mist">Scam Vector / Archetype</label>
            <select
              value={reportType}
              onChange={(e) => setReportType(e.target.value)}
              className="w-full px-3.5 py-2 text-xs rounded-xl bg-black/40 border border-white/10 text-frost focus:outline-none focus:border-emerald-500/50"
            >
              <option value="TASK_SCAM">Task Scam (App boosting / crypto deposits)</option>
              <option value="FAKE_CHECK">Fake Check / Overpayment</option>
              <option value="RESHIPPING">Reshipping / Package Mule</option>
              <option value="FAKE_RECRUITER">Fake Recruiter / Webmail impersonation</option>
              <option value="IDENTITY_HARVEST">Identity Harvesting</option>
            </select>
          </div>

          <div className="space-y-1">
            <label className="block text-xs font-medium text-mist">Scam Evidence / Contact Details</label>
            <textarea
              rows={3}
              required
              value={reportDetails}
              onChange={(e) => setReportDetails(e.target.value)}
              placeholder="Provide email address, phone number, Telegram handle, or description of what happened..."
              className="w-full px-3.5 py-2 text-xs rounded-xl bg-black/40 border border-white/10 text-frost placeholder-fog/60 focus:outline-none focus:border-emerald-500/50 resize-none font-sans"
            />
          </div>

          <button
            type="submit"
            className="w-full py-2.5 rounded-full text-xs font-semibold text-white bg-red-500 hover:bg-red-400 transition-all shadow-md"
          >
            Submit Scam Report
          </button>
        </form>
      </Modal>

    </div>
  );
};

export default LiveScamAlertsPage;
