import { useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Command, Search, Phone, Megaphone, ShieldCheck, Calendar, Users, FileText, X } from "lucide-react";
import { backdropFade, scaleIn, staggerContainer, staggerItem } from "@/lib/motion";
import { useKeyboardShortcut } from "@/hooks/use-motion";

interface CommandPaletteProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const commands = [
  { icon: Phone, label: "Start calling", shortcut: "S", category: "Actions" },
  { icon: ShieldCheck, label: "Review flagged calls", shortcut: "R", category: "Actions" },
  { icon: Megaphone, label: "Create campaign", shortcut: "C", category: "Actions" },
  { icon: Calendar, label: "View tomorrow's pickups", shortcut: "T", category: "Navigation" },
  { icon: Users, label: "Search customers", shortcut: "U", category: "Navigation" },
  { icon: FileText, label: "Update scripts", shortcut: "P", category: "Navigation" },
];

export function CommandPalette({ open, onOpenChange }: CommandPaletteProps) {
  useKeyboardShortcut("k", () => onOpenChange(true), { meta: true });
  useKeyboardShortcut("Escape", () => onOpenChange(false));

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]"
          variants={backdropFade}
          initial="hidden"
          animate="visible"
          exit="exit"
        >
          {/* Backdrop */}
          <motion.div
            className="absolute inset-0 bg-background/80 backdrop-blur-sm"
            onClick={() => onOpenChange(false)}
          />

          {/* Palette */}
          <motion.div
            className="relative w-full max-w-lg bg-card border border-border rounded-xl shadow-elevated overflow-hidden"
            variants={scaleIn}
            initial="hidden"
            animate="visible"
            exit="exit"
          >
            {/* Search input */}
            <div className="flex items-center gap-3 px-4 py-3 border-b border-border">
              <Search className="w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Type a command or search..."
                className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground focus:outline-none"
                autoFocus
              />
              <button
                onClick={() => onOpenChange(false)}
                className="p-1 rounded hover:bg-secondary transition-colors"
              >
                <X className="w-4 h-4 text-muted-foreground" />
              </button>
            </div>

            {/* Commands */}
            <motion.div
              className="p-2 max-h-[300px] overflow-auto"
              variants={staggerContainer}
              initial="hidden"
              animate="visible"
            >
              {["Actions", "Navigation"].map((category) => (
                <div key={category} className="mb-2">
                  <p className="px-2 py-1 text-[10px] font-semibold text-muted-foreground uppercase tracking-widest">
                    {category}
                  </p>
                  {commands
                    .filter((c) => c.category === category)
                    .map((command) => (
                      <motion.button
                        key={command.label}
                        className="w-full flex items-center gap-3 px-2 py-2 rounded-lg text-sm text-foreground hover:bg-secondary transition-colors group"
                        variants={staggerItem}
                        onClick={() => onOpenChange(false)}
                      >
                        <command.icon className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
                        <span className="flex-1 text-left">{command.label}</span>
                        <kbd className="px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground bg-secondary rounded border border-border">
                          {command.shortcut}
                        </kbd>
                      </motion.button>
                    ))}
                </div>
              ))}
            </motion.div>

            {/* Footer */}
            <div className="flex items-center justify-between px-4 py-2 border-t border-border bg-secondary/30 text-[10px] text-muted-foreground">
              <span>Navigate with ↑↓</span>
              <span>Select with ↵</span>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
