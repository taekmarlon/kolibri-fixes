/**
 * DepEd 3-Term School Calendar (DepEd Order No. 009, s. 2026) Utilities
 * Aligns Kolibri / PHIEDU with the official Philippine basic education calendar
 * for School Year 2026-2027 (201 total class days).
 */

export const DEPED_TERMS = {
  ALL: 'all',
  TERM_1: 'term_1',
  TERM_2: 'term_2',
  TERM_3: 'term_3',
};

export const DEPED_TERM_CONFIG = [
  {
    key: DEPED_TERMS.TERM_1,
    label: 'Term 1 (Jun 8 – Sep 15, 2026)',
    shortLabel: 'Term 1',
    tag: '[Term 1]',
    badgeClass: 'deped-term-1',
    startDate: new Date('2026-06-08T00:00:00'),
    endDate: new Date('2026-09-15T23:59:59'),
    classDays: 68,
    blocks: {
      opening: 'June 8 – 11, 2026 (Profiling & BOSY Diagnostic)',
      instructional: 'June 15 – September 4, 2026',
      endOfTerm: 'September 7 – 15, 2026 (Assessments & Wellness Break)',
    },
  },
  {
    key: DEPED_TERMS.TERM_2,
    label: 'Term 2 (Sep 16 – Dec 18, 2026)',
    shortLabel: 'Term 2',
    tag: '[Term 2]',
    badgeClass: 'deped-term-2',
    startDate: new Date('2026-09-16T00:00:00'),
    endDate: new Date('2026-12-18T23:59:59'),
    classDays: 66,
    blocks: {
      instructional: 'September 16 – December 11, 2026',
      endOfTerm: 'December 14 – 18, 2026 (Mid-Year Assessments & Break)',
    },
  },
  {
    key: DEPED_TERMS.TERM_3,
    label: 'Term 3 (Jan 4 – Apr 8, 2027)',
    shortLabel: 'Term 3',
    tag: '[Term 3]',
    badgeClass: 'deped-term-3',
    startDate: new Date('2027-01-04T00:00:00'),
    endDate: new Date('2027-04-08T23:59:59'),
    classDays: 67,
    blocks: {
      instructional: 'January 4 – March 26, 2027',
      endOfTerm: 'March 29 – April 8, 2027 (EOSY Assessments & Moving Up)',
    },
  },
];

/**
 * Extracts or detects which DepEd Term an item (Quiz, Lesson, Assignment) belongs to.
 * Checks for explicit title tags (e.g. "[Term 1]", "[T1]"), description tags,
 * or falls back to date matching against the official DepEd 2026-2027 term bounds.
 * Default fallback is Term 1 for backward compatibility.
 *
 * @param {Object} item
 * @returns {string} One of DEPED_TERMS (term_1, term_2, term_3)
 */
export function getItemTerm(item) {
  if (!item) return DEPED_TERMS.TERM_1;

  const title = (item.title || item.name || '').toLowerCase();
  const desc = (item.description || '').toLowerCase();
  const text = `${title} ${desc}`;

  // Check explicit term tags
  if (text.includes('[term 1]') || text.includes('[t1]') || text.includes('term 1') || text.includes('term-1')) {
    return DEPED_TERMS.TERM_1;
  }
  if (text.includes('[term 2]') || text.includes('[t2]') || text.includes('term 2') || text.includes('term-2')) {
    return DEPED_TERMS.TERM_2;
  }
  if (text.includes('[term 3]') || text.includes('[t3]') || text.includes('term 3') || text.includes('term-3')) {
    return DEPED_TERMS.TERM_3;
  }

  // Fallback to date matching
  const dateVal = item.due_date || item.date_created || item.created_at;
  if (dateVal) {
    const itemDate = new Date(dateVal);
    if (!isNaN(itemDate.getTime())) {
      for (const term of DEPED_TERM_CONFIG) {
        if (itemDate >= term.startDate && itemDate <= term.endDate) {
          return term.key;
        }
      }
    }
  }

  // Backward compatibility default
  return DEPED_TERMS.TERM_1;
}

/**
 * Returns a user-friendly label for a term key.
 * @param {string} termKey
 * @returns {string}
 */
export function getTermLabel(termKey, short = false) {
  const found = DEPED_TERM_CONFIG.find(t => t.key === termKey);
  if (found) {
    return short ? found.shortLabel : found.label;
  }
  return 'All Terms';
}

