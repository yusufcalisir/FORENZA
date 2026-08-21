import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";


// Resolve base URL: custom domain > Vercel auto URL > default production Vercel deployment
const getSiteUrl = () => {
  if (process.env.NEXT_PUBLIC_SITE_URL) {
    const url = process.env.NEXT_PUBLIC_SITE_URL;
    return url.startsWith("http") ? url : `https://${url}`;
  }
  if (process.env.VERCEL_URL) {
    return `https://${process.env.VERCEL_URL}`;
  }
  return "https://forenzaos.vercel.app";
};

const SITE_URL = getSiteUrl();

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: "FORENZA | Multi-Omic Forensic Evidence OS",
  description: "Enterprise Multi-Omic Biocomputational Forensic Intelligence Platform & Evidence Operating System.",
  keywords: ["FORENZA", "DNA", "Forensic OS", "CODIS", "Kinship", "HIrisPlex-S", "MCMC"],
  authors: [{ name: "FORENZA Systems" }],
  creator: "FORENZA",
  publisher: "FORENZA",
  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "any" },
      { url: "/icon.png", type: "image/png", sizes: "512x512" },
      { url: "/icon.svg", type: "image/svg+xml" },
    ],
    shortcut: "/favicon.ico",
    apple: [
      { url: "/apple-touch-icon.png", sizes: "180x180", type: "image/png" },
    ],
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    siteName: "FORENZA",
    title: "FORENZA",
    description: "Enterprise Multi-Omic Biocomputational Forensic Intelligence Platform.",
    images: [
      {
        url: "/opengraph-image.png",
        width: 1200,
        height: 630,
        alt: "FORENZA",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "FORENZA",
    description: "Enterprise Multi-Omic Biocomputational Forensic Intelligence Platform.",
    images: ["/twitter-image.png"],
    creator: "@forenza",
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
        className="font-sans antialiased"
        suppressHydrationWarning
      >
        <Providers>{children}</Providers>
      </body>

    </html>
  );
}
