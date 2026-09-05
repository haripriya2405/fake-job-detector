import React from 'react';
import { useNavigate } from 'react-router-dom';
import { RiskBadge } from '../ui/RiskBadge';
import { formatRelativeTime } from '../../utils/formatters';
import { FileText, Image as ImageIcon, ExternalLink, Building, ArrowRight } from 'lucide-react';

export const RecentScansTable = ({ analyses = [], onSelect }) => {
  const navigate = useNavigate();

  const handleRowClick = (item) => {
    if (onSelect) {
      onSelect(item);
    } else {
      navigate(`/analysis/${item.id}`);
    }
  };

  if (!analyses || analyses.length === 0) {
    return (
      <div className="p-8 text-center text-xs text-slate-500">
        No job scans recorded yet. Initiate your first scan from the analyzer.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-xs">
        <thead className="border-b border-slate-800 text-slate-400 font-mono uppercase text-[10px] tracking-wider">
          <tr>
            <th className="pb-3 px-4 font-semibold">Job Title & Entity</th>
            <th className="pb-3 px-4 font-semibold">Source</th>
            <th className="pb-3 px-4 font-semibold">Risk Classification</th>
            <th className="pb-3 px-4 font-semibold">Scanned</th>
            <th className="pb-3 px-4 font-semibold text-right">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/60">
          {analyses.map((item) => (
            <tr
              key={item.id}
              onClick={() => handleRowClick(item)}
              className="hover:bg-slate-800/40 transition-colors cursor-pointer group"
            >
              {/* Job Title & Company */}
              <td className="py-3.5 px-4">
                <div className="flex flex-col">
                  <span className="font-semibold text-white group-hover:text-blue-400 transition-colors line-clamp-1">
                    {item.job_title || 'Unnamed Job Posting'}
                  </span>
                  <span className="text-slate-400 text-[11px] flex items-center gap-1 mt-0.5">
                    <Building className="w-3 h-3 text-slate-400" />
                    {item.company_name || 'Unspecified Employer'}
                  </span>
                </div>
              </td>

              {/* Source Type */}
              <td className="py-3.5 px-4">
                <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-slate-800 border border-slate-700 text-[11px] font-mono text-slate-300">
                  {item.source_type === 'pdf' ? (
                    <FileText className="w-3 h-3 text-red-400" />
                  ) : item.source_type === 'image' ? (
                    <ImageIcon className="w-3 h-3 text-purple-400" />
                  ) : (
                    <span className="w-2 h-2 rounded-full bg-blue-400" />
                  )}
                  <span className="uppercase">{item.source_type || 'TEXT'}</span>
                </span>
              </td>

              {/* Risk Badge */}
              <td className="py-3.5 px-4">
                <RiskBadge score={item.risk_score} level={item.risk_level} size="sm" />
              </td>

              {/* Time */}
              <td className="py-3.5 px-4 text-slate-400 font-mono text-[11px]">
                {formatRelativeTime(item.created_at)}
              </td>

              {/* Action Link */}
              <td className="py-3.5 px-4 text-right">
                <button className="p-1.5 rounded-lg text-slate-400 group-hover:text-blue-400 group-hover:bg-blue-500/10 transition-colors">
                  <ArrowRight className="w-4 h-4" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default RecentScansTable;
