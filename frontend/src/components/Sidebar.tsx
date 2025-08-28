import React, { useState } from "react";
import { NavLink } from "react-router-dom";
import {
  Table,
  GanttChart,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

interface NavItem {
  to: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}

const navItems: NavItem[] = [
  { to: "/sheet", label: "Sheet", icon: Table },
  { to: "/gantt", label: "Gantt", icon: GanttChart },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={`h-screen bg-gray-50 border-r border-gray-200 flex flex-col transition-[width] duration-300 ${
        collapsed ? "w-16" : "w-64"
      }`}
    >
      <button
        className="p-2 text-gray-500 hover:text-gray-900"
        onClick={() => setCollapsed((c) => !c)}
        aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
      >
        {collapsed ? (
          <ChevronRight className="h-5 w-5" />
        ) : (
          <ChevronLeft className="h-5 w-5" />
        )}
      </button>
      <nav className="mt-4 flex-1 space-y-1">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-4 px-4 py-2 text-sm text-gray-700 hover:bg-gray-200 ${
                collapsed ? "justify-center" : ""
              } ${isActive ? "bg-gray-200" : ""}`
            }
          >
            <Icon className="h-5 w-5" />
            {!collapsed && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
