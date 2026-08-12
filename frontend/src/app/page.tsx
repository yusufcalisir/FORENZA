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
import LandingUserGuide from "@/components/landing/LandingUserGuide";
import LandingFooter from "@/components/landing/LandingFooter";
import { SaasLanguageProvider } from "@/context/SaaSLanguageContext";
import { SaasLanguage } from "@/dictionaries/saasTranslations";

export const metadata: Metadata = {
    title: "FORENZA Forensic Evidence OS",
    description: "Enterprise Multi-Omic Biocomputational Forensic Intelligence Platform",
};

export default async function RootPage() {
    const headersList = await headers();
    
    // Server-side Geolocation & Language detection
    const country = headersList.get("x-vercel-ip-country") || headersList.get("cf-ipcountry") || headersList.get("x-country") || "";
    const acceptLang = headersList.get("accept-language") || "";
    const timezone = headersList.get("x-vercel-ip-timezone") || headersList.get("x-timezone") || "";
    
    let initialLang: SaasLanguage = "en";
    
    const isTurkishCountry = country.toUpperCase() === "TR";
    const isTurkishLang = /tr(-[a-z]{2})?|\btr\b/i.test(acceptLang);
    const isTurkishTz = /istanbul|turkey/i.test(timezone);

    if (isTurkishCountry || isTurkishLang || isTurkishTz) {
        initialLang = "tr";
    }

    return (
        <SaasLanguageProvider initialLang={initialLang}>
            <div className="min-h-screen bg-tactical-bg text-tactical-text w-full max-w-full overflow-x-hidden relative flex flex-col items-center">
                <div className="w-full max-w-full overflow-x-hidden">
                    <LandingHeader />
                    <LandingHero />
                    <LandingBioSimulator />
                    <LandingFeatures />
                    <LandingArchitecture />
                    <LandingSolutions />
                    <LandingSecuritySpecs />
                    <LandingUserGuide />
                    <LandingFaq />
                    <LandingFooter />
                </div>
            </div>
        </SaasLanguageProvider>
    );
}
