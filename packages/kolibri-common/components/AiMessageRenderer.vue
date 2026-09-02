<template>
  <div class="ai-rich-message-content">
    <div
      v-for="(block, idx) in parsedBlocks"
      :key="idx"
      class="content-block"
    >
      <!-- Main Heading (### or ##) -->
      <div
        v-if="block.type === 'heading'"
        class="rich-heading-card"
        :style="{
          backgroundColor: $themePalette.grey.v_100,
          borderLeft: `4px solid ${$themeTokens.primary}`,
          color: $themeTokens.text,
        }"
      >
        <span class="heading-icon">{{ getHeadingIcon(block.text) }}</span>
        <h3 class="heading-title" v-html="formatInlineText(block.text)"></h3>
      </div>

      <!-- Problem / Question Card -->
      <div
        v-else-if="block.type === 'question'"
        class="callout-card question-card"
        :style="{ backgroundColor: '#eff6ff', borderColor: '#93c5fd', color: '#1e3a8a' }"
      >
        <div class="card-badge question-badge">
          <span class="badge-icon">❓</span>
          <span>Question / Problem</span>
        </div>
        <div class="card-body" v-html="formatInlineText(block.text)"></div>
      </div>

      <!-- Solution / Explanation Card -->
      <div
        v-else-if="block.type === 'solution'"
        class="callout-card solution-card"
        :style="{ backgroundColor: '#f0fdf4', borderColor: '#86efac', color: '#14532d' }"
      >
        <div class="card-badge solution-badge">
          <span class="badge-icon">✅</span>
          <span>Step-by-Step Solution</span>
        </div>
        <div class="card-body" v-html="formatInlineText(block.text)"></div>
      </div>

      <!-- Step Card (Step 1, Step 2, etc.) -->
      <div
        v-else-if="block.type === 'step'"
        class="step-card"
        :style="{
          backgroundColor: $themeTokens.surface,
          borderColor: $themeTokens.fineLine,
        }"
      >
        <div class="step-header">
          <span class="step-number" :style="{ backgroundColor: $themeTokens.primary }">{{ block.stepNum }}</span>
          <span class="step-title" :style="{ color: $themeTokens.text }" v-html="formatInlineText(block.title)"></span>
        </div>
        <div class="step-body" :style="{ color: $themeTokens.text }" v-html="formatInlineText(block.text)"></div>
      </div>

      <!-- Block Math / Formula Card ($$...$$) -->
      <div
        v-else-if="block.type === 'math_block'"
        class="math-formula-card"
        :style="{
          backgroundColor: '#f8fafc',
          borderColor: '#cbd5e1',
          color: '#0f172a',
        }"
      >
        <div class="math-label">
          <span class="math-icon">📐</span>
          <span>Calculation / Equation</span>
        </div>
        <div class="math-display">
          {{ cleanMathString(block.math) }}
        </div>
      </div>

      <!-- Fun Fact / Tip Card -->
      <div
        v-else-if="block.type === 'tip'"
        class="callout-card tip-card"
        :style="{ backgroundColor: '#fefce8', borderColor: '#fde047', color: '#713f12' }"
      >
        <div class="card-badge tip-badge">
          <span class="badge-icon">💡</span>
          <span>Helpful Tip / Concept</span>
        </div>
        <div class="card-body" v-html="formatInlineText(block.text)"></div>
      </div>

      <!-- Regular Paragraph -->
      <div
        v-else-if="block.type === 'paragraph'"
        class="rich-paragraph"
        :style="{ color: $themeTokens.text }"
        v-html="formatInlineText(block.text)"
      ></div>

      <!-- Bullet List -->
      <ul
        v-else-if="block.type === 'list'"
        class="rich-list"
        :style="{ color: $themeTokens.text }"
      >
        <li
          v-for="(item, itemIdx) in block.items"
          :key="itemIdx"
          class="list-item"
        >
          <span class="bullet-dot" :style="{ backgroundColor: $themeTokens.primary }"></span>
          <span class="item-text" v-html="formatInlineText(item)"></span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
  import { computed } from 'vue';

  export default {
    name: 'AiMessageRenderer',
    props: {
      content: {
        type: String,
        required: true,
      },
      gradeLevel: {
        type: String,
        default: 'elementary',
      },
    },
    setup(props) {
      function cleanMathString(rawMath) {
        if (!rawMath) return '';
        return rawMath
          .replace(/\\begin\{pmatrix\}/g, '[ ')
          .replace(/\\end\{pmatrix\}/g, ' ]')
          .replace(/\\quad/g, '   ')
          .replace(/\\times/g, ' * ')
          .replace(/\\cdot/g, ' * ')
          .replace(/\\frac\{([^}]+)\}\{([^}]+)\}/g, '($1 / $2)')
          .replace(/\\sqrt\{([^}]+)\}/g, 'sqrt($1)')
          .replace(/\\le/g, ' <= ')
          .replace(/\\ge/g, ' >= ')
          .replace(/\\neq/g, ' != ')
          .replace(/\\approx/g, ' ~= ')
          .replace(/\\pm/g, ' +- ')
          .replace(/\\mathbf\{([^}]+)\}/g, '$1')
          .replace(/\\text\{([^}]+)\}/g, '$1')
          .replace(/\\,/g, ' ')
          .replace(/\\\\/g, '\n')
          .replace(/\$/g, '')
          .trim();
      }

      function formatInlineText(text) {
        if (!text) return '';
        let formatted = text
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
          .replace(/\*\*([^*]+)\*\*/g, '<strong class="highlight-bold">$1</strong>')
          .replace(/\*([^*]+)\*/g, '<em>$1</em>')
          .replace(/\$([^$]+)\$/g, (match, formula) => {
            const cleaned = cleanMathString(formula);
            return `<span class="inline-math-chip">${cleaned}</span>`;
          })
          .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
          .replace(/\n/g, '<br/>');

        return formatted;
      }

      function getHeadingIcon(headingText) {
        const lower = headingText.toLowerCase();
        if (lower.includes('problem') || lower.includes('question')) return '🎯';
        if (lower.includes('solution') || lower.includes('answer')) return '✅';
        if (lower.includes('step')) return '🪜';
        if (lower.includes('law') || lower.includes('formula') || lower.includes('equation')) return '📐';
        if (lower.includes('example')) return '📝';
        if (lower.includes('fact') || lower.includes('trivia')) return '⭐';
        if (lower.includes('summary') || lower.includes('takeaway')) return '📌';
        return '💡';
      }

      const parsedBlocks = computed(() => {
        if (!props.content) return [];
        const raw = props.content.trim();
        const lines = raw.split('\n');
        const blocks = [];
        let currentList = [];
        let i = 0;

        function flushList() {
          if (currentList.length > 0) {
            blocks.push({ type: 'list', items: [...currentList] });
            currentList = [];
          }
        }

        while (i < lines.length) {
          const line = lines[i].trim();

          if (!line) {
            flushList();
            i++;
            continue;
          }

          if (line === '---' || line === '***' || line === '___') {
            flushList();
            i++;
            continue;
          }

          if (line.startsWith('$$')) {
            flushList();
            let mathContent = line.slice(2);
            if (mathContent.endsWith('$$') && mathContent.length > 2) {
              mathContent = mathContent.slice(0, -2);
              blocks.push({ type: 'math_block', math: mathContent.trim() });
              i++;
              continue;
            } else {
              let multiMath = [mathContent];
              i++;
              while (i < lines.length && !lines[i].trim().endsWith('$$')) {
                multiMath.push(lines[i].trim());
                i++;
              }
              if (i < lines.length) {
                const lastLine = lines[i].trim().replace(/\$\$$/, '');
                if (lastLine) multiMath.push(lastLine);
              }
              blocks.push({ type: 'math_block', math: multiMath.join('\n') });
              i++;
              continue;
            }
          }

          if (line.startsWith('#')) {
            flushList();
            const headingText = line.replace(/^#+\s*/, '');
            blocks.push({ type: 'heading', text: headingText });
            i++;
            continue;
          }

          if (line.match(/^\*\*(Question|Problem|Challenge)\s*:?\*\*/i)) {
            flushList();
            const text = line.replace(/^\*\*(Question|Problem|Challenge)\s*:?\*\*\s*/i, '');
            blocks.push({ type: 'question', text });
            i++;
            continue;
          }

          if (line.match(/^\*\*(Solution|Answer|Explanation)\s*:?\*\*/i)) {
            flushList();
            const text = line.replace(/^\*\*(Solution|Answer|Explanation)\s*:?\*\*\s*/i, '');
            blocks.push({ type: 'solution', text });
            i++;
            continue;
          }

          const stepMatch = line.match(/^(\s*\*|\s*-|\s*\d+\.)?\s*\*\*(Step\s*\d+|Part\s*\d+)[^*]*\*\*\s*(.*)/i);
          if (stepMatch) {
            flushList();
            const stepNum = stepMatch[2].replace(/[^0-9]/g, '') || '•';
            blocks.push({ type: 'step', stepNum: stepNum, title: stepMatch[2], text: stepMatch[3] || line });
            i++;
            continue;
          }

          if (line.match(/^\*\*(Tip|Remember|Did you know|Fun Fact|Note)\s*:?\*\*/i)) {
            flushList();
            const text = line.replace(/^\*\*(Tip|Remember|Did you know|Fun Fact|Note)\s*:?\*\*\s*/i, '');
            blocks.push({ type: 'tip', text });
            i++;
            continue;
          }

          if (line.match(/^(\*|-|\+)\s+(.+)/)) {
            const itemText = line.replace(/^(\*|-|\+)\s+/, '');
            currentList.push(itemText);
            i++;
            continue;
          }

          if (line.match(/^\d+\.\s+(.+)/)) {
            const itemText = line.replace(/^\d+\.\s+/, '');
            currentList.push(itemText);
            i++;
            continue;
          }

          flushList();
          blocks.push({ type: 'paragraph', text: line });
          i++;
        }

        flushList();
        return blocks;
      });

      return {
        parsedBlocks,
        formatInlineText,
        cleanMathString,
        getHeadingIcon,
      };
    },
  };
