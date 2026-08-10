import type { Metadata } from "next";
import LandingHeader from "@/components/landing/LandingHeader";
import LandingHero from "@/components/landing/LandingHero";
import LandingBioSimulator from "@/components/landing/LandingBioSimulator";
import LandingFeatures from "@/components/landing/LandingFeatures";
import LandingArchitecture from "@/components/landing/LandingArchitecture";
import LandingSolutions from "@/components/landing/LandingSolutions";
import LandingSecuritySpecs from "@/components/landing/LandingSecuritySpecs";
import LandingFaq from "@/components/landing/LandingFaq";
import LandingFooter from "@/components/landing/LandingFooter";

export const metadata: Metadata = {
    title: "VANTAGE-STR — Advanced Forensic DNA Intelligence Platform",
    description:
        "VANTAGE-STR combines likelihood ratio STR analysis, generative phenotype reconstruction, and zero-knowledge cryptographic verification with immutable blockchain chain of custody into a single tactical intelligence platform.",
};

export default function RootPage() {
    return (
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
    );
}
