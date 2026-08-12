"use client";

import React, { useEffect, useState, useRef } from "react";
import { Brain, Bot, Send, User, Sparkles, ShieldCheck, Dna, Eye, Scale } from "lucide-react";
import { useSaasLanguage } from "@/context/SaaSLanguageContext";

interface ChatMessage {
  id: string;
  sender: "aura" | "user";
  text: string;
  timestamp: string;
  badge?: string;
}

const INITIAL_STEPS_TR = [
  { step: 1, content: "CODIS 24 STR lokusları taranıyor (D3S1358, vWA, FGA...)", duration: "120ms" },
  { step: 2, content: "Bayesçi Likelihood Ratio (LR = 1.84e18) hesaplandı.", duration: "450ms" },
  { step: 3, content: "HIrisPlex-S: %94.2 Mavi Göz, %88.7 Açık Ten fototipi.", duration: "300ms" },
  { step: 4, content: "Circom Groth16 ZK-SNARK ispatı doğrulandı (0 Veri Sızıntısı).", duration: "180ms" }
];

const INITIAL_STEPS_EN = [
  { step: 1, content: "Scanning CODIS 24 STR loci (D3S1358, vWA, FGA...)", duration: "120ms" },
  { step: 2, content: "Bayesian Likelihood Ratio (LR = 1.84e18) computed.", duration: "450ms" },
  { step: 3, content: "HIrisPlex-S: 94.2% Blue Eye, 88.7% Fair Phototype II.", duration: "300ms" },
  { step: 4, content: "Circom Groth16 ZK-SNARK proof verified (0 Data Leakage).", duration: "180ms" }
];

