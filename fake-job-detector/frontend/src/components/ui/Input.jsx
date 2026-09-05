import React from 'react';

export const Input = ({
  label,
  error,
  icon: Icon,
  className = '',
  id,
  ...props
}) => {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

  return (
    <div className="w-full">
      {label && (
        <label htmlFor={inputId} className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
          {label}
        </label>
      )}
      <div className="relative">
        {Icon && (
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
            <Icon className="w-4 h-4" />
          </div>
        )}
        <input
          id={inputId}
          className={`w-full rounded-xl bg-slate-900/90 border ${
            error ? 'border-red-500/60 focus:border-red-500' : 'border-slate-800 focus:border-blue-500'
          } text-slate-100 placeholder-slate-500 text-sm px-4 py-2.5 transition-colors focus:outline-none focus:ring-1 focus:ring-blue-500/50 ${
            Icon ? 'pl-10' : ''
          } ${className}`}
          {...props}
        />
      </div>
      {error && <p className="mt-1.5 text-xs text-red-400">{error}</p>}
    </div>
  );
};

export const Textarea = ({
  label,
  error,
  rows = 5,
  className = '',
  id,
  ...props
}) => {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

  return (
    <div className="w-full">
      {label && (
        <label htmlFor={inputId} className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
          {label}
        </label>
      )}
      <textarea
        id={inputId}
        rows={rows}
        className={`w-full rounded-xl bg-slate-900/90 border ${
          error ? 'border-red-500/60 focus:border-red-500' : 'border-slate-800 focus:border-blue-500'
        } text-slate-100 placeholder-slate-500 text-sm p-4 transition-colors focus:outline-none focus:ring-1 focus:ring-blue-500/50 resize-y ${className}`}
        {...props}
      />
      {error && <p className="mt-1.5 text-xs text-red-400">{error}</p>}
    </div>
  );
};

export default Input;
