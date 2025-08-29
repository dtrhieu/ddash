declare module "frappe-gantt" {
  export interface GanttTask {
    id: string;
    name: string;
    start: string | Date;
    end: string | Date;
    progress?: number;
    dependencies?: string;
    custom_class?: string;
  }
  export type ViewMode = "Quarter Day" | "Half Day" | "Day" | "Week" | "Month" | "Year";
  class Gantt {
    constructor(element: HTMLElement, tasks: GanttTask[], options?: {
      view_mode?: ViewMode;
      custom_popup_html?: null | ((task: GanttTask) => string);
      on_click?: (task: GanttTask) => void;
      on_date_change?: (task: GanttTask, start: Date, end: Date) => void;
      on_progress_change?: (task: GanttTask, progress: number) => void;
    });
  }
  export default Gantt;
}
