import { Variants } from "framer-motion";

/**
 * MOTION MAP - Reusable animation variants for Voice Agent Ops
 * 
 * Usage: Import variants and use with framer-motion's motion components
 * Example: <motion.div variants={fadeUp} initial="hidden" animate="visible" />
 */

// Fade up animation - KPI cards, panels, list items
export const fadeUp: Variants = {
  hidden: { 
    opacity: 0, 
    y: 8,
    filter: "blur(4px)"
  },
  visible: { 
    opacity: 1, 
    y: 0,
    filter: "blur(0px)",
    transition: {
      duration: 0.3,
      ease: [0.25, 0.46, 0.45, 0.94]
    }
  },
  exit: {
    opacity: 0,
    y: -8,
    filter: "blur(4px)",
    transition: {
      duration: 0.2
    }
  }
};

// Blur in animation - Page transitions, modals
export const blurIn: Variants = {
  hidden: { 
    opacity: 0, 
    filter: "blur(8px)",
    scale: 0.98
  },
  visible: { 
    opacity: 1, 
    filter: "blur(0px)",
    scale: 1,
    transition: {
      duration: 0.35,
      ease: [0.25, 0.46, 0.45, 0.94]
    }
  },
  exit: {
    opacity: 0,
    filter: "blur(8px)",
    scale: 0.98,
    transition: {
      duration: 0.25
    }
  }
};

// Scale in animation - Dropdowns, tooltips
export const scaleIn: Variants = {
  hidden: { 
    opacity: 0, 
    scale: 0.95,
    y: -4
  },
  visible: { 
    opacity: 1, 
    scale: 1,
    y: 0,
    transition: {
      type: "spring",
      stiffness: 500,
      damping: 30
    }
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    transition: {
      duration: 0.15
    }
  }
};

// Drawer spring animation - Side panels, command palette
export const drawerSpring: Variants = {
  hidden: { 
    x: "100%",
    opacity: 0.5
  },
  visible: { 
    x: 0,
    opacity: 1,
    transition: {
      type: "spring",
      stiffness: 400,
      damping: 40
    }
  },
  exit: {
    x: "100%",
    opacity: 0.5,
    transition: {
      type: "spring",
      stiffness: 400,
      damping: 40
    }
  }
};

// Slide up from bottom - Live calling bar, bottom sheets
export const slideUp: Variants = {
  hidden: { 
    y: "100%",
    opacity: 0.8
  },
  visible: { 
    y: 0,
    opacity: 1,
    transition: {
      type: "spring",
      stiffness: 400,
      damping: 35
    }
  },
  exit: {
    y: "100%",
    opacity: 0.8,
    transition: {
      duration: 0.3,
      ease: "easeIn"
    }
  }
};

// Stagger container - For lists of items
export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.1
    }
  },
  exit: {
    opacity: 0,
    transition: {
      staggerChildren: 0.03,
      staggerDirection: -1
    }
  }
};

// Stagger item - Individual items in staggered lists
export const staggerItem: Variants = {
  hidden: { 
    opacity: 0, 
    y: 12,
    filter: "blur(4px)"
  },
  visible: { 
    opacity: 1, 
    y: 0,
    filter: "blur(0px)",
    transition: {
      duration: 0.25,
      ease: [0.25, 0.46, 0.45, 0.94]
    }
  },
  exit: {
    opacity: 0,
    y: -8,
    transition: {
      duration: 0.15
    }
  }
};

// Sidebar pill animation - Active nav item indicator
export const navPill: Variants = {
  inactive: {
    opacity: 0,
    scale: 0.9
  },
  active: {
    opacity: 1,
    scale: 1,
    transition: {
      type: "spring",
      stiffness: 500,
      damping: 30
    }
  }
};

// Icon hover rotation
export const iconHover: Variants = {
  rest: { rotate: 0 },
  hover: { 
    rotate: 6,
    transition: {
      duration: 0.2,
      ease: "easeOut"
    }
  }
};

// Card elevation on hover
export const cardHover: Variants = {
  rest: { 
    y: 0,
    boxShadow: "0 0 0 1px hsl(var(--border))"
  },
  hover: { 
    y: -2,
    boxShadow: "0 8px 30px -12px hsl(0 0% 0% / 0.3), 0 0 0 1px hsl(var(--primary) / 0.15)",
    transition: {
      duration: 0.2,
      ease: "easeOut"
    }
  }
};

// Backdrop fade - Modal backgrounds
export const backdropFade: Variants = {
  hidden: { opacity: 0 },
  visible: { 
    opacity: 1,
    transition: {
      duration: 0.25
    }
  },
  exit: {
    opacity: 0,
    transition: {
      duration: 0.2
    }
  }
};

// Table row animation
export const tableRow: Variants = {
  hidden: { 
    opacity: 0,
    x: -10
  },
  visible: { 
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.2,
      ease: "easeOut"
    }
  },
  exit: {
    opacity: 0,
    x: 10,
    height: 0,
    transition: {
      duration: 0.2
    }
  }
};

// Toast notification animation
export const toastSlide: Variants = {
  hidden: { 
    opacity: 0, 
    y: -20,
    scale: 0.95
  },
  visible: { 
    opacity: 1, 
    y: 0,
    scale: 1,
    transition: {
      type: "spring",
      stiffness: 400,
      damping: 25
    }
  },
  exit: {
    opacity: 0,
    y: -10,
    scale: 0.95,
    transition: {
      duration: 0.2
    }
  }
};

// Highlight sweep - For updated values
export const highlightSweep: Variants = {
  initial: {
    backgroundPosition: "-200% 0"
  },
  highlight: {
    backgroundPosition: "200% 0",
    transition: {
      duration: 1,
      ease: "easeInOut"
    }
  }
};

// Button press animation
export const buttonPress = {
  rest: { scale: 1 },
  pressed: { scale: 0.98 },
  hover: { 
    scale: 1.02,
    transition: { duration: 0.15 }
  }
};

// Success checkmark draw
export const checkmarkDraw: Variants = {
  hidden: {
    pathLength: 0,
    opacity: 0
  },
  visible: {
    pathLength: 1,
    opacity: 1,
    transition: {
      pathLength: {
        duration: 0.4,
        ease: "easeOut"
      },
      opacity: {
        duration: 0.1
      }
    }
  }
};

// Reduced motion variants - respect user preferences
export const reducedMotion: Variants = {
  hidden: { opacity: 0 },
  visible: { 
    opacity: 1,
    transition: { duration: 0.01 }
  },
  exit: { 
    opacity: 0,
    transition: { duration: 0.01 }
  }
};
