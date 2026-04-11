import { describe, it, expect } from 'vitest';
import {
  getBuildingColor,
  getColorForDecade,
  getLegendItems,
  COLOR_UNKNOWN,
  DECADE_COLORS,
} from './buildingColors';

describe('getBuildingColor', () => {
  it('devuelve el color de la decena correspondiente', () => {
    expect(getBuildingColor(1955)).toBe(DECADE_COLORS[1950]);
    expect(getBuildingColor(1900)).toBe(DECADE_COLORS[1900]);
    expect(getBuildingColor(2019)).toBe(DECADE_COLORS[2010]);
  });

  it('devuelve UNKNOWN para null/undefined/0', () => {
    expect(getBuildingColor(null)).toBe(COLOR_UNKNOWN);
    expect(getBuildingColor(undefined)).toBe(COLOR_UNKNOWN);
    expect(getBuildingColor(0)).toBe(COLOR_UNKNOWN);
  });

  it('devuelve UNKNOWN para decadas fuera del rango', () => {
    expect(getBuildingColor(1500)).toBe(COLOR_UNKNOWN);
    expect(getBuildingColor(2100)).toBe(COLOR_UNKNOWN);
  });
});

describe('getColorForDecade', () => {
  it('devuelve el color exacto de la decena', () => {
    expect(getColorForDecade(1970)).toBe(DECADE_COLORS[1970]);
  });

  it('devuelve UNKNOWN cuando la decena no esta definida', () => {
    expect(getColorForDecade(null)).toBe(COLOR_UNKNOWN);
    expect(getColorForDecade(1705)).toBe(COLOR_UNKNOWN);
  });
});

describe('getLegendItems', () => {
  it('solo incluye decadas >= 1900', () => {
    const items = getLegendItems();
    expect(items.length).toBeGreaterThan(0);
    expect(items.every((i) => i.decade >= 1900)).toBe(true);
  });

  it('tiene label con formato "YYYYs"', () => {
    const items = getLegendItems();
    expect(items[0].label).toMatch(/^\d{4}s$/);
  });
});
