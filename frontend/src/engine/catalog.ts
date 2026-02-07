/**
 * Benefits Catalog Loader
 * Loads and manages the benefits catalog from JSON files
 */

import { Benefit, BenefitCatalog, BRAZILIAN_STATES } from './types';

// Import federal benefits
import federalData from '../data/benefits/federal.json';
import sectoralData from '../data/benefits/sectoral.json';

// Import state benefits - explicit imports
import stateAC from '../data/benefits/states/ac.json';
import stateAL from '../data/benefits/states/al.json';
import stateAM from '../data/benefits/states/am.json';
import stateAP from '../data/benefits/states/ap.json';
import stateBA from '../data/benefits/states/ba.json';
import stateCE from '../data/benefits/states/ce.json';
import stateDF from '../data/benefits/states/df.json';
import stateES from '../data/benefits/states/es.json';
import stateGO from '../data/benefits/states/go.json';
import stateMA from '../data/benefits/states/ma.json';
import stateMG from '../data/benefits/states/mg.json';
import stateMS from '../data/benefits/states/ms.json';
import stateMT from '../data/benefits/states/mt.json';
import statePA from '../data/benefits/states/pa.json';
import statePB from '../data/benefits/states/pb.json';
import statePE from '../data/benefits/states/pe.json';
import statePI from '../data/benefits/states/pi.json';
import statePR from '../data/benefits/states/pr.json';
import stateRJ from '../data/benefits/states/rj.json';
import stateRN from '../data/benefits/states/rn.json';
import stateRO from '../data/benefits/states/ro.json';
import stateRR from '../data/benefits/states/rr.json';
import stateRS from '../data/benefits/states/rs.json';
import stateSC from '../data/benefits/states/sc.json';
import stateSE from '../data/benefits/states/se.json';
import stateSP from '../data/benefits/states/sp.json';
import stateTO from '../data/benefits/states/to.json';

const stateModules: Record<string, { benefits: Benefit[] }> = {
  AC: stateAC as unknown as { benefits: Benefit[] },
  AL: stateAL as unknown as { benefits: Benefit[] },
  AM: stateAM as unknown as { benefits: Benefit[] },
  AP: stateAP as unknown as { benefits: Benefit[] },
  BA: stateBA as unknown as { benefits: Benefit[] },
  CE: stateCE as unknown as { benefits: Benefit[] },
  DF: stateDF as unknown as { benefits: Benefit[] },
  ES: stateES as unknown as { benefits: Benefit[] },
  GO: stateGO as unknown as { benefits: Benefit[] },
  MA: stateMA as unknown as { benefits: Benefit[] },
  MG: stateMG as unknown as { benefits: Benefit[] },
  MS: stateMS as unknown as { benefits: Benefit[] },
  MT: stateMT as unknown as { benefits: Benefit[] },
  PA: statePA as unknown as { benefits: Benefit[] },
  PB: statePB as unknown as { benefits: Benefit[] },
  PE: statePE as unknown as { benefits: Benefit[] },
  PI: statePI as unknown as { benefits: Benefit[] },
  PR: statePR as unknown as { benefits: Benefit[] },
  RJ: stateRJ as unknown as { benefits: Benefit[] },
  RN: stateRN as unknown as { benefits: Benefit[] },
  RO: stateRO as unknown as { benefits: Benefit[] },
  RR: stateRR as unknown as { benefits: Benefit[] },
  RS: stateRS as unknown as { benefits: Benefit[] },
  SC: stateSC as unknown as { benefits: Benefit[] },
  SE: stateSE as unknown as { benefits: Benefit[] },
  SP: stateSP as unknown as { benefits: Benefit[] },
  TO: stateTO as unknown as { benefits: Benefit[] },
};

