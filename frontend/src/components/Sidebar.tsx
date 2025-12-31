import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
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
  Headphones,
  ChevronLeft,
  ChevronRight
} from "lucide-react";
import { NavLink, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { staggerContainer, staggerItem } from "@/lib/motion";

const navItems = [
  { title: "Overview", url: "/", icon: LayoutDashboard },
  { title: "Calls", url: "/calls", icon: Phone },
  { title: "Campaigns", url: "/campaigns", icon: Megaphone },
  { title: "Appointments", url: "/appointments", icon: Calendar },
  { title: "Customers & Vehicles", url: "/customers", icon: Car },
  { title: "Scripts & Prompts", url: "/scripts", icon: FileText },
  { title: "QA / Review", url: "/qa", icon: ShieldCheck },
  { title: "Settings", url: "/settings", icon: Settings },
];

const quickStats = [
  { label: "Today's Calls", value: "127" },
  { label: "Answer Rate", value: "68%" },
  { label: "Booked Today", value: "23", highlight: true },
];

interface SidebarProps {
  collapsed?: boolean;
  onCollapse?: (collapsed: boolean) => void;
}

export function Sidebar({ collapsed = false, onCollapse }: SidebarProps) {
  const location = useLocation();
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);

  return (
    <motion.aside
      initial={false}
      animate={{ width: collapsed ? 72 : 240 }}
      transition={{ type: "spring", stiffness: 400, damping: 35 }}
      className="min-h-screen bg-sidebar border-r border-sidebar-border flex flex-col relative z-20"
    >
      {/* Logo */}
      <div className="p-4 flex items-center gap-3">
        <motion.div 
          className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary to-primary/70 flex items-center justify-center shadow-glow-sm"
          whileHover={{ scale: 1.05, rotate: 3 }}
          transition={{ type: "spring", stiffness: 400, damping: 20 }}
        >
          <Headphones className="w-5 h-5 text-primary-foreground" />
        </motion.div>
        <AnimatePresence mode="wait">
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              transition={{ duration: 0.15 }}
            >
              <h1 className="font-semibold text-sidebar-primary text-sm">Call Yala</h1>
              <p className="text-xs text-sidebar-foreground">AI Voice Calling Platform</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Collapse button */}
      <button
        onClick={() => onCollapse?.(!collapsed)}
        className="absolute -right-3 top-7 w-6 h-6 rounded-full bg-card border border-border flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors shadow-sm z-50"
      >
        {collapsed ? <ChevronRight className="w-3 h-3" /> : <ChevronLeft className="w-3 h-3" />}
      </button>

      {/* Navigation */}
      <nav className="px-3 mt-4 flex-1">
        <AnimatePresence mode="wait">
          {!collapsed && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-[10px] font-semibold text-sidebar-foreground uppercase tracking-widest px-3 mb-3"
            >
              Navigation
            </motion.p>
          )}
        </AnimatePresence>
        <motion.ul 
          className="space-y-1"
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
        >
          {navItems.map((item) => {
            const isActive = location.pathname === item.url || 
              (item.url !== "/" && location.pathname.startsWith(item.url));
            const isHovered = hoveredItem === item.title;
            
            return (
              <motion.li 
                key={item.title}
                variants={staggerItem}
                onHoverStart={() => setHoveredItem(item.title)}
                onHoverEnd={() => setHoveredItem(null)}
              >
                <NavLink
                  to={item.url}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors relative group",
                    isActive 
                      ? "text-sidebar-accent-foreground font-medium" 
                      : "text-sidebar-foreground hover:text-sidebar-accent-foreground",
                    collapsed && "justify-center px-2"
                  )}
                >
                  {/* Active/Hover background */}
                  <AnimatePresence>
                    {(isActive || isHovered) && (
                      <motion.div
                        layoutId="nav-pill"
                        className={cn(
                          "absolute inset-0 rounded-lg",
                          isActive 
                            ? "bg-sidebar-accent" 
                            : "bg-sidebar-accent/50"
                        )}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ type: "spring", stiffness: 400, damping: 30 }}
                      />
                    )}
                  </AnimatePresence>

                  {/* Left indicator bar */}
                  <AnimatePresence>
                    {isActive && (
                      <motion.div
                        layoutId="nav-indicator"
                        className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-primary rounded-r-full"
                        initial={{ opacity: 0, scaleY: 0 }}
                        animate={{ opacity: 1, scaleY: 1 }}
                        exit={{ opacity: 0, scaleY: 0 }}
                        transition={{ type: "spring", stiffness: 400, damping: 30 }}
                      />
                    )}
                  </AnimatePresence>

                  <motion.div
                    className="relative z-10"
                    animate={{ 
                      x: isHovered && !collapsed ? 2 : 0,
                      rotate: isHovered ? 3 : 0
                    }}
                    transition={{ type: "spring", stiffness: 400, damping: 20 }}
                  >
                    <item.icon className="w-4 h-4" />
                  </motion.div>
                  
                  <AnimatePresence mode="wait">
                    {!collapsed && (
                      <motion.span
                        className="relative z-10"
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ 
                          opacity: 1, 
                          x: isHovered ? 2 : 0 
                        }}
                        exit={{ opacity: 0, x: -10 }}
                        transition={{ duration: 0.15 }}
                      >
                        {item.title}
                      </motion.span>
                    )}
                  </AnimatePresence>
                </NavLink>

                {/* Tooltip when collapsed */}
                {collapsed && (
                  <AnimatePresence>
                    {isHovered && (
                      <motion.div
                        initial={{ opacity: 0, x: -5, scale: 0.95 }}
                        animate={{ opacity: 1, x: 0, scale: 1 }}
                        exit={{ opacity: 0, x: -5, scale: 0.95 }}
                        transition={{ type: "spring", stiffness: 400, damping: 25 }}
                        className="absolute left-full ml-2 px-2.5 py-1.5 bg-popover text-popover-foreground text-xs font-medium rounded-md shadow-elevated-sm border border-border whitespace-nowrap z-50"
                      >
                        {item.title}
                      </motion.div>
                    )}
                  </AnimatePresence>
                )}
              </motion.li>
            );
          })}
        </motion.ul>
      </nav>

      {/* Quick Stats */}
      <AnimatePresence mode="wait">
        {!collapsed && (
          <motion.div 
            className="px-3 mt-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <p className="text-[10px] font-semibold text-sidebar-foreground uppercase tracking-widest px-3 mb-3">
              Today's Stats
            </p>
            <div className="space-y-2 px-3 pb-4">
              {quickStats.map((stat, index) => (
                <motion.div 
                  key={stat.label} 
                  className="flex items-center justify-between text-sm"
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <span className="text-sidebar-foreground">{stat.label}</span>
                  <span className={cn(
                    "font-semibold tabular-nums",
                    stat.highlight ? "text-success" : "text-sidebar-primary"
                  )}>
                    {stat.value}
                  </span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Compliance Badge */}
      <AnimatePresence mode="wait">
        {!collapsed && (
          <motion.div 
            className="px-6 py-3 border-t border-sidebar-border"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="flex items-center gap-2 text-xs text-sidebar-foreground">
              <motion.div 
                className="w-1.5 h-1.5 rounded-full bg-success"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
              />
              <span>Recording Disclosure: ON</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-sidebar-foreground mt-1.5">
              <motion.div 
                className="w-1.5 h-1.5 rounded-full bg-success"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 2, repeat: Infinity, repeatDelay: 3, delay: 0.5 }}
              />
              <span>DNC List: Active</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Footer */}
      <div className="p-3 border-t border-sidebar-border">
        <div className={cn(
          "flex items-center gap-3 px-3 py-2",
          collapsed && "justify-center px-0"
        )}>
          <motion.div 
            className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-primary/70 flex items-center justify-center text-primary-foreground text-xs font-semibold shadow-sm"
            whileHover={{ scale: 1.05 }}
          >
            AF
          </motion.div>
          <AnimatePresence mode="wait">
            {!collapsed && (
              <motion.div 
                className="flex-1 min-w-0"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
              >
                <p className="text-sm font-medium text-sidebar-primary truncate">Al Futtaim Motors</p>
                <p className="text-xs text-sidebar-foreground truncate">Dubai Branch</p>
              </motion.div>
            )}
          </AnimatePresence>
          <AnimatePresence mode="wait">
            {!collapsed && (
              <motion.button 
                className="text-sidebar-foreground hover:text-sidebar-primary transition-colors p-1 rounded-md hover:bg-sidebar-accent"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                whileHover={{ rotate: 45 }}
                transition={{ type: "spring", stiffness: 400, damping: 20 }}
              >
                <Settings className="w-4 h-4" />
              </motion.button>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.aside>
  );
}
