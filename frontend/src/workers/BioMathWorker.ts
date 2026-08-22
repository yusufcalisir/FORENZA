// BioMathWorker.ts
// Offloads forensic biocomputational mathematics from the main UI thread.

import {
  calculateClientBgaPosterior,
  calculateClientHIrisPlex,
} from "@/utils/snpPhenotypeBgaEngine";
import { Ystr27LocusEngine } from "@/utils/ystr27LocusEngine";
import { MtdnaEmpopEngine } from "@/utils/mtdnaEmpopEngine";

export interface MathWorkerPayload {
  type: "CALC_SNP_TRAITS" | "CALC_YSTR_METRICS" | "CALC_MTDNA_ALIGNMENT" | "CALC_LR_PRODUCT";
  id: string;
  data: any;
}

self.onmessage = (event: MessageEvent<MathWorkerPayload>) => {
  const { type, id, data } = event.data;

  try {
    switch (type) {
      case "CALC_SNP_TRAITS": {
        const { snpDosages } = data;
        const bga = calculateClientBgaPosterior(snpDosages);
        const hiris = calculateClientHIrisPlex(snpDosages);
        self.postMessage({
          id,
          type: "SUCCESS",
          result: { bga, hiris },
        });
        break;
      }

      case "CALC_YSTR_METRICS": {
        const { ystrProfile, theta = 0.02, phrThreshold = 0.50 } = data;
        const haplogroup = Ystr27LocusEngine.predictHaplogroup(ystrProfile);
        const clopper = Ystr27LocusEngine.calculateMatchProbabilityClopperPearson(0, 35000);
        const brenner = Ystr27LocusEngine.calculateBrennerSubpopCorrection(clopper.upperBound, theta);
        const mixture = Ystr27LocusEngine.deconvoluteMaleMixture(ystrProfile, phrThreshold);

        self.postMessage({
          id,
          type: "SUCCESS",
          result: { haplogroup, clopper, brenner, mixture },
        });
        break;
      }

      case "CALC_MTDNA_ALIGNMENT": {
        const { rawMutations } = data;
        const aligned = MtdnaEmpopEngine.alignMutations(rawMutations);
        const haplogroup = MtdnaEmpopEngine.classifyHaplogroup(rawMutations);
        const matchStats = MtdnaEmpopEngine.calculateEmpopMatchProbability(0, 51000);

        self.postMessage({
          id,
          type: "SUCCESS",
          result: { aligned, haplogroup, matchStats },
        });
        break;
      }

      case "CALC_LR_PRODUCT": {
        const { locusLrs } = data;
        const totalLog10Lr = (locusLrs as number[]).reduce((sum, val) => sum + Math.log10(val), 0);
        const totalLr = Math.pow(10, totalLog10Lr);
        const rmp = 1 / totalLr;

        self.postMessage({
          id,
          type: "SUCCESS",
          result: { totalLr, totalLog10Lr, rmp },
        });
        break;
      }

      default:
        self.postMessage({
          id,
          type: "ERROR",
          error: `Unknown worker task type: ${type}`,
        });
    }
  } catch (error: any) {
    self.postMessage({
      id,
      type: "ERROR",
      error: error.message || "Failed to execute biocomputational math task",
    });
  }
};
