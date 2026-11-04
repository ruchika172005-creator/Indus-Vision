import React from "react";
import { DecisionType } from "../types";
import { CheckCircle2, AlertTriangle, XCircle } from "lucide-react";

interface Props {
  decision: DecisionType | string;
  size?: "sm" | "md" | "lg";
}

export const DecisionBadge: React.FC<Props> = ({ decision, size = "md" }) => {
  const dec = (decision || "PASS").toUpperCase();

  const configMap: Record<string, { label: string; bg: string; text: string; border: string; icon: React.ReactNode }> = {
    PASS: {
      label: "PASS",
      bg: "bg-emerald-500/10",
      text: "text-emerald-700",
      border: "border-emerald-300",
      icon: <CheckCircle2 className="w-3.5 h-3.5" />
    },
    FAIL: {
      label: "FAIL",
      bg: "bg-rose-500/10",
      text: "text-rose-700",
      border: "border-rose-300",
      icon: <XCircle className="w-3.5 h-3.5" />
    },
    MANUAL_REVIEW: {
      label: "MANUAL REVIEW",
      bg: "bg-amber-500/10",
      text: "text-amber-800",
      border: "border-amber-300",
      icon: <AlertTriangle className="w-3.5 h-3.5" />
    }
  };

  const current = configMap[dec] || configMap["MANUAL_REVIEW"];
  const sizeClasses = {
    sm: "px-2 py-0.5 text-[10px]",
    md: "px-2.5 py-1 text-xs",
    lg: "px-3.5 py-1.5 text-sm font-bold"
  }[size];

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-md font-semibold border ${current.bg} ${current.text} ${current.border} ${sizeClasses}`}
    >
      {current.icon}
      {current.label}
    </span>
  );
};