// Import municipal benefits - explicit imports (98 municipalities)
import mun1100205 from '../data/benefits/municipalities/1100205.json';
import mun1200401 from '../data/benefits/municipalities/1200401.json';
import mun1302603 from '../data/benefits/municipalities/1302603.json';
import mun1400100 from '../data/benefits/municipalities/1400100.json';
import mun1500800 from '../data/benefits/municipalities/1500800.json';
import mun1501402 from '../data/benefits/municipalities/1501402.json';
import mun1506807 from '../data/benefits/municipalities/1506807.json';
import mun1600303 from '../data/benefits/municipalities/1600303.json';
import mun1721000 from '../data/benefits/municipalities/1721000.json';
import mun2105302 from '../data/benefits/municipalities/2105302.json';
import mun2111300 from '../data/benefits/municipalities/2111300.json';
import mun2211001 from '../data/benefits/municipalities/2211001.json';
import mun2303709 from '../data/benefits/municipalities/2303709.json';
import mun2304400 from '../data/benefits/municipalities/2304400.json';
import mun2312908 from '../data/benefits/municipalities/2312908.json';
import mun2408102 from '../data/benefits/municipalities/2408102.json';
import mun2504009 from '../data/benefits/municipalities/2504009.json';
import mun2507507 from '../data/benefits/municipalities/2507507.json';
import mun2604106 from '../data/benefits/municipalities/2604106.json';
import mun2607901 from '../data/benefits/municipalities/2607901.json';
import mun2609600 from '../data/benefits/municipalities/2609600.json';
import mun2611101 from '../data/benefits/municipalities/2611101.json';
import mun2611606 from '../data/benefits/municipalities/2611606.json';
import mun2704302 from '../data/benefits/municipalities/2704302.json';
import mun2800308 from '../data/benefits/municipalities/2800308.json';
import mun2910800 from '../data/benefits/municipalities/2910800.json';
import mun2927408 from '../data/benefits/municipalities/2927408.json';
import mun3106200 from '../data/benefits/municipalities/3106200.json';
import mun3106705 from '../data/benefits/municipalities/3106705.json';
import mun3118601 from '../data/benefits/municipalities/3118601.json';
import mun3127701 from '../data/benefits/municipalities/3127701.json';
import mun3131307 from '../data/benefits/municipalities/3131307.json';
import mun3136702 from '../data/benefits/municipalities/3136702.json';
import mun3143302 from '../data/benefits/municipalities/3143302.json';
import mun3153905 from '../data/benefits/municipalities/3153905.json';
import mun3170107 from '../data/benefits/municipalities/3170107.json';
import mun3170206 from '../data/benefits/municipalities/3170206.json';
import mun3201308 from '../data/benefits/municipalities/3201308.json';
import mun3205002 from '../data/benefits/municipalities/3205002.json';
import mun3205200 from '../data/benefits/municipalities/3205200.json';
import mun3205309 from '../data/benefits/municipalities/3205309.json';
import mun3300456 from '../data/benefits/municipalities/3300456.json';
import mun3301009 from '../data/benefits/municipalities/3301009.json';
import mun3301702 from '../data/benefits/municipalities/3301702.json';
import mun3303302 from '../data/benefits/municipalities/3303302.json';
import mun3303500 from '../data/benefits/municipalities/3303500.json';
import mun3303906 from '../data/benefits/municipalities/3303906.json';
import mun3304557 from '../data/benefits/municipalities/3304557.json';
import mun3304904 from '../data/benefits/municipalities/3304904.json';
import mun3305109 from '../data/benefits/municipalities/3305109.json';
import mun3306305 from '../data/benefits/municipalities/3306305.json';
import mun3506003 from '../data/benefits/municipalities/3506003.json';
import mun3509502 from '../data/benefits/municipalities/3509502.json';
import mun3510609 from '../data/benefits/municipalities/3510609.json';
import mun3513801 from '../data/benefits/municipalities/3513801.json';
import mun3516200 from '../data/benefits/municipalities/3516200.json';
import mun3518701 from '../data/benefits/municipalities/3518701.json';
import mun3518800 from '../data/benefits/municipalities/3518800.json';
import mun3523107 from '../data/benefits/municipalities/3523107.json';
import mun3525904 from '../data/benefits/municipalities/3525904.json';
import mun3529401 from '../data/benefits/municipalities/3529401.json';
import mun3530607 from '../data/benefits/municipalities/3530607.json';
import mun3534401 from '../data/benefits/municipalities/3534401.json';
import mun3538709 from '../data/benefits/municipalities/3538709.json';
import mun3541000 from '../data/benefits/municipalities/3541000.json';
import mun3543402 from '../data/benefits/municipalities/3543402.json';
import mun3547809 from '../data/benefits/municipalities/3547809.json';
import mun3548708 from '../data/benefits/municipalities/3548708.json';
import mun3549805 from '../data/benefits/municipalities/3549805.json';
import mun3549904 from '../data/benefits/municipalities/3549904.json';
import mun3550308 from '../data/benefits/municipalities/3550308.json';
import mun3552205 from '../data/benefits/municipalities/3552205.json';
import mun3554102 from '../data/benefits/municipalities/3554102.json';
import mun4104808 from '../data/benefits/municipalities/4104808.json';
import mun4105805 from '../data/benefits/municipalities/4105805.json';
import mun4106902 from '../data/benefits/municipalities/4106902.json';
import mun4113700 from '../data/benefits/municipalities/4113700.json';
import mun4115200 from '../data/benefits/municipalities/4115200.json';
import mun4119905 from '../data/benefits/municipalities/4119905.json';
import mun4125506 from '../data/benefits/municipalities/4125506.json';
import mun4202404 from '../data/benefits/municipalities/4202404.json';
import mun4205407 from '../data/benefits/municipalities/4205407.json';
import mun4208203 from '../data/benefits/municipalities/4208203.json';
import mun4209102 from '../data/benefits/municipalities/4209102.json';
import mun4209300 from '../data/benefits/municipalities/4209300.json';
import mun4304606 from '../data/benefits/municipalities/4304606.json';
import mun4305108 from '../data/benefits/municipalities/4305108.json';
import mun4309209 from '../data/benefits/municipalities/4309209.json';
import mun4314407 from '../data/benefits/municipalities/4314407.json';
import mun4314902 from '../data/benefits/municipalities/4314902.json';
import mun5002704 from '../data/benefits/municipalities/5002704.json';
import mun5003702 from '../data/benefits/municipalities/5003702.json';
import mun5103403 from '../data/benefits/municipalities/5103403.json';
import mun5108402 from '../data/benefits/municipalities/5108402.json';
import mun5201108 from '../data/benefits/municipalities/5201108.json';
import mun5201405 from '../data/benefits/municipalities/5201405.json';
import mun5208707 from '../data/benefits/municipalities/5208707.json';
import mun5300108 from '../data/benefits/municipalities/5300108.json';

