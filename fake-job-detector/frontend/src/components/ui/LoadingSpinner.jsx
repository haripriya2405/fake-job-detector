import React from 'react';
import { ShieldCheck, Cpu } from 'lucide-react';
import { motion } from 'framer-motion';

export const LoadingSpinner = ({ text = 'Analyzing posting signatures...', size = 'md' }) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 space-y-5">
      <div className="relative flex items-center justify-center">
        {/* Outer glowing orbital ring */}
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 3, ease: 'linear' }}
          className="w-20 h-20 rounded-full border-2 border-blue-500/20 border-t-blue-500 border-r-purple-500"
        />
        {/* Inner pulse */}
        <motion.div
          animate={{ scale: [0.85, 1.15, 0.85], opacity: [0.5, 1, 0.5] }}
          transition={{ repeat: Infinity, duration: 2, ease: 'easeInOut' }}
          className="absolute w-12 h-12 rounded-full bg-blue-500/10 border border-blue-400/30 flex items-center justify-center text-blue-400 shadow-glow-primary"
        >
          <Cpu className="w-6 h-6 animate-pulse text-purple-400" />
        </motion.div>
      </div>

      <div className="text-center space-y-1">
        <p className="text-sm font-semibold text-slate-200">{text}</p>
        <p className="text-xs text-slate-500">Cross-referencing ML models, NLP rules, and WHOIS records...</p>
      </div>
    </div>
  );
};

export default LoadingSpinner;
