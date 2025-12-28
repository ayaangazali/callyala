import { motion } from "framer-motion";
import { Phone, Pause, SkipForward, Square, Volume2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { slideUp } from "@/lib/motion";

interface LiveCallingBarProps {
  onStop: () => void;
}

export function LiveCallingBar({ onStop }: LiveCallingBarProps) {
  return (
    <motion.div
      className="fixed bottom-0 left-0 right-0 z-40 p-4"
      variants={slideUp}
      initial="hidden"
      animate="visible"
      exit="exit"
    >
      <div className="max-w-4xl mx-auto">
        <div className="glass rounded-2xl border border-border p-4 shadow-elevated">
          <div className="flex items-center gap-4">
            {/* Status */}
            <div className="flex items-center gap-3">
              <motion.div
                className="w-10 h-10 rounded-full bg-success/20 flex items-center justify-center"
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              >
                <Phone className="w-5 h-5 text-success" />
              </motion.div>
              <div>
                <p className="text-sm font-medium text-foreground">Calling in progress</p>
                <p className="text-xs text-muted-foreground">Ahmed Al-Mansour • Toyota Land Cruiser</p>
              </div>
            </div>

            {/* Progress */}
            <div className="flex-1 px-4">
              <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                <span>12 of 45 calls</span>
                <span>27%</span>
              </div>
              <div className="h-1.5 bg-secondary rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-primary rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: "27%" }}
                  transition={{ duration: 0.5 }}
                />
              </div>
            </div>

            {/* Controls */}
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="icon" className="h-9 w-9">
                <Volume2 className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="icon" className="h-9 w-9">
                <Pause className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="icon" className="h-9 w-9">
                <SkipForward className="w-4 h-4" />
              </Button>
              <Button variant="destructive" size="sm" className="gap-2" onClick={onStop}>
                <Square className="w-3 h-3" />
                Stop
              </Button>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
