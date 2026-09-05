import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import Footer from './Footer';

export const AppLayout = ({ showSidebar = false }) => {
  return (
    <div className="min-h-screen flex flex-col bg-[#050a08] text-frost selection:bg-emerald-500 selection:text-white">
      <Navbar />
      <div className="flex-1 flex w-full">
        {showSidebar && <Sidebar />}
        <main className="flex-1 min-w-0 px-3 sm:px-6 lg:px-10 py-6 overflow-y-auto">
          <div className="max-w-[1400px] mx-auto space-y-6">
            <Outlet />
          </div>
        </main>
      </div>
      <Footer />
    </div>
  );
};

export default AppLayout;
