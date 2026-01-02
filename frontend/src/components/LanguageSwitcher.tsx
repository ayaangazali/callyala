import { memo, useCallback } from "react";
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
  const currentLanguage = i18n.language;

  const changeLanguage = useCallback((lng: string) => {
    i18n.changeLanguage(lng);
  }, [i18n]);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant={variant} size={size}>
          <Languages className="w-4 h-4" />
          {showLabel && (
            <span className="ml-2">
              {currentLanguage === 'en' ? 'English' : 'العربية'}
            </span>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => changeLanguage('en')}>
          <span className="flex items-center gap-2">
            {currentLanguage === 'en' && '✓'} English
          </span>
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => changeLanguage('ar')}>
          <span className="flex items-center gap-2">
            {currentLanguage === 'ar' && '✓'} العربية (Arabic)
          </span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
});

export { LanguageSwitcher };
