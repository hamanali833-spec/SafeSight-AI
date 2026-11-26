// Small line icons drawn with inline SVG (no icon library to download).
type P = { className?: string };
const base = "h-5 w-5";
const svg = (path: React.ReactNode, className?: string) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8}
       strokeLinecap="round" strokeLinejoin="round" className={className ?? base} aria-hidden="true">
    {path}
  </svg>
);

export const ShieldIcon = ({ className }: P) =>
  svg(<path d="M12 3l7 3v5c0 4.5-3 8.5-7 10-4-1.5-7-5.5-7-10V6l7-3z" />, className);
export const CameraIcon = ({ className }: P) =>
  svg(<><rect x="3" y="7" width="13" height="10" rx="2" /><path d="M16 11l5-3v8l-5-3" /></>, className);
export const BellIcon = ({ className }: P) =>
  svg(<><path d="M6 16V11a6 6 0 0112 0v5l2 2H4l2-2z" /><path d="M10 21h4" /></>, className);
export const ChartIcon = ({ className }: P) =>
  svg(<><path d="M4 20V10" /><path d="M10 20V4" /><path d="M16 20v-7" /><path d="M22 20H2" /></>, className);
export const ZoneIcon = ({ className }: P) =>
  svg(<><path d="M4 7l6-3 10 4-2 11-12-2-2-10z" /><circle cx="12" cy="11" r="1.5" /></>, className);
export const SunIcon = ({ className }: P) =>
  svg(<><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5L19 19M5 19l1.5-1.5M17.5 6.5L19 5" /></>, className);
export const MoonIcon = ({ className }: P) =>
  svg(<path d="M20 14.5A8 8 0 019.5 4 8 8 0 1020 14.5z" />, className);
export const UploadIcon = ({ className }: P) =>
  svg(<><path d="M12 16V4" /><path d="M7 9l5-5 5 5" /><path d="M4 20h16" /></>, className);
export const HelmetIcon = ({ className }: P) =>
  svg(<><path d="M4 16a8 8 0 0116 0" /><path d="M12 8V5" /><path d="M2 16h20v2H2z" /></>, className);
export const AlertIcon = ({ className }: P) =>
  svg(<><path d="M12 3l10 18H2L12 3z" /><path d="M12 10v5" /><path d="M12 18h.01" /></>, className);
export const LogoutIcon = ({ className }: P) =>
  svg(<><path d="M15 4h4v16h-4" /><path d="M10 8l-4 4 4 4" /><path d="M6 12h10" /></>, className);
export const EyeIcon = ({ className }: P) =>
  svg(<><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z" /><circle cx="12" cy="12" r="3" /></>, className);
export const UserIcon = ({ className }: P) =>
  svg(<><circle cx="12" cy="8" r="4" /><path d="M4 21a8 8 0 0116 0" /></>, className);
