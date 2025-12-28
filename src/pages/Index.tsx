import { Phone, PhoneIncoming, CalendarCheck, RefreshCw, UserCheck, Clock } from "lucide-react";
import { Sidebar } from "@/components/Sidebar";
import { DashboardHeader } from "@/components/DashboardHeader";
import { VoiceStatsCard } from "@/components/VoiceStatsCard";
import { OutcomesChart } from "@/components/OutcomesChart";
import { CallsOverTimeChart } from "@/components/CallsOverTimeChart";
import { NeedsAttention } from "@/components/NeedsAttention";
import { QuickActions } from "@/components/QuickActions";
import { CallLogTable } from "@/components/CallLogTable";

const stats = [
  { 
    title: "Calls Placed", 
    value: "127", 
    change: "+18%", 
    changeLabel: "vs yesterday", 
    icon: Phone,
    positive: true,
    trend: "up" as const,
  },
  { 
    title: "Answer Rate", 
    value: "68%", 
    change: "+5%", 
    changeLabel: "vs avg", 
    icon: PhoneIncoming,
    positive: true,
    trend: "up" as const,
  },
  { 
    title: "Booked Pickups", 
    value: "23", 
    change: "+12%", 
    changeLabel: "vs yesterday", 
    icon: CalendarCheck,
    positive: true,
    trend: "up" as const,
  },
  { 
    title: "Reschedules", 
    value: "7", 
    change: "-3", 
    changeLabel: "vs yesterday", 
    icon: RefreshCw,
    positive: true,
    trend: "down" as const,
  },
  { 
    title: "Human Follow-ups", 
    value: "5", 
    change: "+2", 
    changeLabel: "pending", 
    icon: UserCheck,
    positive: false,
    trend: "up" as const,
  },
  { 
    title: "Avg Duration", 
    value: "1:24", 
    change: "-8s", 
    changeLabel: "vs avg", 
    icon: Clock,
    positive: true,
    trend: "down" as const,
  },
];

const Index = () => {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      
      <main className="flex-1 p-6 overflow-auto">
        <DashboardHeader />
        
        {/* Stats Row */}
        <div className="grid grid-cols-6 gap-3 mb-6">
          {stats.map((stat) => (
            <VoiceStatsCard
              key={stat.title}
              title={stat.title}
              value={stat.value}
              change={stat.change}
              changeLabel={stat.changeLabel}
              icon={stat.icon}
              positive={stat.positive}
              trend={stat.trend}
            />
          ))}
        </div>
        
        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-2">
            <CallsOverTimeChart />
          </div>
          <OutcomesChart />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Left Column - Call Log */}
          <div className="lg:col-span-2">
            <CallLogTable />
          </div>
          
          {/* Right Column - Needs Attention & Quick Actions */}
          <div className="space-y-6">
            <NeedsAttention />
            <QuickActions />
          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;
