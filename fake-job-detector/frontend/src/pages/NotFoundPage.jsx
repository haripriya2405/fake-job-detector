import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, ArrowLeft, Home } from 'lucide-react';
import { Button } from '../components/ui/Button';

export const NotFoundPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-[calc(100vh-14rem)] flex flex-col items-center justify-center text-center p-6 space-y-5">
      <div className="w-16 h-16 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center text-red-400 shadow-glow-danger">
        <ShieldAlert className="w-8 h-8" />
      </div>

      <div className="space-y-2">
        <h1 className="text-3xl font-extrabold text-white tracking-tight font-mono">404: RESOURCE_NOT_FOUND</h1>
        <p className="text-xs sm:text-sm text-slate-400 max-w-md mx-auto">
          The requested intelligence endpoint or report path does not exist in the security vault.
        </p>
      </div>

      <div className="flex items-center gap-3 pt-2">
        <Button variant="outline" size="sm" icon={ArrowLeft} onClick={() => navigate(-1)}>
          Go Back
        </Button>
        <Button variant="primary" size="sm" icon={Home} onClick={() => navigate('/')}>
          Return Home
        </Button>
      </div>
    </div>
  );
};

export default NotFoundPage;
