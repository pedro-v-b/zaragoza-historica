import { getLegendItems } from '../../utils/buildingColors';

interface BuildingsLegendProps {
  visible: boolean;
}

export default function BuildingsLegend({ visible }: BuildingsLegendProps) {
  if (!visible) return null;

  const items = getLegendItems();

  return (
    <div className="buildings-legend">
      <div className="buildings-legend-title">Edificios por decada</div>
      <div className="buildings-legend-items">
        {items.map((item) => (
          <div key={item.decade} className="buildings-legend-row">
            <span
              className="buildings-legend-swatch"
              style={{ backgroundColor: item.color }}
            />
            <span>{item.label}</span>
          </div>
        ))}
      </div>
      <div className="buildings-legend-footer">
        Visible desde zoom 14
      </div>
    </div>
  );
}
