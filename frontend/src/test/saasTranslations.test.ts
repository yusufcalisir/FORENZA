import { describe, it, expect } from "vitest";
import { saasTranslations } from "@/dictionaries/saasTranslations";

function getDeepKeys(obj: Record<string, unknown>, prefix = ""): string[] {
  let keys: string[] = [];
  for (const key of Object.keys(obj)) {
    const fullPath = prefix ? `${prefix}.${key}` : key;
    const value = obj[key];
    if (value && typeof value === "object" && !Array.isArray(value)) {
      keys = keys.concat(getDeepKeys(value as Record<string, unknown>, fullPath));
    } else {
      keys.push(fullPath);
    }
  }
  return keys;
}

describe("Bilingual Dictionary Synchronization (TR & EN)", () => {
  it("should have both 'tr' and 'en' root dictionary objects", () => {
    expect(saasTranslations).toHaveProperty("tr");
    expect(saasTranslations).toHaveProperty("en");
    expect(saasTranslations.tr).toBeDefined();
    expect(saasTranslations.en).toBeDefined();
  });

  it("should have identical key parity across TR and EN dictionaries", () => {
    const trKeys = getDeepKeys(saasTranslations.tr as unknown as Record<string, unknown>).sort();
    const enKeys = getDeepKeys(saasTranslations.en as unknown as Record<string, unknown>).sort();

    const missingInEn = trKeys.filter((k) => !enKeys.includes(k));
    const missingInTr = enKeys.filter((k) => !trKeys.includes(k));

    expect(missingInEn, `Keys present in TR but missing in EN: ${missingInEn.join(", ")}`).toEqual([]);
    expect(missingInTr, `Keys present in EN but missing in TR: ${missingInTr.join(", ")}`).toEqual([]);
  });

  it("should not contain empty string translations in TR or EN", () => {
    const checkNoEmptyValues = (obj: Record<string, unknown>, lang: string, path = "") => {
      for (const [key, value] of Object.entries(obj)) {
        const fullPath = path ? `${path}.${key}` : key;
        if (typeof value === "string") {
          expect(value.trim().length, `Empty translation string found in ${lang} at '${fullPath}'`).toBeGreaterThan(0);
        } else if (value && typeof value === "object" && !Array.isArray(value)) {
          checkNoEmptyValues(value as Record<string, unknown>, lang, fullPath);
        }
      }
    };

    checkNoEmptyValues(saasTranslations.tr as unknown as Record<string, unknown>, "TR");
    checkNoEmptyValues(saasTranslations.en as unknown as Record<string, unknown>, "EN");
  });
});
