import React from "react";

interface Props {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: {
    value: string;
    isPositive?: boolean;
  };
  accentColor?: string;
}

export const MetricCard: React.FC<Props> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  accentColor = "border-blue-500"
}) => {
  return (
    <div className={`bg-white rounded-xl border border-slate-200/90 p-5 shadow-xs hover:shadow-md transition-all duration-200 relative overflow-hidden border-l-4 ${accentColor}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
            {title}
          </p>
          <h3 className="text-2xl font-bold text-slate-900 tracking-tight">
            {value}
          </h3>
          {subtitle && (
            <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
              {subtitle}
            </p>
          )}
        </div>
        <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 text-slate-700 shadow-xs">
          {icon}
        </div>
      </div>
      {trend && (
        <div className="mt-3 pt-3 border-t border-slate-100 flex items-center text-xs">
          <span
            className={`font-semibold mr-1.5 ${
              trend.isPositive ? "text-emerald-600" : "text-rose-600"
            }`}
          >
            {trend.value}
          </span>
          <span className="text-slate-400">vs historical baseline</span>
        </div>
      )}
    </div>
  );
};
