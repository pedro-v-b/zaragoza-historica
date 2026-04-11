import { getLegendItems } from '../../utils/buildingColors';

interface BuildingsLegendProps {
  visible: boolean;
}

export default function BuildingsLegend({ visible }: BuildingsLegendProps) {
  if (!visible) return null;

  const items = getLegendItems();

  return (
    <div
      style={{
        position: 'absolute',
        bottom: '18px',
        right: '12px',
        background: 'rgba(255,255,255,0.96)',
        borderRadius: '10px',
        padding: '10px 12px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.18)',
        zIndex: 800,
        maxHeight: '300px',
        overflowY: 'auto',
        fontSize: '12px',
        lineHeight: 1.3,
      }}
    >
      <div style={{ fontWeight: 700, marginBottom: '8px' }}>Edificios por década</div>
      {items.map((item) => (
        <div
          key={item.decade}
          style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '3px' }}
        >
          <span
            style={{
              width: '14px',
              height: '10px',
              backgroundColor: item.color,
              borderRadius: '2px',
              border: '1px solid rgba(0,0,0,0.2)',
              display: 'inline-block',
              flexShrink: 0,
            }}
          />
          <span>{item.label}</span>
        </div>
      ))}
      <div
        style={{
          marginTop: '8px',
          paddingTop: '6px',
          borderTop: '1px solid #e9ecef',
          fontSize: '10px',
          color: '#666',
        }}
      >
        Catastro INSPIRE
        <br />
        Visible desde zoom 14
      </div>
    </div>
  );
}