</script>

<style lang="scss" scoped>
  .ai-rich-message-content {
    display: flex;
    flex-direction: column;
    gap: 12px;
    font-size: 14.5px;
    line-height: 1.6;
  }

  .content-block {
    margin: 0;
  }

  .rich-heading-card {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    border-radius: 6px;
    margin: 6px 0;

    .heading-icon {
      font-size: 20px;
    }

    .heading-title {
      margin: 0;
      font-size: 16px;
      font-weight: 700;
    }
  }

  .callout-card {
    border: 1px solid;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;

    .card-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 6px;
    }

    .card-body {
      font-size: 14px;
      line-height: 1.5;
    }
  }

  .step-card {
    border: 1px solid;
    border-radius: 8px;
    padding: 12px 14px;
    margin: 6px 0;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);

    .step-header {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 6px;

      .step-number {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        color: #ffffff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: bold;
      }

      .step-title {
        font-weight: 700;
        font-size: 14px;
      }
    }

    .step-body {
      padding-left: 34px;
      font-size: 13.5px;
      line-height: 1.5;
    }
  }

  .math-formula-card {
    border: 1px solid;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 10px 0;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);

    .math-label {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #64748b;
      margin-bottom: 6px;
    }

    .math-display {
      font-family: 'Cambria Math', 'STIX Two Math', 'Consolas', 'Courier New', monospace;
      font-size: 15.5px;
      font-weight: 600;
      white-space: pre-wrap;
      line-height: 1.6;
    }
  }

  .rich-paragraph {
    line-height: 1.6;
    margin: 4px 0;
  }

  .rich-list {
    margin: 4px 0;
    padding-left: 8px;
    list-style: none;

    .list-item {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      margin-bottom: 6px;

      .bullet-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        margin-top: 8px;
        flex-shrink: 0;
      }

      .item-text {
        flex: 1;
        line-height: 1.5;
      }
    }
  }

  :deep(.inline-math-chip) {
    display: inline-block;
    background-color: #f1f5f9;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 1px 6px;
    font-family: 'Cambria Math', 'STIX Two Math', monospace;
    font-weight: 600;
    color: #0f172a;
    font-size: 13px;
    margin: 0 2px;
  }

  :deep(.highlight-bold) {
    font-weight: 700;
  }

  :deep(.inline-code) {
    background-color: rgba(0, 0, 0, 0.06);
    padding: 2px 5px;
    border-radius: 4px;
    font-family: monospace;
    font-size: 12.5px;
  }
</style>
