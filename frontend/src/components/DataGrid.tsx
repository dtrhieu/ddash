import React, { useMemo, useState } from "react";
import { AgGridReact } from "ag-grid-react";
import { ColDef, themeBalham } from "ag-grid-community";

export type DataGridProps<RowT = any> = {
  title?: string;
  rows: RowT[];
  columns: ColDef<RowT>[];
  loading?: boolean;
  height?: number | string; // container height
  onRefresh?: () => void;
  toolbarRight?: React.ReactNode;
};

/**
 * Reusable AG Grid wrapper with sane defaults and a simple toolbar.
 */
export default function DataGrid<RowT = any>({
  title,
  rows,
  columns,
  loading,
  height = "calc(100vh - 140px)",
  onRefresh,
  toolbarRight,
}: DataGridProps<RowT>) {
  const [quickFilter, setQuickFilter] = useState("");

  const defaultColDef = useMemo<ColDef>(() => ({
    resizable: true,
    sortable: true,
    filter: true,
    suppressHeaderMenuButton: false,
    suppressHeaderContextMenu: false,
  }), []);

  return (
    <div style={{ padding: 16 }}>
      {(title || onRefresh) && (
        <div className="flex items-center justify-between mb-3 gap-2">
          <div className="flex items-center gap-2">
            {title && <h2 className="text-lg font-semibold m-0">{title}</h2>}
            {loading && <span className="text-xs text-gray-500">Loading…</span>}
          </div>
          <div className="flex items-center gap-2">
            <input
              type="search"
              placeholder="Quick filter…"
              value={quickFilter}
              onChange={(e) => setQuickFilter(e.target.value)}
              className="border rounded px-2 py-1 text-sm"
            />
            {onRefresh && (
              <button
                className="border rounded px-2 py-1 text-sm hover:bg-gray-50"
                onClick={onRefresh}
              >
                Refresh
              </button>
            )}
            {toolbarRight}
          </div>
        </div>
      )}

      <div style={{ height, width: "100%" }}>
        <AgGridReact
          theme={themeBalham}
          rowData={rows}
          columnDefs={columns}
          defaultColDef={defaultColDef}
          quickFilterText={quickFilter}
          animateRows={true}
          pagination={true}
          paginationPageSize={20}
          paginationPageSizeSelector={[10, 20, 50, 100]}
        />
      </div>
    </div>
  );
}
