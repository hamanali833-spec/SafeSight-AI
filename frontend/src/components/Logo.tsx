// SafeSight logo: a safety shield with a camera lens inside (drawn in SVG, no image file).
export function Logo({ className = "h-9 w-9" }: { className?: string }) {
  return (
    <svg viewBox="0 0 40 40" className={className} aria-hidden="true">
      <path d="M20 2.5l14 5.6v10.2c0 9-6 16.2-14 19.2-8-3-14-10.2-14-19.2V8.1l14-5.6z" fill="#facc15" />
      <path d="M20 6.4l10.6 4.2v7.8c0 6.9-4.5 12.6-10.6 15.1-6.1-2.5-10.6-8.2-10.6-15.1v-7.8L20 6.4z" fill="#0a0a0a" />
      <circle cx="20" cy="19" r="6.2" fill="none" stroke="#facc15" strokeWidth="2.2" />
      <circle cx="20" cy="19" r="2.4" fill="#facc15" />
      <circle cx="22.2" cy="16.8" r="0.9" fill="#0a0a0a" />
    </svg>
  );
}
