"use client";

export default function ForenzaLogoIcon({
  size = 32,
  className = "",
}: {
  size?: number;
  className?: string;
}) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      className={className}
    >
      <defs>
        <linearGradient id="forenza_logo_border" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#00E599" />
          <stop offset="50%" stopColor="#06B6D4" />
          <stop offset="100%" stopColor="#3B82F6" />
        </linearGradient>
        <linearGradient id="forenza_dna_color" x1="4" y1="4" x2="28" y2="28" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#00E599" />
          <stop offset="100%" stopColor="#06B6D4" />
        </linearGradient>
      </defs>

      {/* Dark Container */}
      <rect width="32" height="32" rx="8" fill="#090D16" />
      {/* Gradient Border Ring */}
      <rect x="0.75" y="0.75" width="30.5" height="30.5" rx="7.25" stroke="url(#forenza_logo_border)" strokeWidth="1.5" />

      {/* DNA Double Helix */}
      <g transform="translate(4, 4)" stroke="url(#forenza_dna_color)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M2 15c6.667-6 13.333 6 20 0" />
        <path d="M2 9c6.667 6 13.333-6 20 0" />
        <path d="m17 6-2.5 2.5" />
        <path d="m14 11-1.5 1.5" />
        <path d="m17 16-2.5 2.5" />
        <path d="m11 6-2.5 2.5" />
        <path d="m8 11-1.5 1.5" />
        <path d="m11 16-2.5 2.5" />
      </g>

      {/* Glowing Dot Top-Right */}
      <circle cx="24.5" cy="7.5" r="2.5" fill="#00E599" />
      <circle cx="24.5" cy="7.5" r="4.2" fill="#00E599" fillOpacity="0.35" />
    </svg>
  );
}
