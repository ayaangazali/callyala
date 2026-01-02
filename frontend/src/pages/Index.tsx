import { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useTranslation } from "react-i18next";
import { Phone, PhoneIncoming, CalendarCheck, RefreshCw, UserCheck, Clock } from "lucide-react";
import { Sidebar } from "@/components/Sidebar";
import { DashboardHeader } from "@/components/DashboardHeader";
import { VoiceStatsCard } from "@/components/VoiceStatsCard";
import { OutcomesChart } from "@/components/OutcomesChart";
import { CallsOverTimeChart } from "@/components/CallsOverTimeChart";
import { NeedsAttention } from "@/components/NeedsAttention";
import { QuickActions } from "@/components/QuickActions";
import { CallLogTable } from "@/components/CallLogTable";
import { CommandPalette } from "@/components/CommandPalette";
import { LiveCallingBar } from "@/components/LiveCallingBar";
import { PageSkeleton } from "@/components/LoadingSkeletons";
import { staggerContainer, blurIn } from "@/lib/motion";
import { useOverviewStats, useAppointmentStats, useCalls } from "@/hooks/use-api";
import { useLocalizedNumbers } from "@/hooks/use-localized-numbers";

const Index = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [isCallingActive, setIsCallingActive] = useState(false);
  
  const { t } = useTranslation();
  const { formatNumber, formatPercentage, localizeString } = useLocalizedNumbers();

  // Fetch real data from API
  const { data: overviewData, isLoading: overviewLoading } = useOverviewStats();
  const { data: appointmentStats } = useAppointmentStats();
  const { data: callsData } = useCalls({ limit: 50 });

  // Build stats from real data with fallback to mock
  const stats = useMemo(() => {
    const totalCalls = overviewData?.totalCalls ?? 127;
    const successRate = overviewData?.successRate ?? 68;
    const appointmentsBooked = overviewData?.appointmentsBooked ?? appointmentStats?.completed ?? 23;
    const avgDuration = overviewData?.avgCallDuration ?? "1:24";
    
    return [
      { 
        title: t('dashboard.totalCalls'), 
        value: formatNumber(totalCalls), 
        change: localizeString("+18%"), 
        changeLabel: t('stats.vs') + " " + t('stats.today'), 
        icon: Phone, 
        positive: true, 
        trend: "up" as const 
      },
      { 
        title: t('dashboard.successRate'), 
        value: formatPercentage(successRate) + "%", 
        change: localizeString("+5%"), 
        changeLabel: t('stats.vs') + " avg", 
        icon: PhoneIncoming, 
        positive: true, 
        trend: "up" as const 
      },
      { 
        title: t('appointments.upcoming'), 
        value: formatNumber(appointmentsBooked), 
        change: localizeString("+12%"), 
        changeLabel: t('stats.vs') + " " + t('stats.today'), 
        icon: CalendarCheck, 
        positive: true, 
        trend: "up" as const 
      },
      { 
        title: t('appointments.cancelled'), 
        value: formatNumber(appointmentStats?.cancelled ?? 7), 
        change: localizeString("-3"), 
        changeLabel: t('stats.vs') + " " + t('stats.today'), 
        icon: RefreshCw, 
        positive: true, 
        trend: "down" as const 
      },
      { 
        title: t('dashboard.needsAttention'), 
        value: formatNumber(appointmentStats?.scheduled ?? 5), 
        change: localizeString("+2"), 
        changeLabel: t('common.pending'), 
        icon: UserCheck, 
        positive: false, 
        trend: "up" as const 
      },
      { 
        title: t('dashboard.avgDuration'), 
        value: localizeString(avgDuration), 
        change: localizeString("-8s"), 
        changeLabel: t('stats.vs') + " avg", 
        icon: Clock, 
        positive: true, 
        trend: "down" as const 
      },
    ];
  }, [overviewData, appointmentStats, t, formatNumber, formatPercentage, localizeString]);

  // Show loading state
  if (overviewLoading) {
    return (
      <div className="flex min-h-screen bg-background">
        <Sidebar collapsed={sidebarCollapsed} onCollapse={setSidebarCollapsed} />
        <main className="flex-1 p-6 overflow-auto">
          <PageSkeleton />
        </main>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar collapsed={sidebarCollapsed} onCollapse={setSidebarCollapsed} />
      
      <motion.main 
        className="flex-1 p-4 sm:p-6 lg:p-8 overflow-auto relative"
        variants={blurIn}
        initial="hidden"
        animate="visible"
      >
        <DashboardHeader 
          onOpenCommandPalette={() => setCommandPaletteOpen(true)}
          isCallingActive={isCallingActive}
          onToggleCalling={() => setIsCallingActive(!isCallingActive)}
        />
        
        {/* Stats Row - Responsive grid */}
        <motion.div 
          className="grid grid-cols-1 xs:grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-3 sm:gap-4 mb-6"
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
        >
          {stats.map((stat, index) => (
            <VoiceStatsCard key={stat.title} {...stat} index={index} />
          ))}
        </motion.div>
        
        {/* Charts Row - Responsive grid */}
        <motion.div 
          className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-6 mb-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <div className="lg:col-span-2">
            <CallsOverTimeChart />
          </div>
          <OutcomesChart />
        </motion.div>

        {/* Main Content Grid - Responsive */}
        <motion.div 
          className="grid grid-cols-1 xl:grid-cols-3 gap-4 sm:gap-6 mb-20"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <div className="xl:col-span-2">
            <CallLogTable />
          </div>
          <div className="space-y-4 sm:space-y-6">
            <NeedsAttention />
            <QuickActions />
          </div>
        </motion.div>

        {/* Live Calling Bar */}
        <AnimatePresence>
          {isCallingActive && (
            <LiveCallingBar 
              onStop={() => setIsCallingActive(false)}
            />
          )}
        </AnimatePresence>
      </motion.main>

      {/* Command Palette */}
      <CommandPalette 
        open={commandPaletteOpen} 
        onOpenChange={setCommandPaletteOpen} 
      />
    </div>
  );
};

export default Index;
