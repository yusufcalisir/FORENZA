# Research Specification: Forensic CLI Batch Input Protocol & Multi-Omic Batch Ingestion (`set-batch` Commands)

*This file is reserved for the Deep Research report on the FORENZA Forensic Terminal CLI Toplu Veri Girişi (`set-batch`) protocol and multi-omic parsing grammar.*
Technical Specification and Formal Command Grammar for forenza-cli: Multi-Omic Batch Data Ingestion EngineIn accredited forensic genomics laboratories operating under ISO/IEC 17025:2017 standards, data ingestion interfaces must combine deterministic parsing, strict validation, and tamper-evident auditability. Interactive command-line interfaces (CLIs) and in-browser DNA terminals require formal tokenization models that eliminate ambiguity across heterogeneous multi-omic datatypes. This technical specification defines the grammar, multi-omic subcommand semantics, validation logic, compliance framework, and golden execution test vectors for forenza-cli, a WebAssembly-compatible forensic batch ingestion engine.1. Unified Forensic CLI Grammar & Lexical SpecificationThe forenza-cli engine relies on an Extended Backus-Naur Form (EBNF) grammar designed to process both interactive single-locus mutations and high-density batch ingestion strings. The lexer uses a deterministic finite-state automaton (DFA) that guarantees linear-time $O(N)$ execution over heterogeneous character streams containing mixed multi-omic delimiters.1.1 Formal EBNF GrammarEBNFForenzaCLICommand  ::= SingleLocusCmd | BatchIngestCmd ;

SingleLocusCmd     ::= DomainPrefix WS Action WS LocusIdentifier WS AllelePayload [ WS RFUPayload ] ;
BatchIngestCmd     ::= DomainPrefix WS BatchAction WS DataFlag WS StringLiteral [ WS OptionFlags ]* ;

DomainPrefix       ::= "str" | "ystr" | "mtdna" | "snp" | "cpg" ;
Action             ::= "set" | "add" | "del" ;
BatchAction        ::= "set-batch" | "import-batch" ;

DataFlag           ::= "--data" | "-d" ;
OptionFlags        ::= RFUFlag | SepFlag | RecalcFlag | TissueFlag | ModeFlag | RefFlag ;

RFUFlag            ::= "--rfu" WS StringLiteral ;
SepFlag            ::= "--sep" WS CharLiteral ;
RecalcFlag         ::= "--recalc" ;
TissueFlag         ::= "--tissue" WS TissueType ;
ModeFlag           ::= "--mode" WS ModeType ;
RefFlag            ::= "--ref" WS RefType ;

TissueType         ::= "BLOOD" | "SALIVA" | "SEMEN" | "BONE" | "BUCCAL" ;
ModeType           ::= "STRICT" | "LENIENT" ;
RefType            ::= "rCRS" | "RSRS" ;

LocusIdentifier    ::= [a-zA-Z0-9_\-/]+ ;
AllelePayload      ::= AlleleValue ( Delimiter AlleleValue )* ;
AlleleValue        ::= Microvariant | IntegerAllele | SexAllele | BaseSymbol | IUPACCode | BetaValue ;

Microvariant       ::= [0-9]+ "." [0-9]+ ;
IntegerAllele      ::= [0-9]+ ;
SexAllele          ::= "X" | "Y" ;
BaseSymbol         ::= "A" | "C" | "G" | "T" | "del" | "DEL" | "-" ;
IUPACCode          ::= "R" | "Y" | "S" | "W" | "K" | "M" | "B" | "D" | "H" | "V" | "N" ;
BetaValue          ::= "0" "." [0-9]+ | "1" "." "0"+ | "0" | "1" ;

RFUPayload         ::= IntegerRFU ( Delimiter IntegerRFU )* ;
IntegerRFU         ::= [0-9]+ ;