// Phase E — 50 new cities for regional balance
// Norte (8)
import mun1504208 from '../data/benefits/municipalities/1504208.json';
import mun1502400 from '../data/benefits/municipalities/1502400.json';
import mun1303403 from '../data/benefits/municipalities/1303403.json';
import mun1301902 from '../data/benefits/municipalities/1301902.json';
import mun1100122 from '../data/benefits/municipalities/1100122.json';
import mun1100023 from '../data/benefits/municipalities/1100023.json';
import mun1702109 from '../data/benefits/municipalities/1702109.json';
import mun1200203 from '../data/benefits/municipalities/1200203.json';
// Nordeste (18)
import mun2700300 from '../data/benefits/municipalities/2700300.json';
import mun2408003 from '../data/benefits/municipalities/2408003.json';
import mun2403251 from '../data/benefits/municipalities/2403251.json';
import mun2933307 from '../data/benefits/municipalities/2933307.json';
import mun2913606 from '../data/benefits/municipalities/2913606.json';
import mun2918407 from '../data/benefits/municipalities/2918407.json';
import mun2207702 from '../data/benefits/municipalities/2207702.json';
import mun2304202 from '../data/benefits/municipalities/2304202.json';
import mun2307304 from '../data/benefits/municipalities/2307304.json';
import mun2307650 from '../data/benefits/municipalities/2307650.json';
import mun2112209 from '../data/benefits/municipalities/2112209.json';
import mun2103307 from '../data/benefits/municipalities/2103307.json';
import mun2513703 from '../data/benefits/municipalities/2513703.json';
import mun2804805 from '../data/benefits/municipalities/2804805.json';
import mun2606002 from '../data/benefits/municipalities/2606002.json';
import mun2616407 from '../data/benefits/municipalities/2616407.json';
import mun2610707 from '../data/benefits/municipalities/2610707.json';
import mun2602902 from '../data/benefits/municipalities/2602902.json';
// Centro-Oeste (6)
import mun5212501 from '../data/benefits/municipalities/5212501.json';
import mun5218805 from '../data/benefits/municipalities/5218805.json';
import mun5200258 from '../data/benefits/municipalities/5200258.json';
import mun5107602 from '../data/benefits/municipalities/5107602.json';
import mun5107909 from '../data/benefits/municipalities/5107909.json';
import mun5008305 from '../data/benefits/municipalities/5008305.json';
// Sudeste (10)
import mun3201209 from '../data/benefits/municipalities/3201209.json';
import mun3203205 from '../data/benefits/municipalities/3203205.json';
import mun3167202 from '../data/benefits/municipalities/3167202.json';
import mun3122306 from '../data/benefits/municipalities/3122306.json';
import mun3151800 from '../data/benefits/municipalities/3151800.json';
import mun3305802 from '../data/benefits/municipalities/3305802.json';
import mun3300704 from '../data/benefits/municipalities/3300704.json';
import mun3526902 from '../data/benefits/municipalities/3526902.json';
import mun3552403 from '../data/benefits/municipalities/3552403.json';
import mun3520509 from '../data/benefits/municipalities/3520509.json';
// Sul (8)
import mun4108304 from '../data/benefits/municipalities/4108304.json';
import mun4109401 from '../data/benefits/municipalities/4109401.json';
import mun4118204 from '../data/benefits/municipalities/4118204.json';
import mun4316907 from '../data/benefits/municipalities/4316907.json';
import mun4315602 from '../data/benefits/municipalities/4315602.json';
import mun4313409 from '../data/benefits/municipalities/4313409.json';
import mun4204202 from '../data/benefits/municipalities/4204202.json';
import mun4204608 from '../data/benefits/municipalities/4204608.json';

