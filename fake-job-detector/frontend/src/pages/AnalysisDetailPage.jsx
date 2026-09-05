import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ShieldAlert,
  ShieldCheck,
  Building,
  Calendar,
  ArrowLeft,
  Code,
  FileText,
  Copy,
  ExternalLink,
} from 'lucide-react';
import { Card, CardHeader, CardBody } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { RiskBadge } from '../components/ui/RiskBadge';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { analysisService } from '../services/analysisService';
import { formatDate } from '../utils/formatters';
import { useToast } from '../hooks/useToast';

export const AnalysisDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { success } = useToast();

  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const data = await analysisService.getAnalysisById(id);
        setReport(data);
      } catch (err) {
        console.error('Failed to load analysis detail', err);
      } finally {
        setLoading(false);
      }
    };
    fetchReport();
  }, [id]);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto py-12">
        <LoadingSpinner text="Retrieving forensic logs..." />
      </div>
    );
  }

  if (!report) {
    return (
      <div className="max-w-xl mx-auto py-16 text-center space-y-4">
        <h2 className="text-xl font-bold text-white">Record Not Found</h2>
        <Button variant="primary" onClick={() => navigate('/history')}>
          Back to Vault
        </Button>
      </div>
    );
  }

  const handleCopyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(report, null, 2));
    success('Raw forensic JSON payload copied to clipboard.');
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      
      {/* Back button & Action */}
      <div className="flex items-center justify-between">
        <Button
          variant="ghost"
          size="sm"
          icon={ArrowLeft}
          onClick={() => navigate(`/analysis/${report.id}`)}
        >
          Back to Result Overview
        </Button>

        <Button
          variant="outline"
          size="sm"
          icon={Copy}
          onClick={handleCopyJson}
        >
          Copy JSON Payload
        </Button>
      </div>

      {/* Header */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-2">
        <div className="flex items-center justify-between">
          <RiskBadge score={report.risk_score} level={report.risk_level} size="md" />
          <span className="font-mono text-xs text-slate-400">ID: {report.id}</span>
        </div>
        <h1 className="text-xl font-bold text-white">{report.job_title}</h1>
        <p className="text-xs text-slate-400">Entity: {report.company_name} • Scanned {formatDate(report.created_at)}</p>
      </div>

      {/* Raw Content Section */}
      <Card>
        <CardHeader
          title="Extracted Raw Ingestion Buffer"
          subtitle="Unmodified text parsed from source input"
        />
        <CardBody>
          <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 text-xs font-mono text-slate-300 whitespace-pre-wrap leading-relaxed max-h-96 overflow-y-auto">
            {report.raw_content}
          </pre>
        </CardBody>
      </Card>

      {/* Machine Readable JSON Audit */}
      <Card>
        <CardHeader
          title="Machine-Readable Forensic JSON Payload"
          subtitle="Full telemetry object for downstream SIEM / incident response integration"
        />
        <CardBody>
          <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 text-xs font-mono text-purple-300 whitespace-pre-wrap leading-relaxed max-h-96 overflow-y-auto">
            {JSON.stringify(report, null, 2)}
          </pre>
        </CardBody>
      </Card>

    </div>
  );
};

export default AnalysisDetailPage;
