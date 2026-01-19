"use client";

interface FeatureCardProps {
  label: string;
  value: string | number | null;
  unit?: string;
  description?: string;
}

export default function FeatureCard({
  label,
  value,
  unit,
  description,
}: FeatureCardProps) {
  const formatValue = (val: string | number | null): string => {
    if (val === null || val === undefined) return "N/A";
    if (typeof val === "number") {
      if (Math.abs(val) >= 1000000) {
        return (val / 1000000).toFixed(2) + "M";
      } else if (Math.abs(val) >= 1000) {
        return (val / 1000).toFixed(2) + "K";
      } else if (Number.isInteger(val)) {
        return val.toString();
      }
      return val.toFixed(2);
    }
    return val;
  };

  return (
    <div className="card p-4">
      <div className="text-sm text-gray-500 mb-1.5">{label}</div>
      <div className="text-2xl font-bold text-gray-900">
        {formatValue(value)}
        {unit && <span className="text-sm font-normal text-gray-400 ml-1">{unit}</span>}
      </div>
      {description && (
        <div className="text-xs text-gray-400 mt-1.5">{description}</div>
      )}
    </div>
  );
}