// Phase I — 50 new cities (mega-expansion)
// Norte (6)
import mun1101002 from '../data/benefits/municipalities/1101002.json';
import mun1303569 from '../data/benefits/municipalities/1303569.json';
import mun1304062 from '../data/benefits/municipalities/1304062.json';
import mun1500602 from '../data/benefits/municipalities/1500602.json';
import mun1505031 from '../data/benefits/municipalities/1505031.json';
import mun1505536 from '../data/benefits/municipalities/1505536.json';
import mun1600501 from '../data/benefits/municipalities/1600501.json';
// Nordeste (14)
import mun2101400 from '../data/benefits/municipalities/2101400.json';
import mun2211209 from '../data/benefits/municipalities/2211209.json';
import mun2301000 from '../data/benefits/municipalities/2301000.json';
import mun2504405 from '../data/benefits/municipalities/2504405.json';
import mun2800605 from '../data/benefits/municipalities/2800605.json';
import mun2903201 from '../data/benefits/municipalities/2903201.json';
import mun2907400 from '../data/benefits/municipalities/2907400.json';
import mun2910727 from '../data/benefits/municipalities/2910727.json';
import mun2917359 from '../data/benefits/municipalities/2917359.json';
import mun2919207 from '../data/benefits/municipalities/2919207.json';
import mun2919504 from '../data/benefits/municipalities/2919504.json';
import mun2919553 from '../data/benefits/municipalities/2919553.json';
import mun2924009 from '../data/benefits/municipalities/2924009.json';
import mun2928703 from '../data/benefits/municipalities/2928703.json';
import mun2929206 from '../data/benefits/municipalities/2929206.json';
// Centro-Oeste (5)
import mun5002951 from '../data/benefits/municipalities/5002951.json';
import mun5106422 from '../data/benefits/municipalities/5106422.json';
import mun5208004 from '../data/benefits/municipalities/5208004.json';
import mun5211602 from '../data/benefits/municipalities/5211602.json';
import mun5211909 from '../data/benefits/municipalities/5211909.json';
// Sudeste (10)
import mun3105608 from '../data/benefits/municipalities/3105608.json';
import mun3132404 from '../data/benefits/municipalities/3132404.json';
import mun3148004 from '../data/benefits/municipalities/3148004.json';
import mun3300100 from '../data/benefits/municipalities/3300100.json';
import mun3301900 from '../data/benefits/municipalities/3301900.json';
import mun3302502 from '../data/benefits/municipalities/3302502.json';
import mun3303609 from '../data/benefits/municipalities/3303609.json';
import mun3503002 from '../data/benefits/municipalities/3503002.json';
import mun3503208 from '../data/benefits/municipalities/3503208.json';
import mun3507605 from '../data/benefits/municipalities/3507605.json';
import mun3529005 from '../data/benefits/municipalities/3529005.json';
import mun3548500 from '../data/benefits/municipalities/3548500.json';
// Sul (12)
import mun4101408 from '../data/benefits/municipalities/4101408.json';
import mun4101507 from '../data/benefits/municipalities/4101507.json';
import mun4104907 from '../data/benefits/municipalities/4104907.json';
import mun4119509 from '../data/benefits/municipalities/4119509.json';
import mun4127700 from '../data/benefits/municipalities/4127700.json';
import mun4202909 from '../data/benefits/municipalities/4202909.json';
import mun4215802 from '../data/benefits/municipalities/4215802.json';
import mun4218202 from '../data/benefits/municipalities/4218202.json';
import mun4302105 from '../data/benefits/municipalities/4302105.json';
import mun4310207 from '../data/benefits/municipalities/4310207.json';
import mun4317608 from '../data/benefits/municipalities/4317608.json';

