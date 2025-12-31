import { lazy, Suspense } from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { PageSkeleton } from "@/components/LoadingSkeletons";

// Lazy load pages for code splitting
const Index = lazy(() => import("./pages/Index"));
const Calls = lazy(() => import("./pages/Calls"));
const Campaigns = lazy(() => import("./pages/Campaigns"));
const Appointments = lazy(() => import("./pages/Appointments"));
const Customers = lazy(() => import("./pages/Customers"));
const Scripts = lazy(() => import("./pages/Scripts"));
const QA = lazy(() => import("./pages/QA"));
const Settings = lazy(() => import("./pages/Settings"));
const NotFound = lazy(() => import("./pages/NotFound"));

// Production-ready QueryClient configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
});

// Suspense fallback for lazy-loaded pages
const PageLoader = () => (
  <div className="flex min-h-screen bg-background">
    <div className="w-64 shrink-0" /> {/* Sidebar placeholder */}
    <main className="flex-1 p-6">
      <PageSkeleton />
    </main>
  </div>
);

const App = () => (
  <ErrorBoundary>
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Suspense fallback={<PageLoader />}>
            <Routes>
              <Route path="/" element={<Index />} />
              <Route path="/calls" element={<Calls />} />
              <Route path="/campaigns" element={<Campaigns />} />
              <Route path="/appointments" element={<Appointments />} />
              <Route path="/customers" element={<Customers />} />
              <Route path="/scripts" element={<Scripts />} />
              <Route path="/qa" element={<QA />} />
              <Route path="/settings" element={<Settings />} />
              {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Suspense>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  </ErrorBoundary>
);

export default App;
