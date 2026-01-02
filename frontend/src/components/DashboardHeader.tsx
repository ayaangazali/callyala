import { memo, useCallback } from "react";
import { motion } from "framer-motion";
import { useTranslation } from "react-i18next";
import { Plus, Upload, Play, Square, Download, Calendar, Search, Command } from "lucide-react";
import { Button } from "@/components/ui/button";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { fadeUp, buttonPress } from "@/lib/motion";
import { cn } from "@/lib/utils";

interface DashboardHeaderProps {
  onOpenCommandPalette?: () => void;
  isCallingActive?: boolean;
  onToggleCalling?: () => void;
}

export const DashboardHeader = memo(function DashboardHeader({ 
  onOpenCommandPalette, 
  isCallingActive = false,
  onToggleCalling 
}: DashboardHeaderProps) {
  const { t } = useTranslation();
  
  return (
    <motion.div 
      className="flex items-start justify-between mb-6"
      variants={fadeUp}
      initial="hidden"
      animate="visible"
    >
      <div>
        <motion.h1 
          className="text-2xl font-semibold text-foreground"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          {t('dashboard.title')}
        </motion.h1>
        <motion.p 
          className="text-muted-foreground mt-1"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          {t('dashboard.subtitle')}
        </motion.p>
      </div>
      
      <motion.div 
        className="flex items-center gap-2"
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.2 }}
      >
        {/* Language Switcher */}
        <LanguageSwitcher variant="ghost" showLabel={false} size="icon" />
        
        {/* Search / Command Palette Trigger */}
        <motion.button
          onClick={onOpenCommandPalette}
          className="flex items-center gap-2 h-9 px-4 text-sm text-muted-foreground bg-secondary/60 hover:bg-secondary/80 border border-border hover:border-border/80 rounded-lg transition-all duration-200 shadow-sm hover:shadow"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <Search className="w-4 h-4" />
          <span className="hidden lg:inline">{t('common.searchPlaceholder')}</span>
          <kbd className="hidden lg:inline-flex items-center gap-0.5 px-1.5 h-5 text-[10px] font-medium bg-background/50 rounded border border-border">
            <Command className="w-2.5 h-2.5" />K
          </kbd>
        </motion.button>

        <div className="h-6 w-px bg-border/50 mx-2" />

        {/* Date Range Selector */}
        <Select defaultValue="today">
          <SelectTrigger className="w-[130px] h-9 text-sm bg-secondary/50 border-border">
            <Calendar className="w-3.5 h-3.5 mr-2 rtl:mr-0 rtl:ml-2 text-muted-foreground" />
            <SelectValue placeholder={t('common.select')} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="today">{t('stats.today')}</SelectItem>
            <SelectItem value="yesterday">{t('common.previous')}</SelectItem>
            <SelectItem value="week">{t('stats.thisWeek')}</SelectItem>
            <SelectItem value="month">{t('stats.thisMonth')}</SelectItem>
          </SelectContent>
        </Select>

        {/* Branch Selector */}
        <Select defaultValue="dubai">
          <SelectTrigger className="w-[150px] h-9 text-sm bg-secondary/50 border-border">
            <SelectValue placeholder={t('common.select')} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="dubai">Dubai Branch</SelectItem>
            <SelectItem value="abudhabi">Abu Dhabi Branch</SelectItem>
            <SelectItem value="sharjah">Sharjah Branch</SelectItem>
            <SelectItem value="all">{t('common.all')} Branches</SelectItem>
          </SelectContent>
        </Select>

        <div className="h-6 w-px bg-border mx-1" />

        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
          <Button variant="ghost" size="sm" className="gap-2 h-9">
            <Upload className="w-4 h-4" />
            <span className="hidden xl:inline">{t('common.upload')}</span>
          </Button>
        </motion.div>

        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
          <Button variant="ghost" size="sm" className="gap-2 h-9">
            <Download className="w-4 h-4" />
            <span className="hidden xl:inline">{t('common.export')}</span>
          </Button>
        </motion.div>

        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
          <Button variant="secondary" size="sm" className="gap-2 h-9">
            <Plus className="w-4 h-4" />
            <span className="hidden xl:inline">{t('campaigns.createCampaign')}</span>
          </Button>
        </motion.div>

        {/* Premium Start Calling Button */}
        <motion.div
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
        >
          <Button 
            size="sm" 
            className={cn(
              "gap-2 h-9 relative overflow-hidden btn-glow",
              isCallingActive && "bg-destructive hover:bg-destructive/90"
            )}
            onClick={onToggleCalling}
          >
            {!isCallingActive && (
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
                initial={{ x: "-100%" }}
                animate={{ x: "200%" }}
                transition={{ 
                  duration: 2,
                  repeat: Infinity,
                  repeatDelay: 3,
                  ease: "easeInOut"
                }}
              />
            )}
            {isCallingActive ? (
              <>
                <Square className="w-3.5 h-3.5" />
                <span>{t('common.stop')}</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5" />
                <span>{t('common.start')} {t('calls.title')}</span>
              </>
            )}
          </Button>
        </motion.div>
      </motion.div>
    </motion.div>
  );
});
