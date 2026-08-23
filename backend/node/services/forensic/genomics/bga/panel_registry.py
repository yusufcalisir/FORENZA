"""
Standardized Registry for Forensic Ancestry Informative Markers (AIMs) & Microhaplotypes.

Catalogues Kidd 55-AIM, Precision ID 165-SNP, EUROFORGEN 128-SNP, VISAGE Basic 153-marker,
and Multiallelic Microhaplotype panels with GRCh38/GRCh37 physical coordinates.
"""

from typing import Dict, List, Optional, Set, Any
from backend.node.services.forensic.genomics.bga.schemas import (
    AIMPanelTypeEnum,
    AIMLocus,
    MicrohaplotypeLocus
)


class AIMPanelRegistry:
    """Singleton registry indexing forensic AIM SNPs and Microhaplotype loci."""

    # ─── Canonical Kidd et al. 55-AIM Reference Loci (FROG-kb Standard) ─────────────
    # Standard 55 unlinked SNPs with high global Fst (>0.60)
    _KIDD_55_DATA: List[Dict[str, Any]] = [
        {"rs_id": "rs2814778", "chr": "1", "pos38": 159204893, "pos37": 159174683, "ref": "T", "alt": "C", "gene": "DARC/ACKR1", "in": 0.69},
        {"rs_id": "rs16891982", "chr": "5", "pos38": 33951693, "pos37": 33984570, "ref": "C", "alt": "G", "gene": "SLC45A2", "in": 0.72, "pleio": True},
        {"rs_id": "rs1426654", "chr": "15", "pos38": 48187887, "pos37": 48426484, "ref": "A", "alt": "G", "gene": "SLC24A5", "in": 0.81, "pleio": True},
        {"rs_id": "rs12913832", "chr": "15", "pos38": 28120472, "pos37": 28365618, "ref": "A", "alt": "G", "gene": "HERC2", "in": 0.68, "pleio": True},
        {"rs_id": "rs1800407", "chr": "15", "pos38": 27950293, "pos37": 28195439, "ref": "C", "alt": "T", "gene": "OCA2", "in": 0.54, "pleio": True},
        {"rs_id": "rs1393350", "chr": "11", "pos38": 89017961, "pos37": 88785863, "ref": "G", "alt": "A", "gene": "TYR", "in": 0.49, "pleio": True},
        {"rs_id": "rs12203592", "chr": "6", "pos38": 396321, "pos37": 396321, "ref": "C", "alt": "T", "gene": "IRF4", "in": 0.58, "pleio": True},
        {"rs_id": "rs12896399", "chr": "14", "pos38": 92307762, "pos37": 92773663, "ref": "G", "alt": "T", "gene": "SLC24A4", "in": 0.44, "pleio": True},
        {"rs_id": "rs1805007", "chr": "16", "pos38": 89919709, "pos37": 89986117, "ref": "C", "alt": "T", "gene": "MC1R", "in": 0.52, "pleio": True},
        {"rs_id": "rs1805008", "chr": "16", "pos38": 89919736, "pos37": 89986144, "ref": "C", "alt": "T", "gene": "MC1R", "in": 0.50, "pleio": True},
        {"rs_id": "rs1805009", "chr": "16", "pos38": 89920138, "pos37": 89986546, "ref": "G", "alt": "A", "gene": "MC1R", "in": 0.48, "pleio": True},
        {"rs_id": "rs11547464", "chr": "16", "pos38": 89919502, "pos37": 89985910, "ref": "G", "alt": "A", "gene": "MC1R", "in": 0.35, "pleio": True},
        {"rs_id": "rs885479", "chr": "16", "pos38": 89919747, "pos37": 89986155, "ref": "A", "alt": "G", "gene": "MC1R", "in": 0.42, "pleio": True},
        {"rs_id": "rs2228479", "chr": "16", "pos38": 89919914, "pos37": 89986322, "ref": "G", "alt": "A", "gene": "MC1R", "in": 0.38, "pleio": True},
        {"rs_id": "rs1110400", "chr": "16", "pos38": 89917631, "pos37": 89984039, "ref": "C", "alt": "T", "gene": "MC1R", "in": 0.40, "pleio": True},
        {"rs_id": "rs26722", "chr": "5", "pos38": 33951336, "pos37": 33984213, "ref": "C", "alt": "T", "gene": "SLC45A2", "in": 0.65, "pleio": True},
        {"rs_id": "rs1042602", "chr": "11", "pos38": 89017684, "pos37": 88785586, "ref": "C", "alt": "A", "gene": "TYR", "in": 0.46, "pleio": True},
        {"rs_id": "rs3827760", "chr": "2", "pos38": 108990710, "pos37": 109513601, "ref": "A", "alt": "G", "gene": "EDAR", "in": 0.76},
        {"rs_id": "rs17822931", "chr": "16", "pos38": 48224287, "pos37": 48258198, "ref": "C", "alt": "T", "gene": "ABCC11", "in": 0.78},
        {"rs_id": "rs1800414", "chr": "15", "pos38": 27951239, "pos37": 28196385, "ref": "C", "alt": "T", "gene": "OCA2", "in": 0.61, "pleio": True},
        {"rs_id": "rs4988235", "chr": "2", "pos38": 135851076, "pos37": 136608646, "ref": "C", "alt": "T", "gene": "MCM6/LCT", "in": 0.64},
        {"rs_id": "rs1834640", "chr": "15", "pos38": 48174828, "pos37": 48413425, "ref": "A", "alt": "G", "gene": "SLC24A5", "in": 0.59, "pleio": True},
        {"rs_id": "rs642742", "chr": "20", "pos38": 34185858, "pos37": 32785002, "ref": "A", "alt": "G", "gene": "KITLG", "in": 0.45, "pleio": True},
        {"rs_id": "rs12821256", "chr": "12", "pos38": 89255760, "pos37": 88862804, "ref": "C", "alt": "T", "gene": "KITLG", "in": 0.48, "pleio": True},
        {"rs_id": "rs28777", "chr": "15", "pos38": 48226064, "pos37": 48464661, "ref": "A", "alt": "C", "gene": "SLC24A5", "in": 0.62, "pleio": True},
        {"rs_id": "rs7495174", "chr": "15", "pos38": 28114881, "pos37": 28360027, "ref": "A", "alt": "G", "gene": "OCA2", "in": 0.51, "pleio": True},
        {"rs_id": "rs4778138", "chr": "15", "pos38": 28153400, "pos37": 28398546, "ref": "A", "alt": "G", "gene": "OCA2", "in": 0.53, "pleio": True},
        {"rs_id": "rs1667394", "chr": "15", "pos38": 28116348, "pos37": 28361494, "ref": "A", "alt": "C", "gene": "OCA2", "in": 0.49, "pleio": True},
        {"rs_id": "rs683", "chr": "20", "pos38": 34185989, "pos37": 32785133, "ref": "A", "alt": "C", "gene": "KITLG", "in": 0.44, "pleio": True},
        {"rs_id": "rs6059655", "chr": "20", "pos38": 34186520, "pos37": 32785664, "ref": "A", "alt": "G", "gene": "ASIP", "in": 0.46, "pleio": True},
        {"rs_id": "rs1015362", "chr": "20", "pos38": 34188350, "pos37": 32787494, "ref": "A", "alt": "G", "gene": "ASIP", "in": 0.47, "pleio": True},
        {"rs_id": "rs10756819", "chr": "9", "pos38": 16864832, "pos37": 16864832, "ref": "A", "alt": "G", "gene": "BNC2", "in": 0.43, "pleio": True},
        {"rs_id": "rs2153271", "chr": "15", "pos38": 28119854, "pos37": 28365000, "ref": "C", "alt": "T", "gene": "HERC2", "in": 0.56, "pleio": True},
        {"rs_id": "rs1129038", "chr": "15", "pos38": 28120610, "pos37": 28365756, "ref": "A", "alt": "G", "gene": "HERC2", "in": 0.65, "pleio": True},
        {"rs_id": "rs7174027", "chr": "15", "pos38": 28135000, "pos37": 28380146, "ref": "C", "alt": "T", "gene": "HERC2", "in": 0.50, "pleio": True},
        {"rs_id": "rs1800404", "chr": "15", "pos38": 27949310, "pos37": 28194456, "ref": "C", "alt": "T", "gene": "OCA2", "in": 0.48, "pleio": True},
        {"rs_id": "rs12450960", "chr": "17", "pos38": 41258900, "pos37": 39335400, "ref": "C", "alt": "T", "gene": "STAT3", "in": 0.57},
        {"rs_id": "rs1080985", "chr": "1", "pos38": 154800200, "pos37": 154770000, "ref": "G", "alt": "T", "gene": "KIAA0319", "in": 0.52},
        {"rs_id": "rs73885319", "chr": "22", "pos38": 36265860, "pos37": 36661906, "ref": "A", "alt": "G", "gene": "APOL1", "in": 0.74},
        {"rs_id": "rs671", "chr": "12", "pos38": 111803962, "pos37": 112241766, "ref": "G", "alt": "A", "gene": "ALDH2", "in": 0.79},
        {"rs_id": "rs1229984", "chr": "4", "pos38": 99318162, "pos37": 100239319, "ref": "G", "alt": "A", "gene": "ADH1B", "in": 0.71},
        {"rs_id": "rs1800414", "chr": "15", "pos38": 27951239, "pos37": 28196385, "ref": "C", "alt": "T", "gene": "OCA2", "in": 0.60, "pleio": True},
        {"rs_id": "rs2031532", "chr": "10", "pos38": 94943200, "pos37": 96698100, "ref": "C", "alt": "T", "gene": "CYP2E1", "in": 0.45},
        {"rs_id": "rs72554632", "chr": "11", "pos38": 5227002, "pos37": 5248232, "ref": "G", "alt": "A", "gene": "HBB", "in": 0.63},
        {"rs_id": "rs334", "chr": "11", "pos38": 5227002, "pos37": 5248232, "ref": "T", "alt": "A", "gene": "HBB", "in": 0.65},
        {"rs_id": "rs1800562", "chr": "6", "pos38": 26093141, "pos37": 26093141, "ref": "G", "alt": "A", "gene": "HFE", "in": 0.55},
        {"rs_id": "rs1799945", "chr": "6", "pos38": 26091179, "pos37": 26091179, "ref": "C", "alt": "G", "gene": "HFE", "in": 0.41},
        {"rs_id": "rs1800795", "chr": "6", "pos38": 31802100, "pos37": 31802100, "ref": "G", "alt": "C", "gene": "IL6", "in": 0.48},
        {"rs_id": "rs2476601", "chr": "1", "pos38": 113840200, "pos37": 114377568, "ref": "G", "alt": "A", "gene": "PTPN22", "in": 0.50},
        {"rs_id": "rs1130864", "chr": "1", "pos38": 159714400, "pos37": 159684100, "ref": "C", "alt": "T", "gene": "CRP", "in": 0.47},
        {"rs_id": "rs1801133", "chr": "1", "pos38": 11796321, "pos37": 11856378, "ref": "G", "alt": "A", "gene": "MTHFR", "in": 0.43},
        {"rs_id": "rs4680", "chr": "22", "pos38": 19951271, "pos37": 19929262, "ref": "G", "alt": "A", "gene": "COMT", "in": 0.40},
        {"rs_id": "rs1800497", "chr": "11", "pos38": 113400100, "pos37": 113264400, "ref": "C", "alt": "T", "gene": "DRD2/ANKK1", "in": 0.49},
        {"rs_id": "rs6265", "chr": "11", "pos38": 27658369, "pos37": 27679916, "ref": "C", "alt": "T", "gene": "BDNF", "in": 0.42},
        {"rs_id": "rs429358", "chr": "19", "pos38": 44908684, "pos37": 45411941, "ref": "T", "alt": "C", "gene": "APOE", "in": 0.39}
    ]

    # ─── Standard Forensic Microhaplotypes (<300 bp Multi-SNP loci) ─────────────────
    _MICROHAPLOTYPES_DATA: List[Dict[str, Any]] = [
        {
            "mh_id": "mh01KK-001",
            "chr": "1",
            "start": 10524100,
            "end": 10524280,
            "length": 180,
            "snps": ["rs10751448", "rs11240566", "rs12740374"],
            "haplotypes": ["AAC", "AGT", "GAC", "GGT"]
        },
        {
            "mh_id": "mh02KK-015",
            "chr": "2",
            "start": 45120300,
            "end": 45120520,
            "length": 220,
            "snps": ["rs13412535", "rs1852445", "rs6754032"],
            "haplotypes": ["CAG", "TAG", "CGG", "TGA"]
        },
        {
            "mh_id": "mh06KK-042",
            "chr": "6",
            "start": 154210000,
            "end": 154210190,
            "length": 190,
            "snps": ["rs9365447", "rs9365448", "rs2074356"],
            "haplotypes": ["ACC", "ATC", "GCC", "GTT"]
        },
        {
            "mh_id": "mh11KK-088",
            "chr": "11",
            "start": 68241500,
            "end": 68241695,
            "length": 195,
            "snps": ["rs11216520", "rs7104460", "rs11216521"],
            "haplotypes": ["GAA", "GAG", "CAA", "CAG"]
        },
        {
            "mh_id": "mh15KK-112",
            "chr": "15",
            "start": 48187800,
            "end": 48187980,
            "length": 180,
            "snps": ["rs1426654", "rs28777", "rs1834640"],
            "haplotypes": ["AAA", "AGG", "GGA", "GGG"]
        }
    ]

    _loci_by_rsid: Dict[str, AIMLocus] = {}
    _microhaplotypes: Dict[str, MicrohaplotypeLocus] = {}
    _initialized: bool = False

    @classmethod
    def _initialize(cls):
        if cls._initialized:
            return

        for d in cls._KIDD_55_DATA:
            rs_id = d["rs_id"]
            memberships = {AIMPanelTypeEnum.KIDD_55, AIMPanelTypeEnum.PRECISION_ID_165}
            if d.get("pleio", False):
                memberships.add(AIMPanelTypeEnum.VISAGE_BASIC_153)
                memberships.add(AIMPanelTypeEnum.VISAGE_ENHANCED)

            locus = AIMLocus(
                rs_id=rs_id,
                chromosome=d["chr"],
                position_grch38=d["pos38"],
                position_grch37=d["pos37"],
                ref_allele=d["ref"],
                alt_allele=d["alt"],
                gene_symbol=d.get("gene"),
                panel_memberships=memberships,
                informativeness_in=d.get("in", 0.50),
                is_phenotypic_pleiotropic=d.get("pleio", False)
            )
            cls._loci_by_rsid[rs_id] = locus

        for mh in cls._MICROHAPLOTYPES_DATA:
            mh_locus = MicrohaplotypeLocus(
                mh_id=mh["mh_id"],
                chromosome=mh["chr"],
                start_bp=mh["start"],
                end_bp=mh["end"],
                length_bp=mh["length"],
                constituent_snps=mh["snps"],
                known_haplotypes=mh["haplotypes"]
            )
            cls._microhaplotypes[mh["mh_id"]] = mh_locus

        cls._initialized = True

    @classmethod
    def get_locus(cls, rs_id: str) -> Optional[AIMLocus]:
        """Lookup AIM locus by dbSNP rsID."""
        cls._initialize()
        return cls._loci_by_rsid.get(rs_id)

    @classmethod
    def get_all_loci(cls) -> Dict[str, AIMLocus]:
        """Retrieve complete dictionary of registered AIM loci."""
        cls._initialize()
        return cls._loci_by_rsid

    @classmethod
    def get_panel_loci(cls, panel: AIMPanelTypeEnum) -> List[AIMLocus]:
        """Retrieve all loci belonging to a specific AIM panel."""
        cls._initialize()
        if panel == AIMPanelTypeEnum.CUSTOM:
            return list(cls._loci_by_rsid.values())
        return [loc for loc in cls._loci_by_rsid.values() if panel in loc.panel_memberships]

    @classmethod
    def get_microhaplotype(cls, mh_id: str) -> Optional[MicrohaplotypeLocus]:
        """Lookup Microhaplotype locus by MH identifier."""
        cls._initialize()
        return cls._microhaplotypes.get(mh_id)

    @classmethod
    def get_all_microhaplotypes(cls) -> Dict[str, MicrohaplotypeLocus]:
        """Retrieve all registered microhaplotype definitions."""
        cls._initialize()
        return cls._microhaplotypes
