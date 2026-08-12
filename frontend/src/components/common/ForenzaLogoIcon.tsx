"use client";

export default function ForenzaLogoIcon({
  size = 32,
  className = "",
}: {
  size?: number;
  className?: string;
}) {
  return (
    <img
      src="/logo.png"
      alt="FORENZA"
      width={size}
      height={size}
      style={{ width: size, height: size }}
      className={`object-contain shrink-0 ${className}`}
    />
  );
}
