import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
  weight: ["300", "400", "500", "600", "700"],
});

// Resolve base URL: custom domain > Vercel auto URL > localhost
const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL
  ?? (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : "http://localhost:3000");

export const metadata: Metadata = {
  metadataBase: new URL(BASE_URL),
  title: "FORENZA: Forensic Evidence Operating System",
  description: "Enterprise multi-omic biocomputational forensic intelligence platform unifying DNA profiling, kinship, phenotyping, epigenetics, LIMS, QA/QC, and ISO 17025 court admissibility. Powered by VANTAGE v3.0.",
  keywords: ["forensic DNA", "STR analysis", "kinship engine", "probabilistic genotyping", "MCMC", "HIrisPlex", "forensic evidence OS", "LIMS", "ISO 17025"],
  authors: [{ name: "FORENZA Forensic Systems" }],
  creator: "FORENZA",
  publisher: "FORENZA Forensic Systems",
  icons: {
    icon: "/icon.svg",
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://forenza.app",
    siteName: "FORENZA Evidence OS",
    title: "FORENZA: Forensic Evidence Operating System",
    description: "30 biocomputational subsystems. STR profiling, MCMC genotyping, HIrisPlex-S phenotyping, Horvath epigenetic clock, toxicology, LIMS & ISO 17025 court reports. Powered by VANTAGE v3.0.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "FORENZA Forensic Evidence Operating System",
        type: "image/png",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "FORENZA: Forensic Evidence Operating System",
    description: "30 biocomputational subsystems. STR profiling, MCMC genotyping, HIrisPlex-S phenotyping, ISO 17025 court reports. VANTAGE v3.0.",
    images: ["/og-image.png"],
    creator: "@forenza_forensic",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body
        className={`${inter.variable} ${jetbrainsMono.variable} font-sans antialiased`}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
