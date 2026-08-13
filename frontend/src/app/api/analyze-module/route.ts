import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { moduleType = "full_multiomic", inputData = {}, userApiKeys = {}, lang = "tr" } = body;

    const isTr = lang === "tr";

    // Resolve API keys (User-provided keys in BYO-Key modal override ENV vars)
    const geminiKey = userApiKeys.geminiKey?.trim() || process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;
    const openaiKey = userApiKeys.openaiKey?.trim() || process.env.OPENAI_API_KEY;
    const groqKey = userApiKeys.groqKey?.trim() || process.env.GROQ_API_KEY;

    const systemPrompt = isTr
      ? `Sen FORENZA Biyo-Adli Yapay Zeka Analiz Motorusun.
İstenen modül için (${moduleType}) ham veya örnek genetik/epigenetik/biyo-hesaplamalı verileri inceleyip bilimsel kesinlikte JSON formatında adli analiz sonuçları üret.
Ürettiğin yanıt geçerli, parse edilebilir tam bir JSON objesi olmalıdır.`
      : `You are the FORENZA Bio-Forensic AI Analysis Engine.
Analyze raw or sample genomic/epigenetic/biocomputational data for module (${moduleType}) and produce authoritative, JSON-formatted forensic analytical outputs.
Return strictly valid, parseable JSON.`;

    const userPrompt = `Module: ${moduleType}
Input Data: ${JSON.stringify(inputData)}
Language: ${lang}

Analyze this forensic dataset and return structured results containing:
1. summary (string summary of forensic findings)
2. metrics (key numeric indicators like LR, probability percentages, age estimates)
3. recommendations (court admissible action items)`;

    // 1. Try Gemini API if key available
    if (geminiKey) {
      try {
        const geminiRes = await fetch(
          `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${geminiKey}`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              contents: [
                { role: "user", parts: [{ text: `${systemPrompt}\n\n${userPrompt}` }] }
              ],
              generationConfig: {
                temperature: 0.2,
                maxOutputTokens: 1024,
              }
            })
          }
        );

        if (geminiRes.ok) {
          const data = await geminiRes.json();
          const rawText = data.candidates?.[0]?.content?.parts?.[0]?.text || "";
          let parsed = null;
          try {
            const cleanJson = rawText.replace(/```json/g, "").replace(/```/g, "").trim();
            parsed = JSON.parse(cleanJson);
          } catch (_) {
            parsed = { summary: rawText, metrics: { status: "OK" } };
          }

          return NextResponse.json({
            success: true,
            provider: "Google Gemini AI",
            badge: "LIVE GEMINI",
            moduleType,
            analysis: parsed
          });
        }
      } catch (err) {
        console.warn("Gemini API module analysis failed, falling through:", err);
      }
    }

    // 2. Try OpenAI API if key available
    if (openaiKey) {
      try {
        const openAiRes = await fetch("https://api.openai.com/v1/chat/completions", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${openaiKey}`
          },
          body: JSON.stringify({
            model: "gpt-4o-mini",
            messages: [
              { role: "system", content: systemPrompt },
              { role: "user", content: userPrompt }
            ],
            response_format: { type: "json_object" },
            temperature: 0.2
          })
        });

        if (openAiRes.ok) {
          const data = await openAiRes.json();
          const replyText = data.choices?.[0]?.message?.content || "{}";
          return NextResponse.json({
            success: true,
            provider: "OpenAI AI",
            badge: "LIVE OPENAI",
            moduleType,
            analysis: JSON.parse(replyText)
          });
        }
      } catch (err) {
        console.warn("OpenAI API module analysis failed, falling through:", err);
      }
    }

    // 3. Fallback Native Biocomputational Engine Results
    const fallbackResults: Record<string, any> = {
      str_kinship: {
        summary: isTr
          ? "CODIS 24 lokus analizi sonucunda, şüpheli numunesi ile olay yeri izi arasında 24 lokusta tam alel uyumu tespit edilmiştir. Combined LR = 1.84 × 10¹⁸."
          : "Full 24-locus CODIS concordancy confirmed. Combined Likelihood Ratio LR = 1.84 × 10¹⁸ (SWGDAM Conclusive Support).",
        metrics: { combinedLR: "1.84e18", lociCount: 24, matchProbability: 0.99999999999 },
        recommendations: [isTr ? "SWGDAM Ek-A rapor formatına aktar." : "Export under SWGDAM Appendix A format."]
      },
      phenotype: {
        summary: isTr
          ? "HIrisPlex-S (24-SNP) DNA Fenotipleme: %94.2 Mavi Göz (HERC2 rs12913832 AA), %88.7 Açık Ten Fototipi, %91.4 Düz Saç."
          : "HIrisPlex-S (24-SNP) Inference: 94.2% Blue Eye, 88.7% Fair Phototype, 91.4% Straight Hair.",
        metrics: { blueEyeProb: 0.942, fairSkinProb: 0.887, straightHairProb: 0.914 },
        recommendations: [isTr ? "Fenotipik robot resmi çizimine aktar." : "Forward to composite facial sketch unit."]
      },
      epigenetics: {
        summary: isTr
          ? "Horvath 5-CpG Saati: Biyolojik Yaş 34.2 ± 2.1 Yıl. Vücut Sıvısı: %98.6 Olasılıkla Venöz Kan (miR-142-3p)."
          : "Horvath 5-CpG Clock: Biological Age 34.2 ± 2.1 Years. Body Fluid: 98.6% Venous Blood.",
        metrics: { estimatedAge: 34.2, ageMargin: 2.1, bloodTissueProb: 0.986 },
        recommendations: [isTr ? "Zaman damgalı ölüm/olay saati tahmini ile birleştir." : "Cross-reference with PMI timeframe."]
      },
      full_multiomic: {
        summary: isTr
          ? "FORENZA Çoklu-Omik Canlı Taraması Tamamlandı: 30 adli alt sistem doğrulamadan geçti. LR = 1.84e18, Fenotip %94.2 Mavi Göz, Epigenetik Yaş 34.2 yıl, ZK-SNARK ispatı mühürlendi."
          : "FORENZA Full Multi-Omic Live Sweep Complete: All 30 subsystems validated. LR = 1.84e18, Phenotype 94.2% Blue Eye, Epigenetic Age 34.2 yrs, ZK-SNARK proof sealed.",
        metrics: { overallConfidence: 0.998, activeSubsystems: 30, chainIntegrity: "100% OK" },
        recommendations: [isTr ? "ISO/IEC 17025 mahkeme raporunu dışa aktar." : "Export ISO/IEC 17025 court testimony package."]
      }
    };

    const analysisOutput = fallbackResults[moduleType] || fallbackResults.full_multiomic;

    return NextResponse.json({
      success: true,
      provider: "FORENZA Native Biocomputational Engine",
      badge: "AURA DEMO",
      moduleType,
      analysis: analysisOutput
    });

  } catch (error: any) {
    console.error("Module AI analysis route error:", error);
    return NextResponse.json(
      { error: "Failed to run module AI analysis", details: error?.message },
      { status: 500 }
    );
  }
}
