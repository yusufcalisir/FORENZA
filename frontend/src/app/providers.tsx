'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState, type ReactNode } from 'react'
import { WagmiProvider } from 'wagmi'
import { config } from '@/config/wagmi'
import { SaasLanguageProvider } from '@/context/SaaSLanguageContext'
import { SaasLanguage } from '@/dictionaries/saasTranslations'

export function Providers({
    children,
    initialLang = "en",
}: {
    children: ReactNode;
    initialLang?: SaasLanguage;
}) {
    const [queryClient] = useState(() => new QueryClient())

    return (
        <WagmiProvider config={config}>
            <QueryClientProvider client={queryClient}>
                <SaasLanguageProvider initialLang={initialLang}>
                    {children}
                </SaasLanguageProvider>
            </QueryClientProvider>
        </WagmiProvider>
    )
}
