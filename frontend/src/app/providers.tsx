'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useEffect, useState, type ReactNode } from 'react'
import { WagmiProvider } from 'wagmi'
import { config } from '@/config/wagmi'
import { SaasLanguageProvider } from '@/context/SaaSLanguageContext'
import { SaasLanguage } from '@/dictionaries/saasTranslations'

function ChunkLoadErrorHandler() {
    useEffect(() => {
        const handleChunkError = (event: ErrorEvent | PromiseRejectionEvent) => {
            const error = 'error' in event ? event.error : ('reason' in event ? event.reason : null);
            const msg = String(error?.message || error || '');
            const name = String(error?.name || '');

            const isChunkErr =
                name === 'ChunkLoadError' ||
                msg.includes('Failed to load chunk') ||
                msg.includes('Loading chunk') ||
                msg.includes('ERR_CACHE_READ_FAILURE') ||
                msg.includes('net::ERR_CACHE_READ_FAILURE');

            if (isChunkErr && typeof window !== 'undefined') {
                const now = Date.now();
                const lastReload = parseInt(sessionStorage.getItem('forenza_chunk_retry') || '0', 10);
                if (now - lastReload > 12000) {
                    sessionStorage.setItem('forenza_chunk_retry', String(now));
                    window.location.reload();
                }
            }
        };

        window.addEventListener('error', handleChunkError);
        window.addEventListener('unhandledrejection', handleChunkError);

        return () => {
            window.removeEventListener('error', handleChunkError);
            window.removeEventListener('unhandledrejection', handleChunkError);
        };
    }, []);

    return null;
}

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
                    <ChunkLoadErrorHandler />
                    {children}
                </SaasLanguageProvider>
            </QueryClientProvider>
        </WagmiProvider>
    )
}
