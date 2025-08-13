import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Analytics } from '@vercel/analytics/react';
import Index from "./pages/Index";

const App = () => (
  <TooltipProvider>
    <Toaster />
    <Sonner />
    <Index />
    <Analytics />
  </TooltipProvider>
);

export default App;
