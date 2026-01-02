/**
 * Number Formatting Utilities for Arabic/English
 */

// Arabic-Indic numerals mapping
const arabicNumerals: Record<string, string> = {
  '0': '٠',
  '1': '١',
  '2': '٢',
  '3': '٣',
  '4': '٤',
  '5': '٥',
  '6': '٦',
  '7': '٧',
  '8': '٨',
  '9': '٩',
};

// Reverse mapping cache
const westernNumerals: Record<string, string> = Object.entries(arabicNumerals).reduce(
  (acc, [western, arabic]) => ({ ...acc, [arabic]: western }),
  {}
);

// Cache for number formatters
const numberFormatters = new Map<string, Intl.NumberFormat>();

function getNumberFormatter(locale: string, options?: Intl.NumberFormatOptions): Intl.NumberFormat {
  const key = `${locale}-${JSON.stringify(options || {})}`;
  if (!numberFormatters.has(key)) {
    const formatLocale = locale === 'ar' ? 'ar-AE' : 'en-US';
    numberFormatters.set(key, new Intl.NumberFormat(formatLocale, options));
  }
  return numberFormatters.get(key)!;
}

/**
 * Convert Western (0-9) to Eastern Arabic numerals (٠-٩)
 */
export function toArabicNumerals(value: string | number): string {
  const str = String(value);
  return str.replace(/[0-9]/g, (digit) => arabicNumerals[digit] || digit);
}

/**
 * Convert Eastern Arabic numerals (٠-٩) to Western (0-9)
 */
export function toWesternNumerals(value: string): string {
  return value.replace(/[٠-٩]/g, (digit) => westernNumerals[digit] || digit);
}

/**
 * Format number based on locale
 * @param value - Number to format
 * @param locale - 'en' or 'ar'
 * @param options - Intl.NumberFormat options
 */
export function formatNumber(
  value: number,
  locale: string = 'en',
  options?: Intl.NumberFormatOptions
): string {
  const formatter = getNumberFormatter(locale, options);
  const formatted = formatter.format(value);
  return locale === 'ar' ? toArabicNumerals(formatted) : formatted;
}

/**
 * Format currency based on locale
 */
export function formatCurrency(
  value: number,
  locale: string = 'en',
  currency: string = 'AED'
): string {
  const formatter = getNumberFormatter(locale, {
    style: 'currency',
    currency: currency,
  });
  const formatted = formatter.format(value);
  return locale === 'ar' ? toArabicNumerals(formatted) : formatted;
}

/**
 * Format percentage based on locale
 */
export function formatPercentage(
  value: number,
  locale: string = 'en',
  decimals: number = 0
): string {
  const formatter = getNumberFormatter(locale, {
    style: 'percent',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
  const formatted = formatter.format(value / 100);
  return locale === 'ar' ? toArabicNumerals(formatted) : formatted;
}

/**
 * Format date based on locale
 */
export function formatDate(
  date: Date | string | number,
  locale: string = 'en',
  options?: Intl.DateTimeFormatOptions
): string {
  const dateObj = typeof date === 'string' || typeof date === 'number' ? new Date(date) : date;
  
  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    ...options,
  };

  if (locale === 'ar') {
    const formatted = new Intl.DateTimeFormat('ar-AE', defaultOptions).format(dateObj);
    return toArabicNumerals(formatted);
  }
  return new Intl.DateTimeFormat('en-US', defaultOptions).format(dateObj);
}

/**
 * Format time based on locale
 */
export function formatTime(
  date: Date | string | number,
  locale: string = 'en',
  options?: Intl.DateTimeFormatOptions
): string {
  const dateObj = typeof date === 'string' || typeof date === 'number' ? new Date(date) : date;
  
  const defaultOptions: Intl.DateTimeFormatOptions = {
    hour: '2-digit',
    minute: '2-digit',
    ...options,
  };

  if (locale === 'ar') {
    const formatted = new Intl.DateTimeFormat('ar-AE', defaultOptions).format(dateObj);
    return toArabicNumerals(formatted);
  }
  return new Intl.DateTimeFormat('en-US', defaultOptions).format(dateObj);
}

/**
 * Format duration (seconds) to readable format
 */
export function formatDuration(seconds: number, locale: string = 'en'): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  const parts: string[] = [];
  if (hours > 0) {
    parts.push(locale === 'ar' ? `${toArabicNumerals(hours)} ساعة` : `${hours}h`);
  }
  if (minutes > 0) {
    parts.push(locale === 'ar' ? `${toArabicNumerals(minutes)} دقيقة` : `${minutes}m`);
  }
  if (secs > 0 || parts.length === 0) {
    parts.push(locale === 'ar' ? `${toArabicNumerals(secs)} ثانية` : `${secs}s`);
  }

  return parts.join(locale === 'ar' ? ' و ' : ' ');
}

/**
 * Format phone number based on locale
 */
export function formatPhoneNumber(phone: string, locale: string = 'en'): string {
  if (locale === 'ar') {
    return toArabicNumerals(phone);
  }
  return phone;
}

/**
 * Localize any number in a string
 */
export function localizeString(text: string, locale: string): string {
  if (locale === 'ar') {
    return toArabicNumerals(text);
  }
  return text;
}