const municipalModules: Record<string, { benefits: Benefit[] }> = {
  '1100205': mun1100205 as unknown as { benefits: Benefit[] },
  '1200401': mun1200401 as unknown as { benefits: Benefit[] },
  '1302603': mun1302603 as unknown as { benefits: Benefit[] },
  '1400100': mun1400100 as unknown as { benefits: Benefit[] },
  '1500800': mun1500800 as unknown as { benefits: Benefit[] },
  '1501402': mun1501402 as unknown as { benefits: Benefit[] },
  '1506807': mun1506807 as unknown as { benefits: Benefit[] },
  '1600303': mun1600303 as unknown as { benefits: Benefit[] },
  '1721000': mun1721000 as unknown as { benefits: Benefit[] },
  '2105302': mun2105302 as unknown as { benefits: Benefit[] },
  '2111300': mun2111300 as unknown as { benefits: Benefit[] },
  '2211001': mun2211001 as unknown as { benefits: Benefit[] },
  '2303709': mun2303709 as unknown as { benefits: Benefit[] },
  '2304400': mun2304400 as unknown as { benefits: Benefit[] },
  '2312908': mun2312908 as unknown as { benefits: Benefit[] },
  '2408102': mun2408102 as unknown as { benefits: Benefit[] },
  '2504009': mun2504009 as unknown as { benefits: Benefit[] },
  '2507507': mun2507507 as unknown as { benefits: Benefit[] },
  '2604106': mun2604106 as unknown as { benefits: Benefit[] },
  '2607901': mun2607901 as unknown as { benefits: Benefit[] },
  '2609600': mun2609600 as unknown as { benefits: Benefit[] },
  '2611101': mun2611101 as unknown as { benefits: Benefit[] },
  '2611606': mun2611606 as unknown as { benefits: Benefit[] },
  '2704302': mun2704302 as unknown as { benefits: Benefit[] },
  '2800308': mun2800308 as unknown as { benefits: Benefit[] },
  '2910800': mun2910800 as unknown as { benefits: Benefit[] },
  '2927408': mun2927408 as unknown as { benefits: Benefit[] },
  '3106200': mun3106200 as unknown as { benefits: Benefit[] },
  '3106705': mun3106705 as unknown as { benefits: Benefit[] },
  '3118601': mun3118601 as unknown as { benefits: Benefit[] },
  '3127701': mun3127701 as unknown as { benefits: Benefit[] },
  '3131307': mun3131307 as unknown as { benefits: Benefit[] },
  '3136702': mun3136702 as unknown as { benefits: Benefit[] },
  '3143302': mun3143302 as unknown as { benefits: Benefit[] },
  '3153905': mun3153905 as unknown as { benefits: Benefit[] },
  '3170107': mun3170107 as unknown as { benefits: Benefit[] },
  '3170206': mun3170206 as unknown as { benefits: Benefit[] },
  '3201308': mun3201308 as unknown as { benefits: Benefit[] },
  '3205002': mun3205002 as unknown as { benefits: Benefit[] },
  '3205200': mun3205200 as unknown as { benefits: Benefit[] },
  '3205309': mun3205309 as unknown as { benefits: Benefit[] },
  '3300456': mun3300456 as unknown as { benefits: Benefit[] },
  '3301009': mun3301009 as unknown as { benefits: Benefit[] },
  '3301702': mun3301702 as unknown as { benefits: Benefit[] },
  '3303302': mun3303302 as unknown as { benefits: Benefit[] },
  '3303500': mun3303500 as unknown as { benefits: Benefit[] },
  '3303906': mun3303906 as unknown as { benefits: Benefit[] },
  '3304557': mun3304557 as unknown as { benefits: Benefit[] },
  '3304904': mun3304904 as unknown as { benefits: Benefit[] },
  '3305109': mun3305109 as unknown as { benefits: Benefit[] },
  '3306305': mun3306305 as unknown as { benefits: Benefit[] },
  '3506003': mun3506003 as unknown as { benefits: Benefit[] },
  '3509502': mun3509502 as unknown as { benefits: Benefit[] },
  '3510609': mun3510609 as unknown as { benefits: Benefit[] },
  '3513801': mun3513801 as unknown as { benefits: Benefit[] },
  '3516200': mun3516200 as unknown as { benefits: Benefit[] },
  '3518701': mun3518701 as unknown as { benefits: Benefit[] },
  '3518800': mun3518800 as unknown as { benefits: Benefit[] },
  '3523107': mun3523107 as unknown as { benefits: Benefit[] },
  '3525904': mun3525904 as unknown as { benefits: Benefit[] },
  '3529401': mun3529401 as unknown as { benefits: Benefit[] },
  '3530607': mun3530607 as unknown as { benefits: Benefit[] },
  '3534401': mun3534401 as unknown as { benefits: Benefit[] },
  '3538709': mun3538709 as unknown as { benefits: Benefit[] },
  '3541000': mun3541000 as unknown as { benefits: Benefit[] },
  '3543402': mun3543402 as unknown as { benefits: Benefit[] },
  '3547809': mun3547809 as unknown as { benefits: Benefit[] },
  '3548708': mun3548708 as unknown as { benefits: Benefit[] },
  '3549805': mun3549805 as unknown as { benefits: Benefit[] },
  '3549904': mun3549904 as unknown as { benefits: Benefit[] },
  '3550308': mun3550308 as unknown as { benefits: Benefit[] },
  '3552205': mun3552205 as unknown as { benefits: Benefit[] },
  '3554102': mun3554102 as unknown as { benefits: Benefit[] },
  '4104808': mun4104808 as unknown as { benefits: Benefit[] },
  '4105805': mun4105805 as unknown as { benefits: Benefit[] },
  '4106902': mun4106902 as unknown as { benefits: Benefit[] },
  '4113700': mun4113700 as unknown as { benefits: Benefit[] },
  '4115200': mun4115200 as unknown as { benefits: Benefit[] },
  '4119905': mun4119905 as unknown as { benefits: Benefit[] },
  '4125506': mun4125506 as unknown as { benefits: Benefit[] },
  '4202404': mun4202404 as unknown as { benefits: Benefit[] },
  '4205407': mun4205407 as unknown as { benefits: Benefit[] },
  '4208203': mun4208203 as unknown as { benefits: Benefit[] },
  '4209102': mun4209102 as unknown as { benefits: Benefit[] },
  '4209300': mun4209300 as unknown as { benefits: Benefit[] },
  '4304606': mun4304606 as unknown as { benefits: Benefit[] },
  '4305108': mun4305108 as unknown as { benefits: Benefit[] },
  '4309209': mun4309209 as unknown as { benefits: Benefit[] },
  '4314407': mun4314407 as unknown as { benefits: Benefit[] },
  '4314902': mun4314902 as unknown as { benefits: Benefit[] },
  '5002704': mun5002704 as unknown as { benefits: Benefit[] },
  '5003702': mun5003702 as unknown as { benefits: Benefit[] },
  '5103403': mun5103403 as unknown as { benefits: Benefit[] },
  '5108402': mun5108402 as unknown as { benefits: Benefit[] },
  '5201108': mun5201108 as unknown as { benefits: Benefit[] },
  '5201405': mun5201405 as unknown as { benefits: Benefit[] },
  '5208707': mun5208707 as unknown as { benefits: Benefit[] },
  '5300108': mun5300108 as unknown as { benefits: Benefit[] },
  // Phase E — 50 new cities
  // Norte (8)
  '1504208': mun1504208 as unknown as { benefits: Benefit[] },
  '1502400': mun1502400 as unknown as { benefits: Benefit[] },
  '1303403': mun1303403 as unknown as { benefits: Benefit[] },
  '1301902': mun1301902 as unknown as { benefits: Benefit[] },
  '1100122': mun1100122 as unknown as { benefits: Benefit[] },
  '1100023': mun1100023 as unknown as { benefits: Benefit[] },
  '1702109': mun1702109 as unknown as { benefits: Benefit[] },
  '1200203': mun1200203 as unknown as { benefits: Benefit[] },
  // Nordeste (18)
  '2700300': mun2700300 as unknown as { benefits: Benefit[] },
  '2408003': mun2408003 as unknown as { benefits: Benefit[] },
  '2403251': mun2403251 as unknown as { benefits: Benefit[] },
  '2933307': mun2933307 as unknown as { benefits: Benefit[] },
  '2913606': mun2913606 as unknown as { benefits: Benefit[] },
  '2918407': mun2918407 as unknown as { benefits: Benefit[] },
  '2207702': mun2207702 as unknown as { benefits: Benefit[] },
  '2304202': mun2304202 as unknown as { benefits: Benefit[] },
  '2307304': mun2307304 as unknown as { benefits: Benefit[] },
  '2307650': mun2307650 as unknown as { benefits: Benefit[] },
  '2112209': mun2112209 as unknown as { benefits: Benefit[] },
  '2103307': mun2103307 as unknown as { benefits: Benefit[] },
  '2513703': mun2513703 as unknown as { benefits: Benefit[] },
  '2804805': mun2804805 as unknown as { benefits: Benefit[] },
  '2606002': mun2606002 as unknown as { benefits: Benefit[] },
  '2616407': mun2616407 as unknown as { benefits: Benefit[] },
  '2610707': mun2610707 as unknown as { benefits: Benefit[] },
  '2602902': mun2602902 as unknown as { benefits: Benefit[] },
  // Centro-Oeste (6)
  '5212501': mun5212501 as unknown as { benefits: Benefit[] },
  '5218805': mun5218805 as unknown as { benefits: Benefit[] },
  '5200258': mun5200258 as unknown as { benefits: Benefit[] },
  '5107602': mun5107602 as unknown as { benefits: Benefit[] },
  '5107909': mun5107909 as unknown as { benefits: Benefit[] },
  '5008305': mun5008305 as unknown as { benefits: Benefit[] },
  // Sudeste (10)
  '3201209': mun3201209 as unknown as { benefits: Benefit[] },
  '3203205': mun3203205 as unknown as { benefits: Benefit[] },
  '3167202': mun3167202 as unknown as { benefits: Benefit[] },
  '3122306': mun3122306 as unknown as { benefits: Benefit[] },
  '3151800': mun3151800 as unknown as { benefits: Benefit[] },
  '3305802': mun3305802 as unknown as { benefits: Benefit[] },
  '3300704': mun3300704 as unknown as { benefits: Benefit[] },
  '3526902': mun3526902 as unknown as { benefits: Benefit[] },
  '3552403': mun3552403 as unknown as { benefits: Benefit[] },
  '3520509': mun3520509 as unknown as { benefits: Benefit[] },
  // Sul (8)
  '4108304': mun4108304 as unknown as { benefits: Benefit[] },
  '4109401': mun4109401 as unknown as { benefits: Benefit[] },
  '4118204': mun4118204 as unknown as { benefits: Benefit[] },
  '4316907': mun4316907 as unknown as { benefits: Benefit[] },
  '4315602': mun4315602 as unknown as { benefits: Benefit[] },
  '4313409': mun4313409 as unknown as { benefits: Benefit[] },
  '4204202': mun4204202 as unknown as { benefits: Benefit[] },
  '4204608': mun4204608 as unknown as { benefits: Benefit[] },
  // Phase I — 50 new cities (mega-expansion)
  // Norte (7)
  '1101002': mun1101002 as unknown as { benefits: Benefit[] },
  '1303569': mun1303569 as unknown as { benefits: Benefit[] },
  '1304062': mun1304062 as unknown as { benefits: Benefit[] },
  '1500602': mun1500602 as unknown as { benefits: Benefit[] },
  '1505031': mun1505031 as unknown as { benefits: Benefit[] },
  '1505536': mun1505536 as unknown as { benefits: Benefit[] },
  '1600501': mun1600501 as unknown as { benefits: Benefit[] },
  // Nordeste (15)
  '2101400': mun2101400 as unknown as { benefits: Benefit[] },
  '2211209': mun2211209 as unknown as { benefits: Benefit[] },
  '2301000': mun2301000 as unknown as { benefits: Benefit[] },
  '2504405': mun2504405 as unknown as { benefits: Benefit[] },
  '2800605': mun2800605 as unknown as { benefits: Benefit[] },
  '2903201': mun2903201 as unknown as { benefits: Benefit[] },
  '2907400': mun2907400 as unknown as { benefits: Benefit[] },
  '2910727': mun2910727 as unknown as { benefits: Benefit[] },
  '2917359': mun2917359 as unknown as { benefits: Benefit[] },
  '2919207': mun2919207 as unknown as { benefits: Benefit[] },
  '2919504': mun2919504 as unknown as { benefits: Benefit[] },
  '2919553': mun2919553 as unknown as { benefits: Benefit[] },
  '2924009': mun2924009 as unknown as { benefits: Benefit[] },
  '2928703': mun2928703 as unknown as { benefits: Benefit[] },
  '2929206': mun2929206 as unknown as { benefits: Benefit[] },
  // Centro-Oeste (5)
  '5002951': mun5002951 as unknown as { benefits: Benefit[] },
  '5106422': mun5106422 as unknown as { benefits: Benefit[] },
  '5208004': mun5208004 as unknown as { benefits: Benefit[] },
  '5211602': mun5211602 as unknown as { benefits: Benefit[] },
  '5211909': mun5211909 as unknown as { benefits: Benefit[] },
  // Sudeste (12)
  '3105608': mun3105608 as unknown as { benefits: Benefit[] },
  '3132404': mun3132404 as unknown as { benefits: Benefit[] },
  '3148004': mun3148004 as unknown as { benefits: Benefit[] },
  '3300100': mun3300100 as unknown as { benefits: Benefit[] },
  '3301900': mun3301900 as unknown as { benefits: Benefit[] },
  '3302502': mun3302502 as unknown as { benefits: Benefit[] },
  '3303609': mun3303609 as unknown as { benefits: Benefit[] },
  '3503002': mun3503002 as unknown as { benefits: Benefit[] },
  '3503208': mun3503208 as unknown as { benefits: Benefit[] },
  '3507605': mun3507605 as unknown as { benefits: Benefit[] },
  '3529005': mun3529005 as unknown as { benefits: Benefit[] },
  '3548500': mun3548500 as unknown as { benefits: Benefit[] },
  // Sul (11)
  '4101408': mun4101408 as unknown as { benefits: Benefit[] },
  '4101507': mun4101507 as unknown as { benefits: Benefit[] },
  '4104907': mun4104907 as unknown as { benefits: Benefit[] },
  '4119509': mun4119509 as unknown as { benefits: Benefit[] },
  '4127700': mun4127700 as unknown as { benefits: Benefit[] },
  '4202909': mun4202909 as unknown as { benefits: Benefit[] },
  '4215802': mun4215802 as unknown as { benefits: Benefit[] },
  '4218202': mun4218202 as unknown as { benefits: Benefit[] },
  '4302105': mun4302105 as unknown as { benefits: Benefit[] },
  '4310207': mun4310207 as unknown as { benefits: Benefit[] },
  '4317608': mun4317608 as unknown as { benefits: Benefit[] },
};

