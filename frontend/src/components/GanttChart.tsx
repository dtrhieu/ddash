import React, { useEffect, useRef } from "react";

// Minimal type for tasks compatible with frappe-gantt
export type GanttTask = {
  id: string;
  name: string;
  start: string | Date;
  end: string | Date;
  progress?: number;
  dependencies?: string;
  custom_class?: string;
};

export type GanttViewMode = "Quarter Day" | "Half Day" | "Day" | "Week" | "Month" | "Year";

export type GanttChartProps = {
  tasks: GanttTask[];
  viewMode?: GanttViewMode;
  onClickTask?: (task: GanttTask) => void;
  onDateChange?: (task: GanttTask, start: Date, end: Date) => void;
  onProgressChange?: (task: GanttTask, progress: number) => void;
  className?: string;
  height?: number;
};

/**
 * Lightweight React wrapper around frappe-gantt.
 * - Dynamically imports the library to keep initial bundle light and avoid SSR issues.
 * - Rebuilds chart when tasks or viewMode change.
 */
export default function GanttChart({
  tasks,
  viewMode = "Week",
  onClickTask,
  onDateChange,
  onProgressChange,
  className,
  height,
}: GanttChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const ganttRef = useRef<any>(null);

  useEffect(() => {
    let isCancelled = false;

    async function mount() {
      const mod = await import("frappe-gantt");
      if (isCancelled) return;

      // Clear previous chart if any
      if (ganttRef.current && (ganttRef.current as any).svg) {
        // Remove old SVG/content
        if (containerRef.current) containerRef.current.innerHTML = "";
      }

      const Gantt = (mod as any).default ?? (mod as any);
      if (!containerRef.current) return;

      const instance = new Gantt(containerRef.current, tasks, {
        view_mode: viewMode,
        custom_popup_html: null,
        on_click: (task: any) => onClickTask?.(task),
        on_date_change: (task: any, start: Date, end: Date) => onDateChange?.(task, start, end),
        on_progress_change: (task: any, progress: number) => onProgressChange?.(task, progress),
      });

      ganttRef.current = instance;

      if (height && containerRef.current?.firstElementChild instanceof HTMLElement) {
        containerRef.current.firstElementChild.style.height = `${height}px`;
      }
    }

    mount();

    return () => {
      isCancelled = true;
      // Clean up DOM on unmount
      if (containerRef.current) containerRef.current.innerHTML = "";
      ganttRef.current = null;
    };
    // Recreate chart when tasks or view mode change
  }, [JSON.stringify(tasks), viewMode, onClickTask, onDateChange, onProgressChange, height]);

  return <div className={className} ref={containerRef} />;
}
