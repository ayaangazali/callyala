import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
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
import { staggerContainer, staggerItem, blurIn } from "@/lib/motion";

const stats = [
  { title: "Calls Placed", value: "127", change: "+18%", changeLabel: "vs yesterday", icon: Phone, positive: true, trend: "up" as const },
  { title: "Answer Rate", value: "68%", change: "+5%", changeLabel: "vs avg", icon: PhoneIncoming, positive: true, trend: "up" as const },
  { title: "Booked Pickups", value: "23", change: "+12%", changeLabel: "vs yesterday", icon: CalendarCheck, positive: true, trend: "up" as const },
  { title: "Reschedules", value: "7", change: "-3", changeLabel: "vs yesterday", icon: RefreshCw, positive: true, trend: "down" as const },
  { title: "Human Follow-ups", value: "5", change: "+2", changeLabel: "pending", icon: UserCheck, positive: false, trend: "up" as const },
  { title: "Avg Duration", value: "1:24", change: "-8s", changeLabel: "vs avg", icon: Clock, positive: true, trend: "down" as const },
];

const Index = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [isCallingActive, setIsCallingActive] = useState(false);

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar collapsed={sidebarCollapsed} onCollapse={setSidebarCollapsed} />
      
      <motion.main 
        className="flex-1 p-6 overflow-auto relative"
        variants={blurIn}
        initial="hidden"
        animate="visible"
      >
        <DashboardHeader 
          onOpenCommandPalette={() => setCommandPaletteOpen(true)}
          isCallingActive={isCallingActive}
          onToggleCalling={() => setIsCallingActive(!isCallingActive)}
        />
        
        {/* Stats Row */}
        <motion.div 
          className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6"
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
        >
          {stats.map((stat, index) => (
            <VoiceStatsCard key={stat.title} {...stat} index={index} />
          ))}
        </motion.div>
        
        {/* Charts Row */}
        <motion.div 
          className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <div className="lg:col-span-2">
            <CallsOverTimeChart />
          </div>
          <OutcomesChart />
        </motion.div>

        {/* Main Content Grid */}
        <motion.div 
          className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-20"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <div className="lg:col-span-2">
            <CallLogTable />
          </div>
          <div className="space-y-4">
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
