import React, { useState } from 'react';
import {
  Settings,
  User,
  Key,
  Shield,
  Bell,
  Trash2,
  Save,
  Check,
  Sparkles,
  Sliders,
  Database,
} from 'lucide-react';
import { Card, CardHeader, CardBody } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { useAuth } from '../hooks/useAuth';
import { useToast } from '../hooks/useToast';

export const SettingsPage = () => {
  const { user } = useAuth();
  const { success } = useToast();

  const [sensitivity, setSensitivity] = useState('standard');
  const [apiKey, setApiKey] = useState('sentinel_live_sk_948f1029ba30dce4');
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [highRiskWebhook, setHighRiskWebhook] = useState('https://hooks.slack.com/services/T00/B00/XXXX');
  const [isCopied, setIsCopied] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    success('Configuration and security parameters saved.');
  };

  const handleClearCache = () => {
    localStorage.removeItem('sentinel_scan_history');
    success('Local scan cache cleared.');
  };

  const copyApiKey = () => {
    navigator.clipboard.writeText(apiKey);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
    success('API Key copied to clipboard');
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <Settings className="w-6 h-6 text-purple-400" />
          <span>Security Engine & Account Settings</span>
        </h1>
        <p className="text-xs text-slate-400">
          Manage AI detection sensitivity, API access tokens, and integration preferences.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        
        {/* Profile Card */}
        <Card>
          <CardHeader
            title="Analyst Profile"
            subtitle="Current session identity and privileges"
          />
          <CardBody className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Full Name"
                disabled
                value={user?.full_name || 'Not signed in'}
              />
              <Input
                label="Email"
                disabled
                value={user?.email || 'Not signed in'}
              />
            </div>
            <div className="flex items-center gap-2 pt-1 text-xs text-slate-400">
              <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-mono font-semibold">
                ROLE: {user?.role || 'User'}
              </span>
              <span>•</span>
              <span className="text-slate-400">Active Session</span>
            </div>
          </CardBody>
        </Card>

        {/* AI Scoring Calibration & Sensitivity */}
        <Card>
          <CardHeader
            title="AI Sensitivity & Heuristic Weighting"
            subtitle="Configure false-positive tolerance and flag thresholds"
          />
          <CardBody className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {[
                {
                  id: 'relaxed',
                  title: 'Relaxed (Strict Flags)',
                  desc: 'Triggers flags only on explicit check fraud and confirmed scam keywords.',
                },
                {
                  id: 'standard',
                  title: 'Balanced (Standard)',
                  desc: 'Default configuration. Flags suspicious pay, off-platform chat, and unverified domains.',
                },
                {
                  id: 'aggressive',
                  title: 'Strict (High Vigilance)',
                  desc: 'Elevates warnings for any lookalike domains or missing recruiter LinkedIn matches.',
                },
              ].map((tier) => (
                <div
                  key={tier.id}
                  onClick={() => setSensitivity(tier.id)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    sensitivity === tier.id
                      ? 'border-blue-500 bg-blue-500/10 shadow-glow-primary'
                      : 'border-slate-800 bg-slate-900/50 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-white">{tier.title}</span>
                    {sensitivity === tier.id && <Check className="w-4 h-4 text-blue-400" />}
                  </div>
                  <p className="text-[11px] text-slate-400 leading-normal">{tier.desc}</p>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>

        {/* API Integration Token */}
        <Card>
          <CardHeader
            title="Programmatic REST API Key"
            subtitle="Use this secret token for CI/CD or internal recruiting ATS integrations"
          />
          <CardBody className="space-y-4">
            <div className="flex items-center gap-2">
              <input
                type="password"
                readOnly
                value={apiKey}
                className="flex-1 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-slate-300 px-4 py-2.5"
              />
              <Button type="button" variant="outline" size="sm" onClick={copyApiKey}>
                {isCopied ? 'Copied' : 'Copy'}
              </Button>
            </div>
            <p className="text-[11px] text-slate-500">
              API requests are authenticated via <code className="text-slate-300">Authorization: Bearer sentinel_live_sk_...</code>
            </p>
          </CardBody>
        </Card>

        {/* Cache / Danger Zone */}
        <Card className="border-red-500/20">
          <CardHeader
            title="Data Privacy & Local Vault Cache"
            subtitle="Manage locally stored assessment histories"
          />
          <CardBody className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="text-xs text-slate-400 max-w-md">
              Clear your locally cached scan results from browser storage.
            </div>
            <Button
              type="button"
              variant="danger"
              size="sm"
              icon={Trash2}
              onClick={handleClearCache}
            >
              Clear Local Scan History
            </Button>
          </CardBody>
        </Card>

        {/* Save Button */}
        <div className="flex justify-end">
          <Button type="submit" variant="primary" size="md" icon={Save}>
            Save Preferences
          </Button>
        </div>
      </form>

    </div>
  );
};

export default SettingsPage;
