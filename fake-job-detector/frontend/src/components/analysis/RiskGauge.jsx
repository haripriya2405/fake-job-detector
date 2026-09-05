import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getRiskLevelMeta } from '../../utils/riskHelpers';
import { ShieldAlert, ShieldCheck, AlertTriangle, Flame } from 'lucide-react';

export const RiskGauge = ({ score = 0, riskLevel: explicitLevel, size = 220 }) => {
  const [animatedScore, setAnimatedScore] = useState(0);
  const meta = getRiskLevelMeta(score);

  useEffect(() => {
    let start = 0;
    const end = Math.min(Math.max(score, 0), 100);
    if (end === 0) return;
    const duration = 1200; // ms
    const stepTime = 20;
    const increment = end / (duration / stepTime);

    const timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        setAnimatedScore(end);
        clearInterval(timer);
      } else {
        setAnimatedScore(Math.floor(start));
      }
    }, stepTime);

    return () => clearInterval(timer);
  }, [score]);

  // SVG Gauge calculations
  const strokeWidth = 14;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  // Use 240 degree arc instead of full circle for an authentic speedometer feel
  const arcPercentage = 0.75;
  const arcLength = circumference * arcPercentage;
  const offset = arcLength - (animatedScore / 100) * arcLength;

  return (
    <div className="flex flex-col items-center justify-center p-6 relative">
      <div className="relative" style={{ width: size, height: size }}>
        
        {/* Glow backdrop based on risk tier */}
        <div
          className="absolute inset-0 rounded-full blur-2xl opacity-20 pointer-events-none transition-all duration-700"
          style={{ backgroundColor: meta.color }}
        />

        <svg
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
          className="rotate-[135deg] transform origin-center"
        >
          {/* Background Track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#1E293B"
            strokeWidth={strokeWidth}
            strokeDasharray={`${arcLength} ${circumference}`}
            strokeLinecap="round"
            fill="transparent"
          />

          {/* Animated Value Arc */}
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={meta.color}
            strokeWidth={strokeWidth}
            strokeDasharray={`${arcLength} ${circumference}`}
            strokeDashoffset={offset}
            strokeLinecap="round"
            fill="transparent"
            transition={{ duration: 1, ease: 'easeOut' }}
          />
        </svg>

        {/* Center Content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-4">
          <div className="text-4xl font-extrabold tracking-tight font-mono text-white flex items-baseline">
            <span>{animatedScore}</span>
            <span className="text-sm font-normal text-slate-400 ml-0.5">/100</span>
          </div>

          <div
            className="mt-1 px-3 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider border flex items-center gap-1.5 shadow-sm"
            style={{
              color: meta.color,
              backgroundColor: meta.bgColor,
              borderColor: meta.borderColor,
            }}
          >
            {meta.key === 'critical' && <Flame className="w-3.5 h-3.5" />}
            {meta.key === 'high' && <ShieldAlert className="w-3.5 h-3.5" />}
            {meta.key === 'medium' && <AlertTriangle className="w-3.5 h-3.5" />}
            {meta.key === 'low' && <ShieldCheck className="w-3.5 h-3.5" />}
            <span>{meta.label}</span>
          </div>
        </div>
      </div>

      {/* Scale Legend */}
      <div className="mt-4 flex items-center justify-center gap-4 text-[11px] font-mono text-slate-400">
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
          0-29 Low
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-amber-500" />
          30-59 Med
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-orange-500" />
          60-79 High
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-red-500" />
          80-100 Critical
        </span>
      </div>
    </div>
  );
};

export default RiskGauge;
