import type { Metadata } from "next";
import { headers } from "next/headers";
import LandingHeader from "@/components/landing/LandingHeader";
import LandingHero from "@/components/landing/LandingHero";
import LandingBioSimulator from "@/components/landing/LandingBioSimulator";
import LandingFeatures from "@/components/landing/LandingFeatures";
import LandingArchitecture from "@/components/landing/LandingArchitecture";
import LandingSolutions from "@/components/landing/LandingSolutions";
import LandingSecuritySpecs from "@/components/landing/LandingSecuritySpecs";
import LandingFaq from "@/components/landing/LandingFaq";
import LandingFooter from "@/components/landing/LandingFooter";
import { SaasLanguageProvider } from "@/context/SaaSLanguageContext";
import { SaasLanguage } from "@/dictionaries/saasTranslations";

export const metadata: Metadata = {
    title: "FORENZA Forensic Evidence OS",
    description: "Enterprise Multi-Omic Biocomputational Forensic Intelligence Platform",
};

export default async function RootPage() {
    const headersList = await headers();
    
    // Server-side IP Geolocation detection via Vercel & Cloudflare headers
    const country = headersList.get("x-vercel-ip-country") || headersList.get("cf-ipcountry");
    const acceptLang = headersList.get("accept-language") || "";
    
    let initialLang: SaasLanguage = "en";
    
    if (country) {
        // Strict IP Geolocation: Only set Turkish if incoming IP is explicitly from Turkey ('TR')
        initialLang = country.toUpperCase() === "TR" ? "tr" : "en";
    } else if (acceptLang.toLowerCase().startsWith("tr")) {
        // Fallback Accept-Language header if no IP header is present
        initialLang = "tr";
    }

    return (
        <SaasLanguageProvider initialLang={initialLang}>
            <div className="min-h-screen bg-tactical-bg text-tactical-text">
                <LandingHeader />
                <LandingHero />
                <LandingBioSimulator />
                <LandingFeatures />
                <LandingArchitecture />
                <LandingSolutions />
                <LandingSecuritySpecs />
                <LandingFaq />
                <LandingFooter />
            </div>
        </SaasLanguageProvider>
    );
}
