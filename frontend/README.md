# IndusVision — Industrial Inspection Dashboard (Frontend)

Modern manufacturing AI dashboard built with **React**, **TypeScript**, **Vite**, **Tailwind CSS**, and **Recharts**.

---

## 🎨 UI Design System

- **Sidebar:** Industrial Dark Navy (`#0B132B`)
- **Workspace:** Clean Slate Light (`#F8FAFC`)
- **Accents:** Precision Cobalt Blue (`#2563EB`)
- **Severity Coding:**
  - 🟢 **LOW**: Emerald (`#10B981`)
  - 🟡 **MEDIUM**: Amber (`#F59E0B`)
  - 🟠 **HIGH**: Safety Orange (`#F97316`)
  - 🔴 **CRITICAL**: Alert Crimson (`#EF4444`)

---

## 🛠️ Getting Started (Terminal 2)

```powershell
cd frontend

# 1. Install NPM dependencies
npm install

# 2. Launch Vite development server
npm run dev
```

Application will be available at: **[http://localhost:5173](http://localhost:5173)**

---

## 📄 Pages Implemented

1. **Dashboard:** KPI summary cards, 7-day inspection trends, defect category breakdown, recent evaluations.
2. **Live Inspection:** File upload, drag-and-drop, quick demo sample picker, live webcam capture, dual original/annotated image toggle, and GenAI recommendations.
3. **Dataset Management:** Real on-disk status for NEU-DET, GC10-DET, and MVTec AD, verified download guides, and YOLO split builder.
4. **Model Management:** YOLO checkpoint catalog, mAP metrics, active model selector, and background training launcher.
5. **Inspection History:** Telemetry search, severity and decision filters, detailed inspection modal, and PDF downloads.
6. **Analytics:** Defect category donut chart, severity distribution bar chart, 14-day defect rate trend line, and Pareto failure mode table.
7. **Audit Reports:** Single-click ReportLab PDF generation, CSV export, and reports library archive.
8. **System Settings:** Gemini API configuration, confidence threshold slider, IoU threshold slider, and severity assessment rules.
