import { useEffect, useState } from 'react';

/**
 * Hook para debounce de valores
 * Útil para evitar llamadas excesivas a la API mientras el usuario escribe o mueve el mapa
 */
export function useDebounce<T>(value: T, delay: number = 500): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}
