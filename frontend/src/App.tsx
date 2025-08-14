import { useState } from 'react';
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import Index from "./pages/Index";
import { AdminDashboard } from "./pages/AdminDashboard";

type Page = 'home' | 'admin';

const App = () => {
  const [currentPage, setCurrentPage] = useState<Page>('home');

  const renderPage = () => {
    switch (currentPage) {
      case 'admin':
        return <AdminDashboard onNavigateBack={() => setCurrentPage('home')} />;
      case 'home':
      default:
        return <Index onNavigateToAdmin={() => setCurrentPage('admin')} />;
    }
  };

  return (
    <TooltipProvider>
      <Toaster />
      <Sonner />
      {renderPage()}
    </TooltipProvider>
  );
};

export default App;
