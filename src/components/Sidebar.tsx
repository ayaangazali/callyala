import { 
  LayoutDashboard, 
  Phone, 
  Megaphone, 
  Calendar, 
  Car, 
  FileText, 
  ShieldCheck, 
  Puzzle, 
  Settings,
  Headphones
} from "lucide-react";
import { NavLink } from "./NavLink";

const navItems = [
  { title: "Overview", url: "/", icon: LayoutDashboard },
  { title: "Calls", url: "/calls", icon: Phone },
  { title: "Campaigns", url: "/campaigns", icon: Megaphone },
  { title: "Appointments", url: "/appointments", icon: Calendar },
  { title: "Customers & Vehicles", url: "/customers", icon: Car },
  { title: "Scripts & Prompts", url: "/scripts", icon: FileText },
  { title: "QA / Review", url: "/qa", icon: ShieldCheck },
  { title: "Integrations", url: "/integrations", icon: Puzzle },
  { title: "Settings", url: "/settings", icon: Settings },
];

const quickStats = [
  { label: "Today's Calls", value: "127" },
  { label: "Answer Rate", value: "68%" },
  { label: "Booked Today", value: "23", highlight: true },
];

export function Sidebar() {
  return (
    <aside className="w-[240px] min-h-screen bg-sidebar border-r border-sidebar-border flex flex-col">
      {/* Logo */}
      <div className="p-4 flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-accent flex items-center justify-center">
          <Headphones className="w-5 h-5 text-accent-foreground" />
        </div>
        <div>
          <h1 className="font-semibold text-sidebar-primary text-sm">Voice Agent Ops</h1>
          <p className="text-xs text-sidebar-foreground">Dealership AI Calling</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="px-3 mt-4 flex-1">
        <p className="text-[11px] font-medium text-sidebar-foreground uppercase tracking-wider px-3 mb-2">
          Navigation
        </p>
        <ul className="space-y-0.5">
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
      <div className="px-3 mt-4">
        <p className="text-[11px] font-medium text-sidebar-foreground uppercase tracking-wider px-3 mb-3">
          Today's Stats
        </p>
        <div className="space-y-2 px-3 pb-4">
          {quickStats.map((stat) => (
            <div key={stat.label} className="flex items-center justify-between text-sm">
              <span className="text-sidebar-foreground">{stat.label}</span>
              <span className={stat.highlight ? "text-success font-semibold" : "text-sidebar-primary font-medium"}>
                {stat.value}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Compliance Badge */}
      <div className="px-6 py-3 border-t border-sidebar-border">
        <div className="flex items-center gap-2 text-xs text-sidebar-foreground">
          <div className="w-2 h-2 rounded-full bg-success"></div>
          <span>Recording Disclosure: ON</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-sidebar-foreground mt-1">
          <div className="w-2 h-2 rounded-full bg-success"></div>
          <span>DNC List: Active</span>
        </div>
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-sidebar-border">
        <div className="flex items-center gap-3 px-3 py-2">
          <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center text-accent-foreground text-xs font-medium">
            AD
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-sidebar-primary truncate">Al Futtaim Motors</p>
            <p className="text-xs text-sidebar-foreground truncate">Dubai Branch</p>
          </div>
          <button className="text-sidebar-foreground hover:text-sidebar-primary transition-colors">
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
