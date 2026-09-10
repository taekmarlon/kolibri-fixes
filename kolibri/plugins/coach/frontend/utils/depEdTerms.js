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

export default {
  DEPED_TERMS,
  DEPED_TERM_CONFIG,
  getItemTerm,
  getTermLabel,
  transmuteDepEdScore,
  getDepEdRemarks,
};
