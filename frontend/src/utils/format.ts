export function enumLabel(value: string | null | undefined): string {
  if (!value) return "";
  // Convert snake_case or kebab-case to Title Case
  const s = String(value)
    .replace(/[_-]+/g, " ")
    .trim()
    .toLowerCase();
  return s.replace(/\b\w/g, (c) => c.toUpperCase());
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "";
  const d = new Date(String(value));
  return Number.isNaN(d.getTime()) ? String(value) : d.toLocaleDateString();
}

export function formatDateTime(value: string | null | undefined): string {
  if (!value) return "";
  const d = new Date(String(value));
  return Number.isNaN(d.getTime()) ? String(value) : d.toLocaleString();
}

export function formatMoney(value: string | number | null | undefined, currency = "USD"): string {
  if (value == null) return "";
  const n = typeof value === "string" ? parseFloat(value) : value;
  if (Number.isNaN(n)) return String(value);
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: 0,
  }).format(n);
}
