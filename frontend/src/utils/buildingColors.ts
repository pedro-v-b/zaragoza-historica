/**
 * Paleta de colores para edificios del Catastro agrupados por época.
 * Gradiente cálido (edificios más antiguos) → frío (más modernos).
 */

// ── Colores por decena ───────────────────────────────────────────────────────
// Gradiente: rojo muy oscuro (más antiguo) → verde muy claro (más moderno)
// Pre-1900: rojos casi negros
// 1900-1940: rojos y naranjas oscuros
// 1940-1970: naranjas y ámbar
// 1970-1990: amarillo-verde
// 1990-2020: verdes cada vez más claros
export const DECADE_COLORS: Record<number, string> = {
  1800: '#3D0000',
  1810: '#4A0000',
  1820: '#580000',
  1830: '#650000',
  1840: '#720000',
  1850: '#7D0500',
  1860: '#871000',
  1870: '#901C00',
  1880: '#972800',
  1890: '#9D3200',
  1900: '#A83800',
  1910: '#B84400',
  1920: '#C85200',
  1930: '#D46200',
  1940: '#DD7800',
  1950: '#E49200',
  1960: '#EBAA00',
  1970: '#DEC200',
  1980: '#B0C800',
  1990: '#78BC20',
  2000: '#46A845',
  2010: '#7ACC70',
  2020: '#B0E898',
};

export const COLOR_UNKNOWN = '#808080';

/**
 * Devuelve el color para una decena concreta.
 * Usado por BuildingsLayer cuando la API devuelve el campo `decade`.
 */
export function getColorForDecade(decade: number | null | undefined): string {
  if (!decade) return COLOR_UNKNOWN;
  return DECADE_COLORS[decade] ?? COLOR_UNKNOWN;
}

/**
 * Devuelve el color para un año exacto de construcción.
 * Calcula la decena internamente.
 */
export function getBuildingColor(year: number | null | undefined): string {
  if (year == null || year <= 0) return COLOR_UNKNOWN;
  const decade = Math.floor(year / 10) * 10;
  return DECADE_COLORS[decade] ?? COLOR_UNKNOWN;
}

// ── Leyenda ──────────────────────────────────────────────────────────────────

export interface LegendItem {
  decade: number;
  color: string;
  label: string;
}

/**
 * Devuelve los items para la leyenda visual (desde 1900 en adelante).
 */
export function getLegendItems(): LegendItem[] {
  return Object.entries(DECADE_COLORS)
    .map(([decade, color]) => ({
      decade: Number(decade),
      color,
      label: `${decade}s`,
    }))
    .filter((item) => item.decade >= 1900);
}
