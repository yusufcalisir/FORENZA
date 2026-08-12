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

// Resolve base URL: custom domain > Vercel auto URL > default production Vercel deployment
const getSiteUrl = () => {
  if (process.env.NEXT_PUBLIC_SITE_URL) {
    const url = process.env.NEXT_PUBLIC_SITE_URL;
    return url.startsWith("http") ? url : `https://${url}`;
  }
  if (process.env.VERCEL_URL) {
    return `https://${process.env.VERCEL_URL}`;
  }
  return "https://forenza-xi.vercel.app";
};

const SITE_URL = getSiteUrl();

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: "FORENZA",
  description: "Forensic Evidence Operating System",
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
    siteName: "FORENZA",
    title: "FORENZA",
    description: "Forensic Evidence Operating System",
    images: [
      {
        url: `${SITE_URL}/og-image.png`,
        width: 1200,
        height: 630,
        alt: "FORENZA",
        type: "image/png",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "FORENZA",
    description: "Forensic Evidence Operating System",
    images: [`${SITE_URL}/og-image.png`],
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
