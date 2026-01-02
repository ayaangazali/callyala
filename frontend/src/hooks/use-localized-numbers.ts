import { useMemo, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import {
  formatNumber,
  formatCurrency,
  formatPercentage,
  formatDate,
  formatTime,
  formatDuration,
  formatPhoneNumber,
  localizeString,
  toArabicNumerals,
} from '@/lib/i18n-numbers';

/**
 * Custom hook for localized number formatting
 */
export function useLocalizedNumbers() {
  const { i18n } = useTranslation();
  const locale = i18n.language;

  // Memoize the formatter functions to prevent recreation on every render
  const formatters = useMemo(() => ({
    formatNumber: (value: number, options?: Intl.NumberFormatOptions) =>
      formatNumber(value, locale, options),
    formatCurrency: (value: number, currency?: string) =>
      formatCurrency(value, locale, currency),
    formatPercentage: (value: number, decimals?: number) =>
      formatPercentage(value, locale, decimals),
    formatDate: (date: Date | string | number, options?: Intl.DateTimeFormatOptions) =>
      formatDate(date, locale, options),
    formatTime: (date: Date | string | number, options?: Intl.DateTimeFormatOptions) =>
      formatTime(date, locale, options),
    formatDuration: (seconds: number) => formatDuration(seconds, locale),
    formatPhoneNumber: (phone: string) => formatPhoneNumber(phone, locale),
    localizeString: (text: string) => localizeString(text, locale),
  }), [locale]);

  return {
    locale,
    ...formatters,
    toArabicNumerals,
    isArabic: locale === 'ar',
  };
}
