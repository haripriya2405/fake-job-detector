import React from 'react';

export const Card = ({
  children,
  className = '',
  hoverEffect = false,
  glass = true,
  glowColor = null, // 'primary' | 'ai' | 'danger'
  ...props
}) => {
  let glowClasses = '';
  if (glowColor === 'primary') glowClasses = 'hover:border-blue-500/50 hover:shadow-glow-primary';
  if (glowColor === 'ai') glowClasses = 'hover:border-purple-500/50 hover:shadow-glow-ai';
  if (glowColor === 'danger') glowClasses = 'hover:border-red-500/50 hover:shadow-glow-danger';

  return (
    <div
      className={`rounded-2xl transition-all duration-200 ${
        glass ? 'glass-card' : 'bg-slate-900 border border-slate-800'
      } ${hoverEffect ? 'glass-card-hover cursor-pointer' : ''} ${glowClasses} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader = ({ children, className = '', title, subtitle, action }) => (
  <div className={`p-6 border-b border-slate-800/80 flex items-center justify-between ${className}`}>
    <div>
      {title && <h3 className="text-lg font-semibold text-white tracking-tight">{title}</h3>}
      {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
      {children}
    </div>
    {action && <div className="shrink-0 ml-4">{action}</div>}
  </div>
);

export const CardBody = ({ children, className = '' }) => (
  <div className={`p-6 ${className}`}>{children}</div>
);

export const CardFooter = ({ children, className = '' }) => (
  <div className={`p-6 pt-0 border-t border-slate-800/60 mt-4 flex items-center justify-between ${className}`}>
    {children}
  </div>
);

export default Card;
