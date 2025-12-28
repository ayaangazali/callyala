import { LayoutDashboard, Users, Building2, Target, Activity, Settings } from "lucide-react";
import { NavLink } from "./NavLink";

const navItems = [
  { title: "Dashboard", url: "/", icon: LayoutDashboard },
  { title: "Contacts", url: "/contacts", icon: Users },
  { title: "Companies", url: "/companies", icon: Building2 },
  { title: "Deals", url: "/deals", icon: Target },
  { title: "Activities", url: "/activities", icon: Activity },
];

const quickStats = [
  { label: "Active Deals", value: "0" },
  { label: "Total Contacts", value: "0" },
  { label: "Pipeline Value", value: "$0", highlight: true },
];

export function Sidebar() {
  return (
    <aside className="w-[220px] min-h-screen bg-sidebar border-r border-sidebar-border flex flex-col">
      {/* Logo */}
      <div className="p-4 flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-accent flex items-center justify-center">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" className="text-accent-foreground">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
        <div>
          <h1 className="font-semibold text-sidebar-primary text-sm">MarketCRM</h1>
          <p className="text-xs text-sidebar-foreground">Digital Marketing CRM</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="px-3 mt-4">
        <p className="text-[11px] font-medium text-sidebar-foreground uppercase tracking-wider px-3 mb-2">
          Navigation
        </p>
        <ul className="space-y-1">
          {navItems.map((item) => (
            <li key={item.title}>
              <NavLink
                to={item.url}
                end={item.url === "/"}
                className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-colors"
                activeClassName="bg-sidebar-accent text-sidebar-accent-foreground font-medium"
              >
                <item.icon className="w-4 h-4" />
                {item.title}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Quick Stats */}
      <div className="px-3 mt-8">
        <p className="text-[11px] font-medium text-sidebar-foreground uppercase tracking-wider px-3 mb-3">
          Quick Stats
        </p>
        <div className="space-y-2 px-3">
          {quickStats.map((stat) => (
            <div key={stat.label} className="flex items-center justify-between text-sm">
              <span className="text-sidebar-foreground">{stat.label}</span>
              <span className={stat.highlight ? "text-success font-medium" : "text-sidebar-primary font-medium"}>
                {stat.value}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="mt-auto p-3 border-t border-sidebar-border">
        <div className="flex items-center gap-3 px-3 py-2">
          <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center text-accent-foreground text-xs font-medium">
            U
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-sidebar-primary truncate">Sales Team</p>
            <p className="text-xs text-sidebar-foreground truncate">Manage your pipeline</p>
          </div>
          <button className="text-sidebar-foreground hover:text-sidebar-primary transition-colors">
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
