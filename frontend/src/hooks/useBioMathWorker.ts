"use client";

import { useEffect, useRef, useCallback } from "react";
import {
  calculateClientBgaPosterior,
  calculateClientHIrisPlex,
} from "@/utils/snpPhenotypeBgaEngine";
import { Ystr27LocusEngine } from "@/utils/ystr27LocusEngine";
import { MtdnaEmpopEngine } from "@/utils/mtdnaEmpopEngine";

export function useBioMathWorker() {
  const workerRef = useRef<Worker | null>(null);
  const pendingRequests = useRef<Map<string, { resolve: (res: any) => void; reject: (err: any) => void }>>(new Map());

  useEffect(() => {
    if (typeof window !== "undefined" && typeof Worker !== "undefined") {
      try {
        const worker = new Worker(new URL("../workers/BioMathWorker.ts", import.meta.url), {
          type: "module",
        });

        worker.onmessage = (e: MessageEvent) => {
          const { id, type, result, error } = e.data;
          const promiseCallbacks = pendingRequests.current.get(id);

          if (promiseCallbacks) {
            if (type === "SUCCESS") {
              promiseCallbacks.resolve(result);
            } else {
              promiseCallbacks.reject(new Error(error));
            }
            pendingRequests.current.delete(id);
          }
        };

        workerRef.current = worker;
      } catch (err) {
        console.warn("Failed to initialize BioMathWorker, falling back to sync calculations:", err);
      }
    }

    return () => {
      workerRef.current?.terminate();
      workerRef.current = null;
    };
  }, []);

  const executeTask = useCallback(
    <T>(type: string, data: any, syncFallback: () => T): Promise<T> => {
      if (!workerRef.current) {
        // Fallback for SSR or environments without Web Workers
        try {
          return Promise.resolve(syncFallback());
        } catch (e) {
          return Promise.reject(e);
        }
      }

      const id = `task-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
      return new Promise<T>((resolve, reject) => {
        pendingRequests.current.set(id, { resolve, reject });
        workerRef.current?.postMessage({ id, type, data });
      });
    },
    []
  );

  const calculateSnpTraitsAsync = useCallback(
    (snpDosages: Record<string, number>) => {
      return executeTask(
        "CALC_SNP_TRAITS",
        { snpDosages },
        () => ({
          bga: calculateClientBgaPosterior(snpDosages),
          hiris: calculateClientHIrisPlex(snpDosages),
        })
      );
    },
    [executeTask]
  );

  const calculateYstrMetricsAsync = useCallback(
    (ystrProfile: Record<string, any>, theta = 0.02, phrThreshold = 0.5) => {
      return executeTask(
        "CALC_YSTR_METRICS",
        { ystrProfile, theta, phrThreshold },
        () => ({
          haplogroup: Ystr27LocusEngine.predictHaplogroup(ystrProfile),
          clopper: Ystr27LocusEngine.calculateMatchProbabilityClopperPearson(0, 35000),
          brenner: Ystr27LocusEngine.calculateBrennerSubpopCorrection(
            Ystr27LocusEngine.calculateMatchProbabilityClopperPearson(0, 35000).upperBound,
            theta
          ),
          mixture: Ystr27LocusEngine.deconvoluteMaleMixture(ystrProfile, phrThreshold),
        })
      );
    },
    [executeTask]
  );

  const calculateMtdnaAlignmentAsync = useCallback(
    (rawMutations: string[]) => {
      return executeTask(
        "CALC_MTDNA_ALIGNMENT",
        { rawMutations },
        () => {
          const aligned = MtdnaEmpopEngine.alignMutations(rawMutations);
          const haplogroup = MtdnaEmpopEngine.classifyHaplogroup(rawMutations);
          const matchStats = MtdnaEmpopEngine.calculateEmpopMatchProbability(0, 51000);
          return { aligned, haplogroup, matchStats };
        }
      );
    },
    [executeTask]
  );

  return {
    calculateSnpTraitsAsync,
    calculateYstrMetricsAsync,
    calculateMtdnaAlignmentAsync,
  };
}