/**
 * Transmutes a raw percentage score (0-100) according to DepEd Order No. 8, s. 2015
 * and DepEd Order No. 009, s. 2026.
 *
 * Official DepEd scale:
 * Minimum passing score is 60.00% which transmutes to a grade of 75.
 * 100% -> 100
 * Formula: 60 + (raw * 0.4), with exact DepEd boundary stepping.
 *
 * @param {number|null} rawPercentage
 * @returns {number|null} Transmuted grade (60-100) or null if input is null
 */
export function transmuteDepEdScore(rawPercentage) {
  if (rawPercentage === null || rawPercentage === undefined || isNaN(rawPercentage)) {
    return null;
  }

  const raw = Math.min(100, Math.max(0, Number(rawPercentage)));

  // Official DepEd Transmutation Table Reference
  if (raw >= 100) return 100;
  if (raw >= 98.40) return 99;
  if (raw >= 96.80) return 98;
  if (raw >= 95.20) return 97;
  if (raw >= 93.60) return 96;
  if (raw >= 92.00) return 95;
  if (raw >= 90.40) return 94;
  if (raw >= 88.80) return 93;
  if (raw >= 87.20) return 92;
  if (raw >= 85.60) return 91;
  if (raw >= 84.00) return 90;
  if (raw >= 82.40) return 89;
  if (raw >= 80.80) return 88;
  if (raw >= 79.20) return 87;
  if (raw >= 77.60) return 86;
  if (raw >= 76.00) return 85;
  if (raw >= 74.40) return 84;
  if (raw >= 72.80) return 83;
  if (raw >= 71.20) return 82;
  if (raw >= 69.60) return 81;
  if (raw >= 68.00) return 80;
  if (raw >= 66.40) return 79;
  if (raw >= 64.80) return 78;
  if (raw >= 63.20) return 77;
  if (raw >= 61.60) return 76;
  if (raw >= 60.00) return 75; // DepEd Minimum Passing Mark

  // Below 60% (Did Not Meet Expectations / Remediation needed)
  if (raw >= 56.00) return 74;
  if (raw >= 52.00) return 73;
  if (raw >= 48.00) return 72;
  if (raw >= 44.00) return 71;
  if (raw >= 40.00) return 70;
  if (raw >= 36.00) return 69;
  if (raw >= 32.00) return 68;
  if (raw >= 28.00) return 67;
  if (raw >= 24.00) return 66;
  if (raw >= 20.00) return 65;
  if (raw >= 16.00) return 64;
  if (raw >= 12.00) return 63;
  if (raw >= 8.00) return 62;
  if (raw >= 4.00) return 61;
  return 60;
}

/**
 * Returns the DepEd performance remark and ARAL status.
 * @param {number|null} transmutedGrade
 * @returns {Object}
 */
export function getDepEdRemarks(transmutedGrade) {
  if (transmutedGrade === null || transmutedGrade === undefined || isNaN(transmutedGrade)) {
    return {
      status: 'No Grade',
      badgeClass: 'status-pending',
      aral: false,
      descriptor: 'No assessments submitted yet',
    };
  }

  const grade = Number(transmutedGrade);
  if (grade >= 90) {
    return {
      status: 'PASSED / PROMOTED',
      badgeClass: 'status-outstanding',
      aral: false,
      descriptor: 'Outstanding',
    };
  }
  if (grade >= 85) {
    return {
      status: 'PASSED / PROMOTED',
      badgeClass: 'status-very-satisfactory',
      aral: false,
      descriptor: 'Very Satisfactory',
    };
  }
  if (grade >= 80) {
    return {
      status: 'PASSED / PROMOTED',
      badgeClass: 'status-satisfactory',
      aral: false,
      descriptor: 'Satisfactory',
    };
  }
  if (grade >= 75) {
    return {
      status: 'PASSED / PROMOTED',
      badgeClass: 'status-fairly-satisfactory',
      aral: false,
      descriptor: 'Fairly Satisfactory',
    };
  }

  // Grade < 75 requires Academic Recovery and Accessible Learning (ARAL) intervention
  return {
    status: 'NEEDS REMEDIATION (ARAL)',
    badgeClass: 'status-remediation',
    aral: true,
    descriptor: 'Did Not Meet Expectations',
  };
}

/**
 * DepEd Order No. 8, s. 2015 Assessment Components
 * K to 12 Summative Assessment categories
 */
export const DEPED_COMPONENTS = {
  ALL: 'all',
  WW: 'ww',
  PT: 'pt',
  TA: 'ta',
};