export default function InvestigatorSidebar() {
  const { lang } = useSaasLanguage();
  const isTr = lang === "tr";

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Initialize initial welcome & streaming thoughts
  useEffect(() => {
    const welcomeMsg: ChatMessage = {
      id: "welcome-1",
      sender: "aura",
      text: isTr
        ? "FORENZA AURA LOGIC Biyo-Adli Yapay Zeka Asistanı faal. STR profilleri, olabilirlik oranları (LR), fenotip tahminleri ve ZK-SNARK ispatları için soru sorabilirsiniz."
        : "FORENZA AURA LOGIC Bio-Forensic AI Assistant is active. Ask any question regarding STR profiles, Likelihood Ratios (LR), phenotype predictions, and ZK-SNARK proofs.",
      timestamp: isTr ? "Şimdi" : "Just now",
      badge: "ISO 17025 AI"
    };

    setMessages([welcomeMsg]);
  }, [isTr]);

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const handleSendMessage = (textToSend?: string) => {
    const query = (textToSend || inputValue).trim();
    if (!query || isTyping) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: "user",
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    };

    setMessages(prev => [...prev, userMsg]);
    if (!textToSend) setInputValue("");
    setIsTyping(true);

    // Simulate intelligent AI response delay
    setTimeout(() => {
      let aiResponseText = "";
      const lowerQuery = query.toLowerCase();

      if (lowerQuery.includes("str") || lowerQuery.includes("lokus") || lowerQuery.includes("loci") || lowerQuery.includes("lr") || lowerQuery.includes("match")) {
        aiResponseText = isTr
          ? "CODIS 24 lokus analizi sonucunda, şüpheli numunesi ile olay yeri izi arasında 24 lokusta tam alel uyumu tespit edilmiştir. İki katkıcılı MCMC dekonvolüsyon hesabı ile Birleşik Olabilirlik Oranı (Combined LR) = 1.84 × 10¹⁸ olarak hesaplanmıştır. SWGDAM standartlarında 'Kesin İdentifikasyon Desteği' kategorisindedir."
          : "Under CODIS 24 loci evaluation, suspect profile shows full allele concordancy across 24 loci. Combined Likelihood Ratio (LR) via 2-contributor MCMC deconvolution yields LR = 1.84 × 10¹⁸, providing 'Conclusive Support for Identity' under SWGDAM / ENFSI guidelines.";
      } else if (lowerQuery.includes("fenotip") || lowerQuery.includes("phenotype") || lowerQuery.includes("göz") || lowerQuery.includes("eye") || lowerQuery.includes("ten") || lowerQuery.includes("skin") || lowerQuery.includes("saç") || lowerQuery.includes("hair")) {
        aiResponseText = isTr
          ? "HIrisPlex-S (24-SNP) tahmini: Göz rengi %94.2 olasılıkla Mavi (HERC2 rs12913832 AA), Ten Fototipi %88.7 Tip I/II Açık Ten (SLC24A5/SLC45A2 mutasyonları), Saç morfolojisi %91.4 Düz Yapı olarak sınıflandırılmıştır."
          : "HIrisPlex-S (24-SNP) model inference: Eye color 94.2% Blue (HERC2 rs12913832 AA), Skin phototype 88.7% Fitzpatrick Type I/II (SLC24A5/SLC45A2 variants), Hair morphology 91.4% Straight.";
      } else if (lowerQuery.includes("zkp") || lowerQuery.includes("snark") || lowerQuery.includes("gizlilik") || lowerQuery.includes("privacy") || lowerQuery.includes("circom")) {
        aiResponseText = isTr
          ? "Circom Groth16 ZK-SNARK devresi (dna_match.circom) r1cs kısıtlarını başarıyla doğruladı. Ham genetik veri kurum dışına çıkarılmadan LR > 10⁶ eşik koşulu kriptografik olarak ispatlandı. Polygon blokzincir kayıt hash'i oluşturuldu."
          : "Circom Groth16 ZK-SNARK circuit (dna_match.circom) satisfied all r1cs constraints. Cryptographic proof confirmed LR > 10⁶ match criteria without exposing raw genomic sequence data. Polygon ledger hash anchored.";
      } else if (lowerQuery.includes("rapor") || lowerQuery.includes("report") || lowerQuery.includes("iso") || lowerQuery.includes("17025") || lowerQuery.includes("enfsi") || lowerQuery.includes("mahkeme")) {
        aiResponseText = isTr
          ? "ISO/IEC 17025:2017 standartlarına uygun 8 bölümlü Adli Sertifika Raporı hazırlandı. 7 noktalı kalite kontrol (Hb = 0.88, ST = 50 RFU, olumsuz kontrol temiz) onaylandı. PDF mahkeme sunum paketi dışa aktarıma hazır."
          : "ISO/IEC 17025:2017 compliant 8-section Court Evidence Report is compiled. 7-point QA/QC criteria (Hb = 0.88, ST = 50 RFU, negative control clear) verified. PDF court testimony bundle ready for export.";
      } else {
        aiResponseText = isTr
          ? `Sorgunuz işlendi ("${query}"): Biyo-adli veri tabanı ve 30 alt sistem üzerinde analiz yürütüldü. İncelenen numune CODIS 24 standartlarına uygun, kalite kontrolden (%100) geçmiş ve HMAC delil zinciriyle mühürlenmiştir.`
          : `Processed query ("${query}"): Evaluated against FORENZA 30 subsystems. Sample conforms to CODIS 24 standards, passed 100% QA/QC screening, and is anchored via HMAC audit ledger.`;
      }

      const aiMsg: ChatMessage = {
        id: `aura-${Date.now()}`,
        sender: "aura",
        text: aiResponseText,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        badge: "VERIFIED"
      };

      setMessages(prev => [...prev, aiMsg]);
      setIsTyping(false);
    }, 800);
  };

  const initialSteps = isTr ? INITIAL_STEPS_TR : INITIAL_STEPS_EN;

  const quickPrompts = isTr
    ? [
        { label: "STR Uyum Analizi", icon: Dna, query: "STR Lokus ve Likelihood Ratio (LR) eşleşmesini özetle." },
        { label: "Fenotip Tahmini", icon: Eye, query: "HIrisPlex-S fenotipik fiziksel görünüş tahminleri nedir?" },
        { label: "ZK-SNARK Gizlilik", icon: ShieldCheck, query: "Circom ZKP gizlilik ve veri sızıntısı durumu nedir?" },
        { label: "ISO 17025 Raporu", icon: Scale, query: "ISO 17025 mahkeme raporu ve kalite kontrol durumu." }
      ]
    : [
        { label: "STR Match Summary", icon: Dna, query: "Summarize STR Loci and Combined Likelihood Ratio (LR)." },
        { label: "Phenotype Inference", icon: Eye, query: "What are the HIrisPlex-S phenotype predictions?" },
        { label: "ZK-SNARK Privacy", icon: ShieldCheck, query: "Check Circom ZKP privacy proof status." },
        { label: "ISO 17025 Report", icon: Scale, query: "ISO 17025 court testimony and QA/QC status." }
      ];

  return (
    <div className="h-full flex flex-col bg-[#070D18] border-l border-tactical-border/80 font-mono text-tactical-text select-none">
      {/* ── Top Header ── */}
      <div className="p-3.5 border-b border-tactical-border/80 bg-tactical-surface/60 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-xl bg-purple-500/20 border border-purple-500/40 flex items-center justify-center text-purple-300 shadow-[0_0_12px_rgba(168,85,247,0.2)]">
            <Brain className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-white">Aura Logic AI</h3>
            <p className="text-[9px] text-zinc-500 leading-none mt-0.5">
              {isTr ? "Biyo-Adli Akıllı Asistan" : "Bio-Forensic AI Intelligence"}
            </p>
          </div>
        </div>
        <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-[9px] text-emerald-300 font-bold uppercase tracking-wider flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          ONLINE
        </span>
      </div>

      {/* ── Chat Messages Body ── */}
      <div className="flex-1 overflow-y-auto p-3.5 space-y-3.5 min-h-0">
        {/* Initial Automated Workflow Log Stream */}
        <div className="p-3 rounded-xl bg-black/40 border border-tactical-border/60 space-y-2 text-[11px]">
          <div className="flex items-center justify-between border-b border-tactical-border/40 pb-1.5">
            <span className="text-[9px] font-bold uppercase text-zinc-400 tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-3 h-3 text-cyan-400" />
              {isTr ? "Otomatik Delil Boru Hattı" : "Automated Evidence Pipeline"}
            </span>
            <span className="text-[9px] text-emerald-400 font-bold">100% OK</span>
          </div>
          {initialSteps.map(item => (
            <div key={item.step} className="flex items-start justify-between gap-2 text-zinc-300 leading-snug">
              <div className="flex items-start gap-1.5 min-w-0">
                <span className="h-1.5 w-1.5 rounded-full bg-purple-400 mt-1 shrink-0" />
                <span className="truncate text-[10px]">{item.content}</span>
              </div>
              <span className="text-[9px] text-zinc-500 font-mono shrink-0">{item.duration}</span>
            </div>
          ))}
        </div>

        {/* Dynamic Chat Messages */}
        {messages.map(msg => (
          <div
            key={msg.id}
            className={`flex gap-2.5 ${msg.sender === "user" ? "flex-row-reverse" : "flex-row"}`}
          >
            <div
              className={`w-7 h-7 rounded-xl flex items-center justify-center shrink-0 border ${
                msg.sender === "aura"
                  ? "bg-purple-500/20 border-purple-500/40 text-purple-300"
                  : "bg-cyan-500/20 border-cyan-500/40 text-cyan-300"
              }`}
            >
              {msg.sender === "aura" ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
            </div>

            <div className={`flex-1 max-w-[85%] space-y-1 ${msg.sender === "user" ? "text-right" : "text-left"}`}>
              <div
                className={`p-3 rounded-2xl border text-xs leading-relaxed ${
                  msg.sender === "user"
                    ? "bg-cyan-500/15 border-cyan-500/40 text-cyan-100 rounded-tr-none"
                    : "bg-tactical-surface border-tactical-border text-zinc-200 rounded-tl-none shadow-md"
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.text}</p>
              </div>
              <div className="flex items-center gap-2 text-[9px] text-zinc-500 px-1">
                <span>{msg.timestamp}</span>
                {msg.badge && (
                  <span className="px-1.5 py-0.2 rounded bg-purple-500/20 text-purple-300 font-bold text-[8px] uppercase border border-purple-500/30">
                    {msg.badge}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}

        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex gap-2.5 items-center">
            <div className="w-7 h-7 rounded-xl bg-purple-500/20 border border-purple-500/40 flex items-center justify-center text-purple-300 shrink-0">
              <Bot className="w-4 h-4" />
            </div>
            <div className="p-3 rounded-2xl bg-tactical-surface border border-tactical-border rounded-tl-none flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-bounce" />
              <span className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-bounce [animation-delay:0.2s]" />
              <span className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-bounce [animation-delay:0.4s]" />
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* ── Quick Action Suggestion Chips ── */}
      <div className="px-3 py-2 border-t border-tactical-border/40 bg-black/30 overflow-x-auto flex items-center gap-1.5 scrollbar-none shrink-0">
        {quickPrompts.map((chip, idx) => {
          const ChipIcon = chip.icon;
          return (
            <button
              key={idx}
              type="button"
              onClick={() => handleSendMessage(chip.query)}
              className="px-2.5 py-1 rounded-lg border border-tactical-border/80 bg-tactical-surface/60 text-[10px] font-bold text-zinc-300 hover:text-cyan-300 hover:border-cyan-500/50 hover:bg-cyan-500/10 transition-all flex items-center gap-1.5 whitespace-nowrap cursor-pointer shrink-0"
            >
              <ChipIcon className="w-3 h-3 text-cyan-400 shrink-0" />
              <span>{chip.label}</span>
            </button>
          );
        })}
      </div>

      {/* ── Interactive Input Area ── */}
      <form
        onSubmit={e => {
          e.preventDefault();
          handleSendMessage();
        }}
        className="p-3 border-t border-tactical-border/80 bg-tactical-surface/40 flex items-center gap-2 shrink-0"
      >
        <input
          type="text"
          value={inputValue}
          onChange={e => setInputValue(e.target.value)}
          placeholder={isTr ? "Aura Logic'e sorun..." : "Ask Aura Logic..."}
          className="flex-1 bg-black/60 border border-tactical-border/80 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/30 transition-all"
        />
        <button
          type="submit"
          disabled={!inputValue.trim() || isTyping}
          className="p-2.5 rounded-xl bg-cyan-500/20 border border-cyan-500/40 text-cyan-300 hover:bg-cyan-500/30 disabled:opacity-40 disabled:pointer-events-none transition-all cursor-pointer shrink-0"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}
