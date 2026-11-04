import React from "react";
import { SeverityLevel } from "../types";

interface Props {
  severity: SeverityLevel | string;
  size?: "sm" | "md" | "lg";
}

export const SeverityBadge: React.FC<Props> = ({ severity, size = "md" }) => {
  const sev = (severity || "LOW").toUpperCase();

  const colorMap: Record<string, { bg: string; text: string; border: string; dot: string }> = {
    LOW: {
      bg: "bg-emerald-50",
      text: "text-emerald-700",
      border: "border-emerald-200",
      dot: "bg-emerald-500"
    },
    MEDIUM: {
      bg: "bg-amber-50",
      text: "text-amber-800",
      border: "border-amber-200",
      dot: "bg-amber-500"
    },
    HIGH: {
      bg: "bg-orange-50",
      text: "text-orange-800",
      border: "border-orange-200",
      dot: "bg-orange-500"
    },
    CRITICAL: {
      bg: "bg-rose-50",
      text: "text-rose-800",
      border: "border-rose-200",
      dot: "bg-rose-500"
    }
  };

  const style = colorMap[sev] || colorMap["LOW"];
  const sizeClasses = {
    sm: "px-2 py-0.5 text-[10px]",
    md: "px-2.5 py-1 text-xs",
    lg: "px-3.5 py-1.5 text-sm"
  }[size];

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-semibold border ${style.bg} ${style.text} ${style.border} ${sizeClasses}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${style.dot} animate-pulse`} />
      {sev}
    </span>
  );
};