export const DEPED_COMPONENT_CONFIG = [
  {
    key: DEPED_COMPONENTS.WW,
    code: 'WW',
    label: 'Written Work (WW)',
    shortLabel: 'Written Work',
    tag: '[WW]',
    badgeClass: 'deped-comp-ww',
    description: 'Unit quizzes, short tests, essays, written exercises, and chapter reviews',
  },
  {
    key: DEPED_COMPONENTS.PT,
    code: 'PT',
    label: 'Performance Task (PT)',
    shortLabel: 'Performance Task',
    tag: '[PT]',
    badgeClass: 'deped-comp-pt',
    description: 'Hands-on projects, experiments, oral presentations, and practical outputs',
  },
  {
    key: DEPED_COMPONENTS.TA,
    code: 'TA',
    label: 'Quarterly / Term Assessment (QA/TA)',
    shortLabel: 'Term Exam',
    tag: '[TA]',
    badgeClass: 'deped-comp-ta',
    description: 'Periodic examinations, end-of-term assessments, and comprehensive evaluations',
  },
];

/**
 * DepEd Order No. 8, s. 2015 Subject Group Weighting Schemes
 */
export const DEPED_GRADING_SCHEMES = {
  math_science: {
    key: 'math_science',
    label: 'Science & Mathematics (WW: 40%, PT: 40%, QA: 20%)',
    shortLabel: 'Math & Science',
    weights: { ww: 0.4, pt: 0.4, ta: 0.2 },
  },
  languages_ap_esp: {
    key: 'languages_ap_esp',
    label: 'Languages, AP & EsP (WW: 30%, PT: 50%, QA: 20%)',
    shortLabel: 'Languages & Social Studies',
    weights: { ww: 0.3, pt: 0.5, ta: 0.2 },
  },
  mapeh_epp_tle: {
    key: 'mapeh_epp_tle',
    label: 'MAPEH, EPP & TLE (WW: 20%, PT: 60%, QA: 20%)',
    shortLabel: 'MAPEH, EPP & TLE',
    weights: { ww: 0.2, pt: 0.6, ta: 0.2 },
  },
  shs_core: {
    key: 'shs_core',
    label: 'Senior High School - Core Subjects (WW: 25%, PT: 50%, QA: 25%)',
    shortLabel: 'SHS Core',
    weights: { ww: 0.25, pt: 0.5, ta: 0.25 },
  },
  shs_acad: {
    key: 'shs_acad',
    label: 'Senior High School - Academic Track (WW: 35%, PT: 40%, QA: 25%)',
    shortLabel: 'SHS Academic',
    weights: { ww: 0.35, pt: 0.4, ta: 0.25 },
  },
  shs_tvl: {
    key: 'shs_tvl',
    label: 'Senior High School - TVL / Arts / Sports (WW: 20%, PT: 60%, QA: 20%)',
    shortLabel: 'SHS TVL & Arts',
    weights: { ww: 0.2, pt: 0.6, ta: 0.2 },
  },
};

/**
 * Detects or extracts the DepEd Assessment Component for an item.
 * Checks explicit tags [WW], [PT], [TA], [QA] or applies intelligent fallbacks.
 *
 * @param {Object} item
 * @returns {string} One of DEPED_COMPONENTS (ww, pt, ta)
 */
export function getItemComponent(item) {
  if (!item) return DEPED_COMPONENTS.WW;

  const title = (item.title || item.name || '').toLowerCase();
  const desc = (item.description || '').toLowerCase();
  const text = `${title} ${desc}`;

  // Explicit component tags
  if (
    text.includes('[ww]') ||
    text.includes('written work') ||
    text.includes('[written-work]')
  ) {
    return DEPED_COMPONENTS.WW;
  }
  if (
    text.includes('[pt]') ||
    text.includes('performance task') ||
    text.includes('[performance-task]') ||
    text.includes('[project]')
  ) {
    return DEPED_COMPONENTS.PT;
  }
  if (
    text.includes('[ta]') ||
    text.includes('[qa]') ||
    text.includes('term assessment') ||
    text.includes('quarterly assessment') ||
    text.includes('periodical') ||
    text.includes('periodic exam')
  ) {
    return DEPED_COMPONENTS.TA;
  }

  // Type and naming based detection
  if (
    text.includes('exam') ||
    text.includes('capstone') ||
    text.includes('end-of-school-year') ||
    text.includes('eosy')
  ) {
    return DEPED_COMPONENTS.TA;
  }

  // Quizzes default to Written Work (WW)
  if (item.question_sources || item.quiz_id || (item.kind && item.kind === 'exam')) {
    return DEPED_COMPONENTS.WW;
  }

  // Default coursework assignments default to Performance Task (PT)
  return DEPED_COMPONENTS.PT;
}