/**
 * Load all benefits from the catalog
 */
export function loadBenefitsCatalog(): BenefitCatalog {
  // Load federal benefits
  const federal = (federalData as { benefits: Benefit[] }).benefits;

  // Load sectoral benefits
  const sectoral = (sectoralData as { benefits: Benefit[] }).benefits;

  // Load state benefits
  const states: Record<string, Benefit[]> = {};

  for (const [stateCode, stateData] of Object.entries(stateModules)) {
    states[stateCode] = stateData.benefits || [];
  }

  // Load municipal benefits by IBGE code
  const municipal: Record<string, Benefit[]> = {};

  for (const [ibgeCode, municipalData] of Object.entries(municipalModules)) {
    municipal[ibgeCode] = municipalData.benefits || [];
  }

  return {
    federal,
    states,
    sectoral,
    municipal,
  };
}

/**
 * Get all benefits as a flat array
 */
export function getAllBenefits(catalog: BenefitCatalog): Benefit[] {
  const allBenefits: Benefit[] = [
    ...catalog.federal,
    ...catalog.sectoral,
  ];

  // Add all state benefits
  for (const stateBenefits of Object.values(catalog.states)) {
    allBenefits.push(...stateBenefits);
  }

  // Add all municipal benefits
  if (catalog.municipal) {
    for (const municipalBenefits of Object.values(catalog.municipal)) {
      allBenefits.push(...municipalBenefits);
    }
  }

  return allBenefits;
}

