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
  const Gantt: any;
  export default Gantt;
}
