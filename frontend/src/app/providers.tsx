'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState, type ReactNode } from 'react'
import { WagmiProvider } from 'wagmi'
import { config } from '@/config/wagmi'

import { SaasLanguageProvider } from '@/context/SaaSLanguageContext'

export function Providers({ children }: { children: ReactNode }) {
    const [queryClient] = useState(() => new QueryClient())

    return (
        <WagmiProvider config={config}>
            <QueryClientProvider client={queryClient}>
                <SaasLanguageProvider>
                    {children}
                </SaasLanguageProvider>
            </QueryClientProvider>
        </WagmiProvider>
    )
}