/**
 * Returns user-friendly component info object.
 * @param {string} compKey
 * @returns {Object}
 */
export function getComponentInfo(compKey) {
  return (
    DEPED_COMPONENT_CONFIG.find(c => c.key === compKey) || DEPED_COMPONENT_CONFIG[0]
  );
}

/**
 * Calculates DepEd E-Class Record (DO 8, s. 2015) for a single term and learner.
 * Computes:
 * - Highest Possible Score (HPS) and Raw Score per component (WW, PT, TA)
 * - Percentage Score (PS = Raw / HPS * 100)
 * - Weighted Score (WS = PS * Component Weight)
 * - Initial Grade = Sum of Weighted Scores
 * - Transmuted Grade = Table Lookup of Initial Grade
 *
 * @param {Object} learnerSubmissions - Dict of { [assignmentId]: { grade, status } }
 * @param {Array} termAssignments - List of assignments for the term
 * @param {Object} scheme - Object from DEPED_GRADING_SCHEMES
 * @returns {Object} ECR calculation details
 */
export function calculateTermECR(learnerSubmissions, termAssignments, scheme) {
  const activeScheme = scheme || DEPED_GRADING_SCHEMES.math_science;
  const weights = activeScheme.weights;

  const components = {
    ww: { hps: 0, rawScore: 0, items: 0, gradedItems: 0 },
    pt: { hps: 0, rawScore: 0, items: 0, gradedItems: 0 },
    ta: { hps: 0, rawScore: 0, items: 0, gradedItems: 0 },
  };

  (termAssignments || []).forEach(item => {
    const compKey = getItemComponent(item);
    if (components[compKey]) {
      components[compKey].items += 1;
      components[compKey].hps += item.max_points || 0;
      const sub = learnerSubmissions && learnerSubmissions[item.id];
      if (sub && sub.grade !== null && sub.grade !== undefined) {
        components[compKey].rawScore += sub.grade;
        components[compKey].gradedItems += 1;
      }
    }
  });

  const result = {
    ww: null,
    pt: null,
    ta: null,
    initialGrade: null,
    transmutedGrade: null,
    remarks: null,
    hasSubmissions: false,
  };

  let activeWeightSum = 0;
  let weightedScoreSum = 0;

  ['ww', 'pt', 'ta'].forEach(compKey => {
    const c = components[compKey];
    const weight = weights[compKey];
    if (c.hps > 0) {
      const ps = Number(((c.rawScore / c.hps) * 100).toFixed(1));
      const ws = Number((ps * weight).toFixed(2));
      result[compKey] = {
        hps: c.hps,
        rawScore: c.rawScore,
        ps,
        ws,
        weight: Math.round(weight * 100),
        items: c.items,
        gradedItems: c.gradedItems,
      };
      if (c.gradedItems > 0) {
        result.hasSubmissions = true;
      }
      activeWeightSum += weight;
      weightedScoreSum += ws;
    } else {
      result[compKey] = {
        hps: 0,
        rawScore: 0,
        ps: null,
        ws: null,
        weight: Math.round(weight * 100),
        items: 0,
        gradedItems: 0,
      };
    }
  });

  if (result.hasSubmissions && activeWeightSum > 0) {
    // If not all components are populated in this term, normalize weighted score
    const normalizedInitial = weightedScoreSum / activeWeightSum;
    result.initialGrade = Number(normalizedInitial.toFixed(1));
    result.transmutedGrade = transmuteDepEdScore(result.initialGrade);
    result.remarks = getDepEdRemarks(result.transmutedGrade);
  } else {
    result.remarks = getDepEdRemarks(null);
  }

  return result;
}

export default {
  DEPED_TERMS,
  DEPED_TERM_CONFIG,
  DEPED_COMPONENTS,
  DEPED_COMPONENT_CONFIG,
  DEPED_GRADING_SCHEMES,
  getItemTerm,
  getTermLabel,
  getItemComponent,
  getComponentInfo,
  calculateTermECR,
  transmuteDepEdScore,
  getDepEdRemarks,
};
