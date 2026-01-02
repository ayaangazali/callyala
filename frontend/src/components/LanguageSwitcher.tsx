import { memo, useCallback, useState } from "react";
import { Languages } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface LanguageSwitcherProps {
  variant?: "default" | "outline" | "ghost";
  size?: "default" | "sm" | "lg" | "icon";
  showLabel?: boolean;
}

const LanguageSwitcher = memo(function LanguageSwitcher({ 
  variant = "outline", 
  size = "default",
  showLabel = true 
}: LanguageSwitcherProps) {
  const { i18n } = useTranslation();
  const [open, setOpen] = useState(false);
  
  // Get current language, handle 'en-US' -> 'en' etc
  const currentLanguage = i18n.language?.startsWith('ar') ? 'ar' : 'en';

  const changeLanguage = useCallback(async (lng: string) => {
    try {
      // Change language
      await i18n.changeLanguage(lng);
      
      // Update document direction
      const dir = lng === 'ar' ? 'rtl' : 'ltr';
      document.documentElement.dir = dir;
      document.documentElement.lang = lng;
      
      // Save to localStorage
      localStorage.setItem('i18nextLng', lng);
      localStorage.setItem('language', lng);
      
      // Close dropdown
      setOpen(false);
    } catch (error) {
      console.error('Failed to change language:', error);
    }
  }, [i18n, currentLanguage]);

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant={variant} size={size} className="gap-2">
          <Languages className="w-4 h-4" />
          {showLabel && (
            <span>
              {currentLanguage === 'ar' ? 'العربية' : 'English'}
            </span>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="min-w-[150px]">
        <DropdownMenuItem 
          onClick={() => changeLanguage('en')}
          className="cursor-pointer"
        >
          <span className="flex items-center gap-2 w-full">
            <span className="w-4">{currentLanguage === 'en' && '✓'}</span>
            <span>English</span>
          </span>
        </DropdownMenuItem>
        <DropdownMenuItem 
          onClick={() => changeLanguage('ar')}
          className="cursor-pointer"
        >
          <span className="flex items-center gap-2 w-full">
            <span className="w-4">{currentLanguage === 'ar' && '✓'}</span>
            <span>العربية (Arabic)</span>
          </span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
});

export { LanguageSwitcher };