/**
 * Get benefits relevant to a specific state
 * Returns federal + state-specific + applicable sectoral benefits
 */
export function getBenefitsForState(
  catalog: BenefitCatalog,
  stateCode: string
): Benefit[] {
  const upperState = stateCode.toUpperCase();

  const benefits: Benefit[] = [
    ...catalog.federal,
    ...(catalog.states[upperState] || []),
    ...catalog.sectoral.filter(b => !b.state || b.state === upperState),
  ];

  return benefits;
}

/**
 * Get benefits relevant to a specific municipality
 * Returns federal + state + municipal + applicable sectoral benefits
 */
export function getBenefitsForMunicipality(
  catalog: BenefitCatalog,
  stateCode: string,
  ibgeCode: string
): Benefit[] {
  const upperState = stateCode.toUpperCase();

  const benefits: Benefit[] = [
    ...catalog.federal,
    ...(catalog.states[upperState] || []),
    ...(catalog.municipal?.[ibgeCode] || []),
    ...catalog.sectoral.filter(b => !b.state || b.state === upperState),
  ];

  return benefits;
}

/**
 * Get list of municipalities that have benefits registered
 */
export function getMunicipalitiesWithBenefits(catalog: BenefitCatalog): string[] {
  if (!catalog.municipal) return [];
  return Object.keys(catalog.municipal).filter(
    ibge => catalog.municipal![ibge].length > 0
  );
}

