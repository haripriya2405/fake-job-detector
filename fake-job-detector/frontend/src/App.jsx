import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import { LanguageProvider } from './context/LanguageContext';
import AppLayout from './components/layout/AppLayout';
import { LoadingSpinner } from './components/ui/LoadingSpinner';

// Route-level Lazy Loaded Pages
const LandingPage = lazy(() => import('./pages/LandingPage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));
const RedFlagsGuidePage = lazy(() => import('./pages/RedFlagsGuidePage'));
const LiveScamAlertsPage = lazy(() => import('./pages/LiveScamAlertsPage'));
const CommunityScamDatabasePage = lazy(() => import('./pages/CommunityScamDatabasePage'));
const JobVerificationCertificatePage = lazy(() => import('./pages/JobVerificationCertificatePage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const AnalyzeJobPage = lazy(() => import('./pages/AnalyzeJobPage'));
const AnalysisResultPage = lazy(() => import('./pages/AnalysisResultPage'));
const AnalysisHistoryPage = lazy(() => import('./pages/AnalysisHistoryPage'));
const AnalysisDetailPage = lazy(() => import('./pages/AnalysisDetailPage'));
const ReportScamPage = lazy(() => import('./pages/ReportScamPage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'));

const PageFallback = () => (
  <div className="flex items-center justify-center min-h-[50vh] p-8">
    <LoadingSpinner text="Loading secure interface..." size="lg" />
  </div>
);

export function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <LanguageProvider>
          <BrowserRouter>
            <Suspense fallback={<PageFallback />}>
              <Routes>
                {/* Public Layout Routes */}
                <Route element={<AppLayout showSidebar={false} />}>
                  <Route path="/" element={<LandingPage />} />
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/register" element={<RegisterPage />} />
                  <Route path="/database" element={<CommunityScamDatabasePage />} />
                  <Route path="/scams" element={<CommunityScamDatabasePage />} />
                  <Route path="/verify/:id" element={<JobVerificationCertificatePage />} />
                  <Route path="/certificate/:id" element={<JobVerificationCertificatePage />} />
                  <Route path="/guides/job-scam-red-flags" element={<RedFlagsGuidePage />} />
                  <Route path="/simulator" element={<RedFlagsGuidePage />} />
                  <Route path="/game" element={<RedFlagsGuidePage />} />
                  <Route path="/alerts" element={<LiveScamAlertsPage />} />
                  <Route path="/live-alerts" element={<LiveScamAlertsPage />} />
                </Route>

                {/* Workspace Layout Routes with Sidebar */}
                <Route element={<AppLayout showSidebar={true} />}>
                  <Route path="/scan" element={<AnalyzeJobPage />} />
                  <Route path="/analyze" element={<AnalyzeJobPage />} />
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/history" element={<AnalysisHistoryPage />} />
                  <Route path="/report-scam" element={<ReportScamPage />} />
                  <Route path="/analysis/:id" element={<AnalysisResultPage />} />
                  <Route path="/analysis/detail/:id" element={<AnalysisDetailPage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                </Route>

                {/* Catch-all route */}
                <Route element={<AppLayout showSidebar={false} />}>
                  <Route path="*" element={<NotFoundPage />} />
                </Route>
              </Routes>
            </Suspense>
          </BrowserRouter>
        </LanguageProvider>
      </ToastProvider>
    </AuthProvider>
  );
}

export default App;