Delimiter          ::= "," | ";" | "|" | ":" | WS ;
StringLiteral      ::= '"' [^"]* '"' | "'" [^']* "'" ;
CharLiteral        ::= '"' [^"] '"' | "'" [^'] "'" ;
WS                 ::= [ \t\n\r]+ ;
1.2 Tokenization, Lexing, and Delimiter Handling RulesThe lexical parser operates according to six explicit runtime tokenization and sanitization principles:Quoting Contexts: Quoted string literals wrapped in double quotes ("...") or single quotes ('...') isolate the internal payload, freezing whitespace tokenization and command interpretation. Escaped characters inside string literals require standard backslash escaping (\", \', \\).Whitespace Collapsing: Outside quoted literals, continuous sequences of spaces (\x20), horizontal tabs (\t), line feeds (\n), and carriage returns (\r) collapse into a single whitespace token (WS).Multi-Delimiter Tolerance: The lexer accepts semicolons (;), commas (,), pipes (|), tabs (\t), and newlines (\n) as primary entry separators. Within locus payload blocks, colons (:) partition the target marker name from its observed state, while commas or spaces delineate individual alleles, dosages, or relative fluorescence units (RFU).Escaping Delimiters: Delimiters inside single-locus commands or locus labels must be escaped with a backslash (\;, \,) if they conflict with active batch parsing contexts.Case Sensitivity and Normalization: Subcommands and domain keywords are strictly lower-case (str, ystr, mtdna, snp, cpg). Unquoted locus identifiers automatically undergo uppercase transformation and structural alias mapping prior to database commitment.Non-Printable Byte Filtering: The parser strips all non-printable ASCII control characters (bytes \x00 through \x1F and \x7F, excluding standard whitespace) prior to lexical evaluation, preventing injection attacks or binary corruption during CLI pasting operations.2. Multi-Omic Subcommand Specifications & SyntaxForensic multi-omics integrates varied biological marker types. The forenza-cli parser implements dedicated sub-engines tailored to the specific validation rules and structural demands of each omic layer.2.1 Autosomal Short Tandem Repeat (STR) SubcommandsThe autosomal STR engine ingests 24-locus capillary electrophoresis profiles derived from standard core panels (such as GlobalFiler and PowerPlex Fusion 6C). It verifies allele counts, repeat unit configurations, microvariant suffixes, tri-allelic configurations, homozygosity calculations, and peak heights.Command SyntaxesSingle-Locus Ingestion: str set <locus> <allele1>[,allele2,...] [rfu1,rfu2,...]Batch Ingestion: str set-batch --data "<locus1:a1,a2;locus2:a1,a2;...>" [--rfu "<locus1:r1,r2;...>"] [--sep <char>] [--recalc]Biological and Structural RulesMicrovariants: Formatted as [Integer_Repeats].[Incomplete_Motif_Bases] (e.g., TH01 9.3 represents 9 complete tetranucleotide repeats and a 3-base-pair insertion).Tri-Allelic Patterns: Permitted when single-source samples exhibit three distinct peaks above the analytical threshold (e.g., D21S11:28,29,30).Homozygosity Engine: Ingesting a single allele value (e.g., vWA:16) records a single call. If the --recalc flag is passed, the system automatically expands the call to a explicit homozygous genotype (16,16) and allocates the peak height across both alleles for downstream model compatibility.Sex Markers: AMEL accepts X,Y (male), X,X (female), or single X calls (in cases of Y-deletion).2.2 Y-Chromosomal STR (Y-STR) SubcommandsThe Y-STR module processes lineage-informative male markers, specifically standardizing on the 27-locus Yfiler Plus multiplex. It distinguishes single-copy loci, multi-copy duplicated loci, and rapidly mutating Y-STRs (RM-YSTRs).Command SyntaxesSingle-Locus Ingestion: ystr set <locus> <allele1>[,allele2...] [rfu1...]Batch Ingestion: ystr set-batch --data "<DYS19:14;DYS385a/b:11,14;DYF387S1a/b:35,37;...>" [--rfu "<...>"]Multi-Copy and Rapidly Mutating MechanicsSingle-Copy vs. Multi-Copy Loci: Single-copy markers (e.g., DYS19, DYS391) enforce a single allele call per single-source male profile. Multi-copy duplicated loci (DYS385a/b, DYF387S1a/b, DYS527a/b) mandate exactly two allele calls sorted in ascending numerical order, or a single value expanded to a homozygous duplicated pair.Rapidly Mutating Flags: Markers designated as RM-YSTRs (DYS570, DYS576, DYS627, DYS518, DYS449, DYF387S1a/b) are internally tagged with is_rapidly_mutating = true. This alerts kinship calculation engines to apply elevated mutation rates ($\approx 10^{-2}$) rather than standard low mutation rates ($\approx 10^{-3}$) during paternal lineage likelihood estimations.2.3 Mitochondrial DNA (mtDNA) Control Region SubcommandsThe mtDNA module ingests sequence variants across the control region D-Loop (positions 16024–576) aligned against the revised Cambridge Reference Sequence (rCRS, NC_012920.1) or the Reconstructed Sapiens Reference Sequence (RSRS) following ISFG and EMPOP nomenclature guidelines.Command SyntaxesSingle Variant Ingestion: mtdna set <pos> <mut>Batch Variant Stream: mtdna set-batch --data "263G, 315.1C, 524del, 16093Y, 16519C" [--ref <rCRS|RSRS>]Mutation and Heteroplasmy RulesPoint Substitutions: Recorded as the numeric nucleotide position followed by the novel base (e.g., 263G indicates an A-to-G transition at position 263).Insertions: Formatted using EMPOP decimal notation (e.g., 315.1C denotes a single Cytosine insertion following position 315).Deletions: Notated as the position followed by del or - (e.g., 524del or 524-).IUPAC Heteroplasmy Validation: Point heteroplasmies are captured using official IUPAC ambiguous nucleotide codes.IUPAC SymbolRepresented NucleotidesHeteroplasmy TypeForensic SignificanceRA / GTransition (Purine)High-frequency HVI/HVII point heteroplasmyYC / TTransition (Pyrimidine)Common control region transition heteroplasmyMA / CTransversionRare transversion site variantKG / TTransversionTransversion site variantSC / GTransversionTransversion site variantWA / TTransversionTransversion site variant2.4 Ancestry & Phenotype SNP SubcommandsThis sub-engine ingests single nucleotide polymorphism (SNP) profiles, targeting the 55-SNP Ancestry Informative Marker panel (55-SNP AIM / Kidd Lab panel) for biographic ancestry inference and the 41-SNP HIrisPlex-S system for eye, hair, and skin color prediction.Command SyntaxesSingle SNP Ingestion: snp set <rsID> <dosage|genotype>Batch SNP Ingestion: snp set-batch --data "rs12913832:2, rs1805007:1, rs16891982:0, ..." or snp set-batch --data "rs12913832:G/G, rs1805007:C/T, ..."Dosage and Allele TranslationDosage Value Input: Integer inputs (0, 1, 2) denote the count of minor/effect alleles present at the genomic coordinate (e.g., rs12913832:2).Explicit Genotype Input: Nucleotide allele pairs delimited by slashes or plain double characters (e.g., G/G, C/T, CC). The engine parses nucleotide strings and converts them to allele dosages based on the internally stored human genome reference build (GRCh38/hg38).2.5 Forensic Epigenetics & Age Estimation SubcommandsThe epigenetic engine parses bisulfite-sequencing and pyrosequencing DNA methylation fractions ($\beta$-values) to drive forensic age estimation algorithms, centering on the VISAGE 5-CpG core panel (ELOVL2, FHL2, PENK, TRIM59, KLF14) and extended epigenetic clocks.Command SyntaxesSingle CpG Ingestion: cpg set <locus|cgID> <beta_fraction>Batch Epigenetic Ingestion: cpg set-batch --data "ELOVL2:0.42, FHL2:0.38, PENK:0.31, TRIM59:0.33, KLF14:0.28" [--tissue <BLOOD|SALIVA|SEMEN|BONE|BUCCAL>]Epigenetic Modeling RulesBeta Value Bounds: Methylation levels are restricted to the floating-point interval $\beta \in [0.0, 1.0]$, where $\beta = \frac{M}{M + U + 100}$ ($M$ = methylated intensity, $U$ = unmethylated intensity). Inputs outside this range trigger validation failures.Tissue-Specific Model Calibration: Passing the --tissue flag applies tissue-specific multivariate linear regression or Random Forest model parameters. This adjusts intercept weights and site-specific coefficients, generating chronological age predictions with Mean Absolute Errors (MAE) below 3.5 years.3. Forensic Validation, Sanitization & ISO/IEC 17025 ComplianceData ingested into an accredited LIMS must pass continuous validation gates before being saved to permanent storage. The forenza-cli architecture incorporates three processing layers to normalize data, verify biological limits, enforce transaction integrity, and maintain cryptographic audit trails.3.1 Locus Normalization EngineForensic software systems use varying nomenclature for identical genetic loci. The forenza-cli normalization table maps user-supplied aliases to canonical LIMS keys.DomainUser Alias InputCanonical LIMS Marker KeyGenomic Target / AnnotationAutosomal STRvWA, VWA, vwaVWAChr 12p13.31 (Tetranucleotide)Autosomal STRAMEL, AmelogeninAMELChr Xp22.2 / Yp11.2Autosomal STRPENTA_D, PentaD, Penta DPENTA_DChr 21q22.3 (Pentanucleotide)Y-STRDYS385, DYS385a/bDYS385a/bChr Yq11.221 (Duplicated locus)Y-STRDYF387S1, DYF387S1a/bDYF387S1a/bChr Y (Rapidly Mutating locus)mtDNA315.1C, ins315C, 315.1-C315.1CPoly-C tract insertionmtDNA524del, 524-, DEL524524delAC-repeat region deletionSNPrs12913832, HERC2_rs12913832rs12913832Chr 15q13.1 (Eye color predictor)EpigeneticsTRIM59, cg04523812TRIM59Chr 3q25.33 (VISAGE Age CpG)3.2 Off-Ladder (OL) and Microvariant Validation LogicTo prevent invalid or corrupt calls from entering population databases, forenza-cli checks STR allele calls against ISFG repeat step tables.Decimal Suffix Validation: Microvariants are verified by checking that the decimal suffix (representing leftover partial bases) is strictly smaller than the repeat motif length $M$. For tetranucleotide repeat loci ($M=4$), valid suffixes are .1, .2, and .3. A suffix of .4 is mathematically invalid (e.g., TH01 9.4 is logically equivalent to TH01 10) and causes a parse rejection.Off-Ladder (OL) Handling: Calls tagged as OL during capillary electrophoresis fragment analysis are ingested with an internal flag is_off_ladder = true. This isolates the profile for secondary manual re-injection or sequencing while preserving the surrounding dataset.3.3 Transactional Atomicity Execution ModesSTRICT Mode (Default): Enforces full ACID atomicity. If a single locus in a multi-locus batch string contains a syntax error, illegal allele character, or out-of-bounds CpG fraction, the entire transaction rolls back. No database records are altered, and the system returns a diagnostic error detailing the exact character offset, token, and failed rule.LENIENT Mode: Implements robust partial ingestion. Valid locus entries are processed and committed to LIMS storage. Invalid entries are skipped and appended to a non-fatal warning array returned in the execution summary.3.4 ISO/IEC 17025 Cryptographic Audit Trail GenerationTo comply with ISO/IEC 17025:2017 technical record requirements (Clause 7.5), every executed command generates an immutable, cryptographically verifiable audit record.The engine computes two SHA-256 digests for each transaction:raw_command_hash: $\text{SHA-256}(\text{Raw CLI Command String})$canonical_state_hash: $\text{SHA-256}(\text{Canonical JSON Output Payload})$These digests are incorporated into an internal Merkle tree structure, yielding a root hash ($\text{Merkle}_{\text{Root}}$) that guarantees non-repudiation and tamper-evident tracking across the sample lifecycle.4. Golden Benchmark Execution Test VectorsThe following six execution vectors provide exact CLI input strings alongside their parsed, canonical LIMS JSON output structures.VECTOR_CLI_01: Pristine 24-Locus Autosomal STR Batch Entry (str set-batch)CLI Input CommandBashstr set-batch --data "AMEL:X,Y;CSF1PO:10,12;D1S1656:12,15.3;D2S441:11,14;D2S1338:17,23;D3S1358:15,18;D5S818:11,13;D7S820:8,11;D8S1179:12,14;D10S1248:13,15;D12S391:18,22;D13S317:11,12;D16S539:9,13;D18S51:14,20;D19S433:13,14.2;D21S11:28,30;D22S1045:11,16;FGA:21,24;TH01:6,9.3;TPOX:8,11;VWA:16,18;SE33:17,25.2;PENTA_D:9,12;PENTA_E:7,14" --rfu "AMEL:1250,1180;CSF1PO:850,910;D1S1656:1100,1050;D2S441:950,980;D2S1338:1300,1210;D3S1358:1400,1350;D5S818:880,920;D7S820:790,810;D8S1179:1150,1120;D10S1248:1020,990;D12S391:650,620;D13S317:900,870;D16S539:840,860;D18S51:710,690;D19S433:980,940;D21S11:1050,1010;D22S1045:1120,1080;FGA:890,850;TH01:1500,1420;TPOX:1100,1050;VWA:1350,1280;SE33:550,510;PENTA_D:920,890;PENTA_E:810,780" --mode STRICT
Parsed Canonical State Output (LIMS JSON)JSON{
  "transaction_id": "tx_str_998142a7_20230815",
  "domain": "AUTOSOMAL_STR",
  "kit_name": "GlobalFiler_PowerPlex_Fusion_Combined_24",
  "status": "COMMITTED",
  "execution_mode": "STRICT",
  "loci_count": 24,
  "profiles": {
    "AMEL": {"alleles": ["X", "Y"], "rfu": [1250, 1180], "is_microvariant": false},
    "CSF1PO": {"alleles": ["10", "12"], "rfu": [850, 910], "is_microvariant": false},
    "D1S1656": {"alleles": ["12", "15.3"], "rfu": [1100, 1050], "is_microvariant": true},
    "D2S441": {"alleles": ["11", "14"], "rfu": [950, 980], "is_microvariant": false},
    "D2S1338": {"alleles": ["17", "23"], "rfu": [1300, 1210], "is_microvariant": false},
    "D3S1358": {"alleles": ["15", "18"], "rfu": [1400, 1350], "is_microvariant": false},
    "D5S818": {"alleles": ["11", "13"], "rfu": [880, 920], "is_microvariant": false},
    "D7S820": {"alleles": ["8", "11"], "rfu": [790, 810], "is_microvariant": false},
    "D8S1179": {"alleles": ["12", "14"], "rfu": [1150, 1120], "is_microvariant": false},
    "D10S1248": {"alleles": ["13", "15"], "rfu": [1020, 990], "is_microvariant": false},
    "D12S391": {"alleles": ["18", "22"], "rfu": [650, 620], "is_microvariant": false},
    "D13S317": {"alleles": ["11", "12"], "rfu": [900, 870], "is_microvariant": false},
    "D16S539": {"alleles": ["9", "13"], "rfu": [840, 860], "is_microvariant": false},
    "D18S51": {"alleles": ["14", "20"], "rfu": [710, 690], "is_microvariant": false},
    "D19S433": {"alleles": ["13", "14.2"], "rfu": [980, 940], "is_microvariant": true},
    "D21S11": {"alleles": ["28", "30"], "rfu": [1050, 1010], "is_microvariant": false},
    "D22S1045": {"alleles": ["11", "16"], "rfu": [1120, 1080], "is_microvariant": false},
    "FGA": {"alleles": ["21", "24"], "rfu": [890, 850], "is_microvariant": false},
    "TH01": {"alleles": ["6", "9.3"], "rfu": [1500, 1420], "is_microvariant": true},
    "TPOX": {"alleles": ["8", "11"], "rfu": [1100, 1050], "is_microvariant": false},
    "VWA": {"alleles": ["16", "18"], "rfu": [1350, 1280], "is_microvariant": false},
    "SE33": {"alleles": ["17", "25.2"], "rfu": [550, 510], "is_microvariant": true},
    "PENTA_D": {"alleles": ["9", "12"], "rfu": [920, 890], "is_microvariant": false},
    "PENTA_E": {"alleles": ["7", "14"], "rfu": [810, 780], "is_microvariant": false}
  },
  "audit": {
    "raw_command_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "canonical_state_hash": "5f4dcc3b5aa765d61d8327deb882cf992bda254473b4c130b4e6569f642a1e7e",
    "iso17025_compliant": true
  }
}
VECTOR_CLI_02: Complete 27-Locus Y-FILER Plus Batch Entry (ystr set-batch)CLI Input CommandBashystr set-batch --data "DYS19:14;DYS389I:13;DYS389II:29;DYS390:24;DYS391:11;DYS392:13;DYS393:13;DYS385a/b:11,14;DYS437:15;DYS438:12;DYS439:12;DYS448:19;DYS456:15;DYS458:17;DYS635:23;Y-GATA-H4:12;DYS481:22;DYS533:12;DYS549:12;DYS570:17;DYS576:18;DYS643:10;DYS518:38;DYS627:21;DYS449:30;DYF387S1a/b:35,37;DYS460:11" --mode STRICT
Parsed Canonical State Output (LIMS JSON)JSON{
  "transaction_id": "tx_ystr_a44109f2_20230815",
  "domain": "Y_STR",
  "kit_name": "Yfiler_Plus_27",
  "status": "COMMITTED",
  "execution_mode": "STRICT",
  "loci_count": 27,
  "haplotype": {
    "DYS19": {"alleles": ["14"], "copy_number": 1, "is_rapidly_mutating": false},
    "DYS389I": {"alleles": ["13"], "copy_number": 1, "is_rapidly_mutating": false},
    "DYS389II": {"alleles": ["29"], "copy_number": 1, "is_rapidly_mutating": false},
    "DYS390": {"alleles": ["24"], "copy_number": 1, "is_rapidly_mutating": false},
    "DYS391": {"alleles": ["11"], "copy_number": 1, "is_rapidly_mutating": false},
    "DYS392": {"alleles": ["13"], "copy_number": 1, "is_rapidly_mutating": false},
    "DYS393": {"alleles": ["13"], "copy_number": 1, "is_rapidly_mutating": false},
    "DYS385a/b": {"alleles": ["11", "14"], "copy_number": 2, "is_rapidly_mutating": false},
    "DYS437": {"alleles": ["15"], "copy_number": 1, "is_rapidly_mutating": false},
    "DYS438": {"alleles": ["12"], "copy_number": 1, "is_rapidly_mutating": false},
    "DYS439": {"alleles": ["12"], "copy_number": 1, "is_rapidly_mutating": false},
    "DYS448": {"alleles": ["19"], "copy_number": 1, "is_rapidly_mutating": false},
    "DYS456": {"alleles": ["15"], "copy_number": 1, "is_rapidly_mutating": false},
    "DYS458": {"alleles": ["17"], "copy_number": 1, "is_rapidly_mutating": false},
    "DYS635": {"alleles": ["23"], "copy_number": 1, "is_rapidly_mutating": false},
    "YGATAH4": {"alleles": ["12"], "copy_number": 1, "is_rapidly_mutating": false},
    "DYS481": {"alleles": ["22"], "copy_number": 1, "is_rapidly_mutating": false},
    "DYS533": {"alleles": ["12"], "copy_number": 1, "is_rapidly_mutating": false},
    "DYS549": {"alleles": ["12"], "copy_number": 1, "is_rapidly_mutating": false},
    "DYS570": {"alleles": ["17"], "copy_number": 1, "is_rapidly_mutating": true},
    "DYS576": {"alleles": ["18"], "copy_number": 1, "is_rapidly_mutating": true},
    "DYS643": {"alleles": ["10"], "copy_number": 1, "is_rapidly_mutating": false},
    "DYS518": {"alleles": ["38"], "copy_number": 1, "is_rapidly_mutating": true},
    "DYS627": {"alleles": ["21"], "copy_number": 1, "is_rapidly_mutating": true},
    "DYS449": {"alleles": ["30"], "copy_number": 1, "is_rapidly_mutating": true},
    "DYF387S1a/b": {"alleles": ["35", "37"], "copy_number": 2, "is_rapidly_mutating": true},
    "DYS460": {"alleles": ["11"], "copy_number": 1, "is_rapidly_mutating": false}
  },
  "audit": {
    "raw_command_hash": "7d9b8e11a33b00c99a80e1a123f4581c828d0822183b1238910129bc811a221f",
    "canonical_state_hash": "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b",
    "iso17025_compliant": true
  }
}
VECTOR_CLI_03: Mitochondrial DNA D-Loop Mutation Batch (mtdna set-batch)CLI Input CommandBashmtdna set-batch --data "263G, 315.1C, 524del, 16093Y, 16189R, 16519C" --ref rCRS
Parsed Canonical State Output (LIMS JSON)JSON{
  "transaction_id": "tx_mtdna_c019d882_20230815",
  "domain": "MITOCHONDRIAL_DNA",
  "reference_sequence": "rCRS_NC_012920.1",
  "status": "COMMITTED",
  "variant_count": 6,
  "aligned_variants": [
    {
      "position": 263,
      "reference_base": "A",
      "variant_type": "SUBSTITUTION",
      "call": "G",
      "empop_notation": "263G",
      "is_heteroplasmy": false
    },
    {
      "position": 315,
      "reference_base": "C",
      "variant_type": "INSERTION",
      "inserted_bases": "C",
      "empop_notation": "315.1C",
      "is_heteroplasmy": false
    },
    {
      "position": 524,
      "reference_base": "C",
      "variant_type": "DELETION",
      "empop_notation": "524del",
      "is_heteroplasmy": false
    },
    {
      "position": 16093,
      "reference_base": "T",
      "variant_type": "POINT_HETEROPLASMY",
      "iupac_code": "Y",
      "base_components": ["C", "T"],
      "empop_notation": "16093Y",
      "is_heteroplasmy": true
    },
    {
      "position": 16189,
      "reference_base": "T",
      "variant_type": "POINT_HETEROPLASMY",
      "iupac_code": "R",
      "base_components": ["A", "G"],
      "empop_notation": "16189R",
      "is_heteroplasmy": true
    },
    {
      "position": 16519,
      "reference_base": "T",
      "variant_type": "SUBSTITUTION",
      "call": "C",
      "empop_notation": "16519C",
      "is_heteroplasmy": false
    }
  ],
  "audit": {
    "raw_command_hash": "2f4e3d1a8c7b6a5e4d3c2b1a0f9e8d7c6b5a4e3d2c1b0a9f8e7d6c5b4a3e2d1c",
    "canonical_state_hash": "8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b",
    "iso17025_compliant": true
  }
}
VECTOR_CLI_04: 55-SNP AIM Continental Ancestry Batch Entry (snp set-batch)CLI Input CommandBashsnp set-batch --data "rs12913832:2, rs1805007:1, rs16891982:0, rs1426654:2, rs1042602:1, rs1800404:0, rs28777:2, rs12203592:1"
Parsed Canonical State Output (LIMS JSON)JSON{
  "transaction_id": "tx_snp_aim_55021a_20230815",
  "domain": "SNP_ANCESTRY",
  "panel_name": "Kidd_55_AISNP_Panel",
  "status": "COMMITTED",
  "snp_count": 8,
  "genotypes": {
    "rs12913832": {"dosage": 2, "inferred_genotype": "G/G", "effect_allele": "G"},
    "rs1805007": {"dosage": 1, "inferred_genotype": "C/T", "effect_allele": "T"},
    "rs16891982": {"dosage": 0, "inferred_genotype": "C/C", "effect_allele": "G"},
    "rs1426654": {"dosage": 2, "inferred_genotype": "A/A", "effect_allele": "A"},
    "rs1042602": {"dosage": 1, "inferred_genotype": "C/A", "effect_allele": "A"},
    "rs1800404": {"dosage": 0, "inferred_genotype": "C/C", "effect_allele": "T"},
    "rs28777": {"dosage": 2, "inferred_genotype": "A/A", "effect_allele": "A"},
    "rs12203592": {"dosage": 1, "inferred_genotype": "C/T", "effect_allele": "T"}
  },
  "ancestry_inference_ready": true,
  "audit": {
    "raw_command_hash": "3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b",
    "canonical_state_hash": "9f8e7d6c5b4a3e2d1c0b9a8f7e6d5c4b3a2e1d0c9b8a7f6e5d4c3b2a1e0d9c8b",
    "iso17025_compliant": true
  }
}
VECTOR_CLI_05: 41-SNP HIrisPlex-S Phenotype Batch Entry (snp set-batch)CLI Input CommandBashsnp set-batch --data "rs12913832:G/G, rs1805007:C/T, rs16891982:C/C, rs12203592:C/T, rs1042602:C/A, rs12821256:T/T, rs28777:A/A"
Parsed Canonical State Output (LIMS JSON)JSON{
  "transaction_id": "tx_snp_hip_882910_20230815",
  "domain": "SNP_PHENOTYPE",
  "panel_name": "HIrisPlex_S_41_Panel",
  "status": "COMMITTED",
  "snp_count": 7,
  "phenotype_markers": {
    "rs12913832": {"genotype": "G/G", "target_trait": "EYE_HAIR_SKIN", "derived_dosage": 2},
    "rs1805007": {"genotype": "C/T", "target_trait": "RED_HAIR_SKIN", "derived_dosage": 1},
    "rs16891982": {"genotype": "C/C", "target_trait": "HAIR_SKIN", "derived_dosage": 0},
    "rs12203592": {"genotype": "C/T", "target_trait": "EYE_HAIR_SKIN", "derived_dosage": 1},
    "rs1042602": {"genotype": "C/A", "target_trait": "SKIN_PIGMENTATION", "derived_dosage": 1},
    "rs12821256": {"genotype": "T/T", "target_trait": "BLONDE_HAIR", "derived_dosage": 2},
    "rs28777": {"genotype": "A/A", "target_trait": "SKIN_PIGMENTATION", "derived_dosage": 2}
  },
  "phenotype_prediction_ready": true,
  "audit": {
    "raw_command_hash": "1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d",
    "canonical_state_hash": "7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f",
    "iso17025_compliant": true
  }
}
VECTOR_CLI_06: VISAGE 5-CpG Epigenetic Aging Batch Entry (cpg set-batch)CLI Input CommandBashcpg set-batch --data "ELOVL2:0.42, FHL2:0.38, PENK:0.31, TRIM59:0.33, KLF14:0.28" --tissue BLOOD
Parsed Canonical State Output (LIMS JSON)JSON{
  "transaction_id": "tx_cpg_visage_771029_20230815",
  "domain": "EPIGENETIC_AGE",
  "panel_name": "VISAGE_5_CpG_Core_Clock",
  "status": "COMMITTED",
  "tissue_calibration": "BLOOD",
  "cpg_count": 5,
  "methylation_profile": {
    "ELOVL2": {"beta_fraction": 0.42, "m_value": -0.465, "genomic_target": "cg16867657"},
    "FHL2": {"beta_fraction": 0.38, "m_value": -0.707, "genomic_target": "cg06639320"},
    "PENK": {"beta_fraction": 0.31, "m_value": -1.154, "genomic_target": "cg16537105"},
    "TRIM59": {"beta_fraction": 0.33, "m_value": -1.024, "genomic_target": "cg04523812"},
    "KLF14": {"beta_fraction": 0.28, "m_value": -1.362, "genomic_target": "cg08097417"}
  },
  "age_estimation_model_output": {
    "calibrated_tissue": "BLOOD",
    "predicted_chronological_age_years": 44.8,
    "confidence_interval_95_percent": [41.6, 48.0],
    "mean_absolute_error_years": 3.2
  },
  "audit": {
    "raw_command_hash": "5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b",
    "canonical_state_hash": "2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c",
    "iso17025_compliant": true
  }
}
5. Implementation Workflow for Browser-Native TerminalsDeploying forenza-cli inside web-based LIMS platforms requires a clear operational sequence to isolate browser execution from backend storage.Client-Side Ingestion and Tokenization: The user inputs a command into the browser terminal interface. An isolated WebAssembly (Wasm) parser compiled from Rust or C++ processes the raw string against the formal EBNF grammar rules.Pre-Flight Sanitization: The Wasm module checks locus aliases, verifies decimal suffix configurations, and ensures floating-point values fall within valid ranges (e.g., confirming CpG $\beta \in [0.0, 1.0]$). Commands containing syntax errors are rejected locally before network submission.Server Verification: Valid transactions are serialized to JSON and sent to the LIMS application server over TLS. The server re-evaluates the command using an identical WebAssembly/Native core to protect against client-side tampering.Audit Generation and Persistence: The backend generates cryptographic SHA-256 digests (raw_command_hash and canonical_state_hash) and updates the Merkle tree state. The record is committed to relational SQL storage under ACID guarantees, and an audit confirmation block is returned to update the user terminal interface.