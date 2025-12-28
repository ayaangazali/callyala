import { useEffect, useState, useCallback, useRef } from "react";
import { useReducedMotion } from "framer-motion";

/**
 * Hook to get animation variants based on reduced motion preference
 */
export function useMotionPreference() {
  const prefersReducedMotion = useReducedMotion();
  return { prefersReducedMotion };
}

/**
 * Animated counter hook for KPI numbers
 */
export function useCountUp(
  end: number,
  duration: number = 1000,
  start: number = 0
) {
  const [count, setCount] = useState(start);
  const prefersReducedMotion = useReducedMotion();
  const frameRef = useRef<number>();

  useEffect(() => {
    if (prefersReducedMotion) {
      setCount(end);
      return;
    }

    const startTime = performance.now();
    const difference = end - start;

    const animate = (currentTime: number) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Ease out cubic
      const easeOut = 1 - Math.pow(1 - progress, 3);
      
      setCount(Math.round(start + difference * easeOut));

      if (progress < 1) {
        frameRef.current = requestAnimationFrame(animate);
      }
    };

    frameRef.current = requestAnimationFrame(animate);

    return () => {
      if (frameRef.current) {
        cancelAnimationFrame(frameRef.current);
      }
    };
  }, [end, duration, start, prefersReducedMotion]);

  return count;
}

/**
 * Hook for staggered animations on children
 */
export function useStaggeredReveal(
  itemCount: number,
  staggerDelay: number = 50,
  initialDelay: number = 100
) {
  const [visibleItems, setVisibleItems] = useState<Set<number>>(new Set());

  useEffect(() => {
    const timers: NodeJS.Timeout[] = [];
    
    for (let i = 0; i < itemCount; i++) {
      const timer = setTimeout(() => {
        setVisibleItems(prev => new Set([...prev, i]));
      }, initialDelay + i * staggerDelay);
      timers.push(timer);
    }

    return () => {
      timers.forEach(clearTimeout);
    };
  }, [itemCount, staggerDelay, initialDelay]);

  return visibleItems;
}

/**
 * Hook for detecting when element enters viewport
 */
export function useInViewAnimation(threshold: number = 0.1) {
  const [isInView, setIsInView] = useState(false);
  const [hasAnimated, setHasAnimated] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasAnimated) {
          setIsInView(true);
          setHasAnimated(true);
        }
      },
      { threshold }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [threshold, hasAnimated]);

  return { ref, isInView };
}

/**
 * Hook for smooth value interpolation (lerp)
 */
export function useSmoothValue(
  target: number,
  smoothing: number = 0.1
) {
  const [value, setValue] = useState(target);
  const frameRef = useRef<number>();

  useEffect(() => {
    const animate = () => {
      setValue(current => {
        const diff = target - current;
        if (Math.abs(diff) < 0.01) return target;
        return current + diff * smoothing;
      });
      frameRef.current = requestAnimationFrame(animate);
    };

    frameRef.current = requestAnimationFrame(animate);

    return () => {
      if (frameRef.current) {
        cancelAnimationFrame(frameRef.current);
      }
    };
  }, [target, smoothing]);

  return value;
}

/**
 * Hook for keyboard shortcut handling
 */
export function useKeyboardShortcut(
  key: string,
  callback: () => void,
  modifiers: { ctrl?: boolean; meta?: boolean; shift?: boolean; alt?: boolean } = {}
) {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const { ctrl, meta, shift, alt } = modifiers;
      
      if (
        event.key.toLowerCase() === key.toLowerCase() &&
        (!ctrl || event.ctrlKey) &&
        (!meta || event.metaKey) &&
        (!shift || event.shiftKey) &&
        (!alt || event.altKey)
      ) {
        event.preventDefault();
        callback();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [key, callback, modifiers]);
}

/**
 * Format number with animated transition
 */
export function formatAnimatedNumber(
  value: number,
  options: { prefix?: string; suffix?: string; decimals?: number } = {}
) {
  const { prefix = "", suffix = "", decimals = 0 } = options;
  const formatted = value.toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
  return `${prefix}${formatted}${suffix}`;
}
