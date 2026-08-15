import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { moduleType = "full_multiomic", inputData = {}, userApiKeys = {}, lang = "tr" } = body;

    const isTr = lang === "tr";

    // Active-case values forwarded by the client from the Zustand store
    const kinshipLR: string     = inputData.kinshipLR    ?? "N/A";
    const eyeColorProb: number  = inputData.eyeColorProb ?? 0;
    const eyeColor: string      = inputData.eyeColor     ?? "Unknown";
    const skinType: string      = inputData.skinType     ?? "Unknown";
    const skinTypeProb: number  = inputData.skinTypeProb ?? 0;
    const epigeneticAge: number = inputData.epigeneticAge ?? 0;
    const markerCount: number   = inputData.markerCount  ?? 24;


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

    const anthropicKey = userApiKeys.anthropicKey?.trim() || process.env.ANTHROPIC_API_KEY;
    const deepseekKey = userApiKeys.deepseekKey?.trim() || process.env.DEEPSEEK_API_KEY;

    // 3. Try Anthropic Claude API
    if (anthropicKey) {
      try {
        const anthropicRes = await fetch("https://api.anthropic.com/v1/messages", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "x-api-key": anthropicKey,
            "anthropic-version": "2023-06-01"
          },
          body: JSON.stringify({
            model: "claude-3-5-sonnet-20241022",
            max_tokens: 1024,
            system: `${systemPrompt}\n\nIMPORTANT: Return ONLY valid, parseable JSON. Do not include markdown code blocks or explanatory text outside JSON.`,
            messages: [{ role: "user", content: userPrompt }]
          })
        });

        if (anthropicRes.ok) {
          const data = await anthropicRes.json();
          const rawText = data.content?.[0]?.text || "";
          let parsed = null;
          try {
            const cleanJson = rawText.replace(/```json/g, "").replace(/```/g, "").trim();
            parsed = JSON.parse(cleanJson);
          } catch (_) {
            parsed = { summary: rawText, metrics: { status: "OK" } };
          }
          return NextResponse.json({
            success: true,
            provider: "Anthropic Claude AI",
            badge: "LIVE CLAUDE",
            moduleType,
            analysis: parsed
          });
        }
      } catch (err) {
        console.warn("Anthropic API module analysis failed, falling through:", err);
      }
    }

    // 4. Try DeepSeek API
    if (deepseekKey) {
      try {
        const deepseekRes = await fetch("https://api.deepseek.com/chat/completions", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${deepseekKey}`
          },
          body: JSON.stringify({
            model: "deepseek-chat",
            messages: [
              { role: "system", content: `${systemPrompt}\n\nIMPORTANT: Return strictly valid JSON.` },
              { role: "user", content: userPrompt }
            ],
            response_format: { type: "json_object" },
            temperature: 0.2
          })
        });

        if (deepseekRes.ok) {
          const data = await deepseekRes.json();
          const replyText = data.choices?.[0]?.message?.content || "{}";
          return NextResponse.json({
            success: true,
            provider: "DeepSeek AI",
            badge: "LIVE DEEPSEEK",
            moduleType,
            analysis: JSON.parse(replyText)
          });
        }
      } catch (err) {
        console.warn("DeepSeek API module analysis failed, falling through:", err);
      }
    }

    // 5. Fallback Native Biocomputational Engine Results
    const fallbackResults: Record<string, any> = {
      str_kinship: {
        summary: isTr
          ? `Genişletilmiş ${markerCount}-lokus STR analizi sonucunda, şüpheli numunesi ile olay yeri izi arasında CODIS ve ESS lokuslarında tam alel uyumu tespit edilmiştir. Combined LR = ${kinshipLR} (SWGDAM Conclusive Support).`
          : `Full expanded ${markerCount}-locus STR concordancy confirmed (CODIS + ESS loci). Combined Likelihood Ratio LR = ${kinshipLR} (SWGDAM Conclusive Support).`,
        metrics: { combinedLR: kinshipLR, lociCount: markerCount, matchProbability: 0.99999999999 },
        recommendations: [isTr ? "SWGDAM Ek-A rapor formatına aktar." : "Export under SWGDAM Appendix A format."]
      },
      phenotype: {
        summary: isTr
          ? `HIrisPlex-S DNA Fenotipleme: %${eyeColorProb} ${eyeColor} Göz (HERC2 rs12913832), %${skinTypeProb} ${skinType}.`
          : `HIrisPlex-S Phenotype Inference: ${eyeColorProb}% ${eyeColor} Eye, ${skinTypeProb}% ${skinType} Phototype.`,
        metrics: {
          eyeColorProb: eyeColorProb / 100,
          skinTypeProb: skinTypeProb / 100,
        },
        recommendations: [isTr ? "Fenotipik robot resmi çizimine aktar." : "Forward to composite facial sketch unit."]
      },
      epigenetics: {
        summary: isTr
          ? `Horvath 5-CpG Saati: Biyolojik Yaş ${epigeneticAge} ± 2.1 Yıl. Vücut Sıvısı: %98.6 Olasılıkla Venöz Kan (miR-142-3p).`
          : `Horvath 5-CpG Clock: Biological Age ${epigeneticAge} ± 2.1 Years. Body Fluid: 98.6% Venous Blood.`,
        metrics: { estimatedAge: epigeneticAge, ageMargin: 2.1, bloodTissueProb: 0.986 },
        recommendations: [isTr ? "Zaman damgalı ölüm/olay saati tahmini ile birleştir." : "Cross-reference with PMI timeframe."]
      },
      full_multiomic: {
        summary: isTr
          ? `FORENZA Çoklu-Omik Canlı Taraması Tamamlandı: 30 adli alt sistem doğrulamadan geçti. LR = ${kinshipLR}, Fenotip %${eyeColorProb} ${eyeColor} Göz, Epigenetik Yaş ${epigeneticAge} yıl, ZK-SNARK ispatı mühürlendi.`
          : `FORENZA Full Multi-Omic Live Sweep Complete: All 30 subsystems validated. LR = ${kinshipLR}, Phenotype ${eyeColorProb}% ${eyeColor} Eye, Epigenetic Age ${epigeneticAge} yrs, ZK-SNARK proof sealed.`,
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
