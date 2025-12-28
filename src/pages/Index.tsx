import { Users, Target, DollarSign, Building2, Trophy, TrendingUp } from "lucide-react";
import { Sidebar } from "@/components/Sidebar";
import { DashboardHeader } from "@/components/DashboardHeader";
import { StatsCard } from "@/components/StatsCard";
import { SalesPipeline } from "@/components/SalesPipeline";
import { RecentActivities } from "@/components/RecentActivities";
import { TopDeals } from "@/components/TopDeals";
import { QuickActions } from "@/components/QuickActions";

const stats = [
  { 
    title: "Total Contacts", 
    value: "0", 
    change: "+12%", 
    changeLabel: "from last month", 
    icon: Users 
  },
  { 
    title: "Active Deals", 
    value: "0", 
    change: "+8%", 
    changeLabel: "from last month", 
    icon: Target 
  },
  { 
    title: "Pipeline Value", 
    value: "$0", 
    change: "+23%", 
    changeLabel: "from last month", 
    icon: DollarSign 
  },
  { 
    title: "Companies", 
    value: "0", 
    change: "+5%", 
    changeLabel: "from last month", 
    icon: Building2 
  },
  { 
    title: "Won This Month", 
    value: "0", 
    change: "Great work!", 
    changeLabel: "", 
    icon: Trophy,
    showChart: true
  },
];

const Index = () => {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      
      <main className="flex-1 p-8">
        <DashboardHeader />
        
        {/* Stats Row */}
        <div className="flex gap-4 mb-6 overflow-x-auto">
          {stats.map((stat) => (
            <StatsCard
              key={stat.title}
              title={stat.title}
              value={stat.value}
              change={stat.change}
              changeLabel={stat.changeLabel}
              icon={stat.icon}
              showChart={stat.showChart}
            />
          ))}
        </div>
        
        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Pipeline & Activities */}
          <div className="lg:col-span-2 space-y-6">
            <SalesPipeline />
            <RecentActivities />
          </div>
          
          {/* Right Column - Top Deals & Quick Actions */}
          <div className="space-y-6">
            <TopDeals />
            <QuickActions />
          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;