/**
 * Get a single benefit by ID
 */
export function getBenefitById(
  catalog: BenefitCatalog,
  benefitId: string
): Benefit | undefined {
  // Search in federal
  let benefit = catalog.federal.find(b => b.id === benefitId);
  if (benefit) return benefit;

  // Search in sectoral
  benefit = catalog.sectoral.find(b => b.id === benefitId);
  if (benefit) return benefit;

  // Search in all states
  for (const stateBenefits of Object.values(catalog.states)) {
    benefit = stateBenefits.find(b => b.id === benefitId);
    if (benefit) return benefit;
  }

  // Search in all municipalities
  if (catalog.municipal) {
    for (const municipalBenefits of Object.values(catalog.municipal)) {
      benefit = municipalBenefits.find(b => b.id === benefitId);
      if (benefit) return benefit;
    }
  }

  return undefined;
}

/**
 * Get benefits by scope
 */
export function getBenefitsByScope(
  catalog: BenefitCatalog,
  scope: 'federal' | 'state' | 'municipal' | 'sectoral'
): Benefit[] {
  switch (scope) {
    case 'federal':
      return catalog.federal;
    case 'sectoral':
      return catalog.sectoral;
    case 'state':
      // Return all state benefits combined
      return Object.values(catalog.states).flat();
    case 'municipal':
      // Return all municipal benefits combined
      return catalog.municipal ? Object.values(catalog.municipal).flat() : [];
    default:
      return [];
  }
}

/**
 * Get list of states that have benefits registered
 */
export function getStatesWithBenefits(catalog: BenefitCatalog): string[] {
  return Object.keys(catalog.states).filter(
    state => catalog.states[state].length > 0
  );
}

/**
 * Get catalog statistics
 */
export function getCatalogStats(catalog: BenefitCatalog): {
  totalBenefits: number;
  federalCount: number;
  stateCount: number;
  municipalCount: number;
  sectoralCount: number;
  statesWithBenefits: number;
  municipalitiesWithBenefits: number;
  benefitsByCategory: Record<string, number>;
} {
  const allBenefits = getAllBenefits(catalog);

  const benefitsByCategory: Record<string, number> = {};
  for (const benefit of allBenefits) {
    const category = benefit.category || 'Outros';
    benefitsByCategory[category] = (benefitsByCategory[category] || 0) + 1;
  }

  return {
    totalBenefits: allBenefits.length,
    federalCount: catalog.federal.length,
    stateCount: Object.values(catalog.states).flat().length,
    municipalCount: catalog.municipal ? Object.values(catalog.municipal).flat().length : 0,
    sectoralCount: catalog.sectoral.length,
    statesWithBenefits: getStatesWithBenefits(catalog).length,
    municipalitiesWithBenefits: getMunicipalitiesWithBenefits(catalog).length,
    benefitsByCategory,
  };
}

/**
 * Format currency value in Brazilian Reais
 */
export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

/**
 * Format benefit value for display
 * Accepts either a full Benefit or a partial object with estimatedValue
 */
export function formatBenefitValue(benefit: { estimatedValue?: Benefit['estimatedValue'] }): string {
  if (!benefit.estimatedValue) return 'Consultar';

  const { type, min, max, description } = benefit.estimatedValue;

  if (description) {
    // If there's a description, use it but add values if available
    if (min && max && min !== max) {
      return `${formatCurrency(min)} a ${formatCurrency(max)}`;
    }
    if (min || max) {
      return formatCurrency(min || max || 0);
    }
    return description;
  }

  const typeLabel = {
    monthly: '/mês',
    annual: '/ano',
    one_time: ' (único)',
  }[type];

  if (min && max && min !== max) {
    return `${formatCurrency(min)} a ${formatCurrency(max)}${typeLabel}`;
  }

  return `${formatCurrency(min || max || 0)}${typeLabel}`;
}

/**
 * Get state name from code
 */
export function getStateName(stateCode: string): string {
  return BRAZILIAN_STATES[stateCode.toUpperCase()] || stateCode;
}

// Singleton catalog instance
let catalogInstance: BenefitCatalog | null = null;

/**
 * Get the benefits catalog (loads once, returns cached)
 */
export function getBenefitsCatalog(): BenefitCatalog {
  if (!catalogInstance) {
    catalogInstance = loadBenefitsCatalog();
  }
  return catalogInstance;
}

/**
 * Refresh the catalog (useful for hot reloading in development)
 */
export function refreshCatalog(): BenefitCatalog {
  catalogInstance = loadBenefitsCatalog();
  return catalogInstance;
}
