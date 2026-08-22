import type { Metadata } from "next";
import { headers, cookies } from "next/headers";
import "./globals.css";
import { Providers } from "./providers";
import { SaasLanguage } from "@/dictionaries/saasTranslations";

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

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const cookieStore = await cookies();
  const headersList = await headers();

  const savedLangCookie = cookieStore.get("forenza_saas_lang")?.value;
  let initialLang: SaasLanguage = "en";

  if (savedLangCookie === "tr" || savedLangCookie === "en") {
    initialLang = savedLangCookie;
  } else {
    // Server-side Geolocation & Language detection
    const country = headersList.get("x-vercel-ip-country") || headersList.get("cf-ipcountry") || headersList.get("x-country") || "";
    const acceptLang = headersList.get("accept-language") || "";
    const timezone = headersList.get("x-vercel-ip-timezone") || headersList.get("x-timezone") || "";

    const isTurkishCountry = country.toUpperCase() === "TR";
    const isTurkishLang = /tr(-[a-z]{2})?|\btr\b/i.test(acceptLang);
    const isTurkishTz = /istanbul|turkey/i.test(timezone);

    if (isTurkishCountry || isTurkishLang || isTurkishTz) {
      initialLang = "tr";
    }
  }

  return (
    <html lang={initialLang} className="dark" suppressHydrationWarning>
      <body
        className="font-sans antialiased"
        suppressHydrationWarning
      >
        <Providers initialLang={initialLang}>{children}</Providers>
      </body>
    </html>
  );
}
