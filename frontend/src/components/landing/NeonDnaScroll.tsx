"use client";

export default function NeonDnaScroll({ targetId }: { targetId: string }) {
    const handleClick = (e: React.MouseEvent) => {
        e.preventDefault();
        const el = document.getElementById(targetId);
        if (el) {
            el.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    };

    return (
        <button
            onClick={handleClick}
            aria-label="Scroll to next section"
            className="hidden sm:flex flex-col items-center justify-center cursor-pointer group py-2 transition-transform duration-300 hover:scale-110 focus:outline-none"
        >
            <div className="relative flex items-center justify-center">
                {/* SVG DNA Helix - Dikey Duruş & Süzülme Animasyonu */}
                <svg
                    width="28"
                    height="44"
                    viewBox="0 0 28 44"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                    className="animate-bounce duration-1000 drop-shadow-[0_0_12px_rgba(34,197,94,0.8)]"
                >
                    {/* Zümrüt Yeşil Sarmal Dalga */}
                    <path
                        d="M6 4C14 12 22 18 22 26C22 34 14 38 6 42"
                        stroke="#22C55E"
                        strokeWidth="3"
                        strokeLinecap="round"
                    />
                    {/* Siyan Mavi Sarmal Dalga */}
                    <path
                        d="M22 4C14 12 6 18 6 26C6 34 14 38 22 42"
                        stroke="#06B6D4"
                        strokeWidth="3"
                        strokeLinecap="round"
                    />

                    {/* Sarmal Bağlantı Basamakları */}
                    <line x1="8" y1="10" x2="20" y2="10" stroke="#8B5CF6" strokeWidth="2" strokeLinecap="round" opacity="0.8" />
                    <line x1="6" y1="22" x2="22" y2="22" stroke="#22C55E" strokeWidth="2" strokeLinecap="round" opacity="0.9" />
                    <line x1="8" y1="34" x2="20" y2="34" stroke="#06B6D4" stroke-width="2" strokeLinecap="round" opacity="0.8" />
                </svg>
            </div>
        </button>
    );
}
