import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="p-3 rounded-xl bg-slate-900 border border-slate-700 shadow-xl text-xs font-mono">
        <p className="font-bold text-white mb-1.5">{label} Activity</p>
        <p className="text-blue-400">Total Scanned: <span className="text-white">{payload[0]?.value}</span></p>
        <p className="text-red-400">Threats Flagged: <span className="text-white">{payload[1]?.value}</span></p>
      </div>
    );
  }
  return null;
};

export const ThreatTrendChart = ({ data = [] }) => {
  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="scansGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.0} />
            </linearGradient>
            <linearGradient id="threatsGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#EF4444" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#EF4444" stopOpacity={0.0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
          <XAxis dataKey="month" stroke="#64748B" fontSize={11} tickLine={false} />
          <YAxis stroke="#64748B" fontSize={11} tickLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="scans"
            stroke="#3B82F6"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#scansGrad)"
          />
          <Area
            type="monotone"
            dataKey="threats"
            stroke="#EF4444"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#threatsGrad)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ThreatTrendChart;
