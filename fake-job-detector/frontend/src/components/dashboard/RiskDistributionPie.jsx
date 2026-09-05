import React from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';

export const RiskDistributionPie = ({ data = [] }) => {
  return (
    <div className="w-full flex flex-col items-center">
      <div className="w-full h-48">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Tooltip
              contentStyle={{
                backgroundColor: '#0F172A',
                borderColor: '#334155',
                borderRadius: '12px',
                fontSize: '12px',
                color: '#fff',
              }}
            />
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={50}
              outerRadius={75}
              paddingAngle={5}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} stroke="#070B14" strokeWidth={2} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-2 gap-2 w-full mt-2">
        {data.map((item, idx) => (
          <div key={idx} className="flex items-center justify-between text-xs p-1.5 rounded-lg bg-slate-900/60 border border-slate-800">
            <span className="flex items-center gap-1.5 text-slate-300">
              <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }} />
              <span className="truncate max-w-[90px]">{item.name.split(' ')[0]}</span>
            </span>
            <span className="font-mono font-bold text-white">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RiskDistributionPie;
