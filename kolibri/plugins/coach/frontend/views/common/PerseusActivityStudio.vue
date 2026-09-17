<template>

  <div class="perseus-activity-studio">
    <!-- Header: Activity Metadata & Subject Category -->
    <div
      class="studio-top-bar"
      :style="{
        backgroundColor: $themePalette.grey.v_100,
        border: `1px solid ${$themeTokens.fineLine}`,
        borderRadius: '8px',
        padding: '16px',
        marginBottom: '20px',
      }"
    >
      <div class="top-row mb-16">
        <div class="title-field">
          <KTextbox
            v-model="title"
            :label="titleLabel$()"
            :invalid="Boolean(titleError)"
            :invalidText="titleError"
            :autofocus="true"
          />
        </div>
        <div class="subject-select-field">
          <KSelect
            v-model="selectedSubject"
            :label="subjectLabel$()"
            :options="subjectOptions"
            :inline="true"
            @change="handleSubjectFilterChange"
          />
        </div>
      </div>

      <KTextbox
        v-model="description"
        :label="descriptionLabel$()"
        :textArea="true"
        :rows="2"
      />
    </div>

    <!-- Multi-Subject Template Selector Banner -->
    <div
      class="templates-banner mb-20"
      :style="{
        backgroundColor: $themeTokens.surface,
        border: `1px solid ${$themeTokens.fineLine}`,
        borderRadius: '8px',
        padding: '16px',
      }"
    >
      <div class="templates-header mb-12">
        <h4 :style="{ margin: '0 0 4px', color: $themeTokens.text }">
          {{ templateLibraryTitle$() }}
        </h4>
        <p :style="{ margin: 0, color: $themeTokens.annotation, fontSize: '0.85rem' }">
          {{ templateLibrarySubtitle$() }}
        </p>
      </div>

      <div class="templates-scroll-row">
        <button
          v-for="tpl in filteredTemplates"
          :key="tpl.id"
          type="button"
          class="template-pill-card"
          :class="{ 'is-selected': activeTemplateId === tpl.id }"
          :style="{
            borderColor: activeTemplateId === tpl.id ? $themeTokens.primary : $themeTokens.fineLine,
            backgroundColor:
              activeTemplateId === tpl.id ? $themePalette.grey.v_100 : $themeTokens.surface,
          }"
          @click="applyTemplate(tpl)"
        >
          <div class="pill-top">
            <span class="tpl-icon">{{ tpl.icon }}</span>
            <span
              class="subject-tag"
              :style="{
                backgroundColor: $themePalette.grey.v_200,
                color: $themeTokens.annotation,
              }"
            >
              {{ tpl.subjectTag }}
            </span>
          </div>
          <div class="tpl-name" :style="{ color: $themeTokens.text }">
            {{ tpl.name }}
          </div>
          <div class="tpl-desc" :style="{ color: $themeTokens.annotation }">
            {{ tpl.description }}
          </div>
        </button>
      </div>
    </div>

    <!-- Mode Switcher: Visual Editor | Interactive Live Preview | Perseus JSON -->
    <div
      class="studio-mode-tabs mb-16"
      :style="{
        display: 'flex',
        gap: '8px',
        borderBottom: `2px solid ${$themeTokens.fineLine}`,
        paddingBottom: '8px',
      }"
    >
      <KButton
        :text="visualEditorModeLabel$()"
        icon="edit"
        :appearance="studioMode === 'editor' ? 'raised-button' : 'flat-button'"
        :primary="studioMode === 'editor'"
        @click="studioMode = 'editor'"
      />
      <KButton
        :text="interactivePreviewModeLabel$()"
        :appearance="studioMode === 'preview' ? 'raised-button' : 'flat-button'"
        :primary="studioMode === 'preview'"
        @click="switchToPreview"
      />
      <KButton
        :text="rawJsonModeLabel$()"
        :appearance="studioMode === 'json' ? 'raised-button' : 'flat-button'"
        :primary="studioMode === 'json'"
        @click="switchToRawJson"
      />
    </div>

    <!-- TAB 1: VISUAL BUILDER -->
    <div
      v-if="studioMode === 'editor'"
      class="editor-mode-wrapper"
    >
      <!-- Question Prompt & Instant Widget Toolbar -->
      <div
        class="prompt-card mb-20"
        :style="{
          backgroundColor: $themeTokens.surface,
          border: `1px solid ${$themeTokens.fineLine}`,
          borderRadius: '8px',
          padding: '16px',
        }"
      >
        <div class="prompt-header-row mb-12">
          <h4 :style="{ margin: 0, color: $themeTokens.text }">
            {{ questionPromptHeader$() }}
          </h4>
          <span :style="{ color: $themeTokens.annotation, fontSize: '0.85rem' }">
            {{ promptHelpText$() }}
          </span>
        </div>

        <!-- Quick Widget Insert Buttons (Multi-Subject) -->
        <div
          class="widget-insert-toolbar mb-12"
          :style="{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '6px',
            backgroundColor: $themePalette.grey.v_100,
            padding: '8px 12px',
            borderRadius: '6px',
            border: `1px solid ${$themeTokens.fineLine}`,
          }"
        >
          <span
            class="toolbar-label"
            :style="{
              alignSelf: 'center',
              fontSize: '0.8rem',
              fontWeight: 'bold',
              color: $themeTokens.annotation,
              marginRight: '6px',
            }"
          >
            {{ insertWidgetPrompt$() }}:
          </span>
          <KButton
            text="📖 Reading Passage"
            appearance="flat-button"
            size="small"
            @click="insertWidgetPlaceholder('passage')"
          />
          <KButton
            text="🔘 Multiple Choice"
            appearance="flat-button"
            size="small"
            @click="insertWidgetPlaceholder('radio')"
          />
          <KButton
            text="🔽 Cloze Dropdown"
            appearance="flat-button"
            size="small"
            @click="insertWidgetPlaceholder('dropdown')"
          />
          <KButton
            text="🔢 Sequence Orderer"
            appearance="flat-button"
            size="small"
            @click="insertWidgetPlaceholder('orderer')"
          />
          <KButton
            text="🗂️ Concept Categorizer"
            appearance="flat-button"
            size="small"
            @click="insertWidgetPlaceholder('categorizer')"
          />
          <KButton
            text="🔗 Matching Pairs"
            appearance="flat-button"
            size="small"
            @click="insertWidgetPlaceholder('matcher')"
          />
          <KButton
            text="📐 Math Expression"
            appearance="flat-button"
            size="small"
            @click="insertWidgetPlaceholder('expression')"
          />
          <KButton
            text="🔢 Numeric Input"
            appearance="flat-button"
            size="small"
            @click="insertWidgetPlaceholder('numeric-input')"
          />
        </div>

        <KTextbox
          v-model="questionContent"
          :label="questionContentLabel$()"
          :textArea="true"
          :rows="5"
          placeholder="Enter question instructions, story or passage text, and widget tags like [[☃ radio 1]] or [[☃ passage 1]]..."
          @input="syncWidgetsFromContent"
        />
      </div>

      <!-- Configured Widget Cards -->
      <div
        v-if="detectedWidgetKeys.length > 0"
        class="configured-widgets-container mb-20"
      >
        <h4
          class="mb-12"
          :style="{ color: $themeTokens.text }"
        >
          {{ widgetConfigurationsHeader$() }} ({{ detectedWidgetKeys.length }})
        </h4>

        <div
          v-for="wKey in detectedWidgetKeys"
          :key="wKey"
          class="widget-config-card mb-16"
          :style="{
            backgroundColor: $themeTokens.surface,
            border: `1px solid ${$themeTokens.fineLine}`,
            borderLeft: `5px solid ${$themeTokens.primary}`,
            borderRadius: '8px',
            padding: '16px',
          }"
        >
          <!-- Card Header -->
          <div class="widget-card-header mb-12">
            <div class="header-tag">
              <span class="widget-icon">{{ getWidgetIcon(widgets[wKey]?.type) }}</span>
              <strong :style="{ color: $themeTokens.text }">{{ wKey }}</strong>
              <span
                class="type-badge ml-8"
                :style="{
                  backgroundColor: $themePalette.grey.v_200,
                  color: $themeTokens.annotation,
                  padding: '2px 8px',
                  borderRadius: '10px',
                  fontSize: '0.8rem',
                }"
              >
                {{ widgets[wKey]?.type?.toUpperCase() }}
              </span>
            </div>
            <KButton
              :text="removeWidgetAction$()"
              appearance="flat-button"
              size="small"
              icon="trash"
              @click="removeWidget(wKey)"
            />
          </div>

          <!-- WIDGET TYPE 1: READING PASSAGE -->
          <div
            v-if="widgets[wKey]?.type === 'passage'"
            class="widget-passage-editor"
          >
            <KTextbox
              v-model="widgets[wKey].options.passageTitle"
              :label="passageTitleLabel$()"
              placeholder="e.g. The Gettysburg Address"
              class="mb-12"
            />
            <KTextbox
              v-model="widgets[wKey].options.passageText"
              :label="passageTextLabel$()"
              :textArea="true"
              :rows="6"
              placeholder="Paste reading passage, historical speech, or literary story here..."
              class="mb-12"
            />
            <KTextbox
              v-model="widgets[wKey].options.footnotes"
              :label="footnotesOptionalLabel$()"
              :textArea="true"
              :rows="2"
              placeholder="Optional explanatory footnotes or vocabulary notes..."
            />
          </div>

          <!-- WIDGET TYPE 2: CLOZE DROPDOWN -->
          <div
            v-else-if="widgets[wKey]?.type === 'dropdown'"
            class="widget-dropdown-editor"
          >
            <p :style="{ margin: '0 0 8px', fontSize: '0.85rem', color: $themeTokens.annotation }">
              {{ dropdownChoicesHelp$() }}
            </p>
            <div
              v-for="(choice, cIdx) in widgets[wKey].options.choices"
              :key="`dd-c-${cIdx}`"
              class="choice-item-row mb-8"
              style="display: flex; align-items: center; gap: 8px;"
            >
              <input
                type="radio"
                :name="`correct-dd-${wKey}`"
                :checked="choice.correct"
                :title="markAsCorrectLabel$()"
                @change="setDropdownCorrect(wKey, cIdx)"
              >
              <div style="flex-grow: 1;">
                <KTextbox
                  v-model="choice.content"
                  :label="`${choiceLabel$()} ${cIdx + 1}`"
                />
              </div>
              <KIconButton
                icon="trash"
                size="small"
                :disabled="widgets[wKey].options.choices.length <= 2"
                :ariaLabel="removeChoiceLabel$()"
                @click="removeDropdownChoice(wKey, cIdx)"
              />
            </div>
            <KButton
              :text="addChoiceAction$()"
              appearance="flat-button"
              icon="plus"
              size="small"
              @click="addDropdownChoice(wKey)"
            />
          </div>

          <!-- WIDGET TYPE 3: MULTIPLE CHOICE (RADIO) -->
          <div
            v-else-if="widgets[wKey]?.type === 'radio'"
            class="widget-radio-editor"
          >
            <div class="radio-options-controls mb-12" style="display: flex; gap: 16px; flex-wrap: wrap;">
              <KCheckbox
                :checked="widgets[wKey].options.multipleSelect"
                :label="allowMultipleAnswersLabel$()"
                @change="val => widgets[wKey].options.multipleSelect = val"
              />
              <KCheckbox
                :checked="widgets[wKey].options.randomize"
                :label="randomizeChoicesLabel$()"
                @change="val => widgets[wKey].options.randomize = val"
              />
            </div>

            <div
              v-for="(choice, cIdx) in widgets[wKey].options.choices"
              :key="`radio-c-${cIdx}`"
              class="choice-item-row mb-8"
              style="display: flex; align-items: center; gap: 8px;"
            >
              <input
                :type="widgets[wKey].options.multipleSelect ? 'checkbox' : 'radio'"
                :name="`correct-radio-${wKey}`"
                :checked="choice.correct"
                :title="markAsCorrectLabel$()"
                @change="toggleRadioChoiceCorrect(wKey, cIdx)"
              >
              <div style="flex-grow: 1;">
                <KTextbox
                  v-model="choice.content"
                  :label="`${choiceLabel$()} ${cIdx + 1}`"
                />
              </div>
              <KIconButton
                icon="trash"
                size="small"
                :disabled="widgets[wKey].options.choices.length <= 2"
                :ariaLabel="removeChoiceLabel$()"
                @click="removeRadioChoice(wKey, cIdx)"
              />
            </div>
            <KButton
              :text="addChoiceAction$()"
              appearance="flat-button"
              icon="plus"
              size="small"
              @click="addRadioChoice(wKey)"
            />
          </div>

          <!-- WIDGET TYPE 4: SEQUENCE ORDERER -->
          <div
            v-else-if="widgets[wKey]?.type === 'orderer'"
            class="widget-orderer-editor"
          >
            <p :style="{ margin: '0 0 8px', fontSize: '0.85rem', color: $themeTokens.annotation }">
              {{ ordererItemsHelp$() }}
            </p>
            <div
              v-for="(item, oIdx) in widgets[wKey].options.correctOptions"
              :key="`order-${oIdx}`"
              class="order-item-row mb-8"
              style="display: flex; align-items: center; gap: 8px;"
            >
              <span
                class="order-badge"
                :style="{
                  backgroundColor: $themePalette.grey.v_200,
                  padding: '4px 8px',
                  borderRadius: '4px',
                  fontWeight: 'bold',
                  fontSize: '0.85rem',
                }"
              >
                {{ oIdx + 1 }}
              </span>
              <div style="flex-grow: 1;">
                <KTextbox
                  v-model="item.content"
                  :label="`${sequenceItemLabel$()} ${oIdx + 1}`"
                />
              </div>
              <KIconButton
                icon="back"
                class="rotate-up"
                size="small"
                :disabled="oIdx === 0"
                :ariaLabel="moveUpLabel$()"
                @click="moveOrderItem(wKey, oIdx, -1)"
              />
              <KIconButton
                icon="forward"
                class="rotate-down"
                size="small"
                :disabled="oIdx === widgets[wKey].options.correctOptions.length - 1"
                :ariaLabel="moveDownLabel$()"
                @click="moveOrderItem(wKey, oIdx, 1)"
              />
              <KIconButton
                icon="trash"
                size="small"
                :disabled="widgets[wKey].options.correctOptions.length <= 2"
                :ariaLabel="removeChoiceLabel$()"
                @click="removeOrderItem(wKey, oIdx)"
              />
            </div>
            <KButton
              :text="addSequenceItemAction$()"
              appearance="flat-button"
              icon="plus"
              size="small"
              @click="addOrderItem(wKey)"
            />
          </div>

          <!-- WIDGET TYPE 5: CONCEPT CATEGORIZER -->
          <div
            v-else-if="widgets[wKey]?.type === 'categorizer'"
            class="widget-categorizer-editor"
          >
            <div class="categories-setup mb-16">
              <h5 :style="{ margin: '0 0 8px', color: $themeTokens.text }">
                {{ categoryColumnsTitle$() }}
              </h5>
              <div
                v-for="(cat, cIdx) in widgets[wKey].options.categories"
                :key="`cat-col-${cIdx}`"
                class="mb-6"
                style="display: flex; align-items: center; gap: 8px;"
              >
                <div style="flex-grow: 1;">
                  <KTextbox
                    v-model="widgets[wKey].options.categories[cIdx]"
                    :label="`${categoryColumnLabel$()} ${cIdx + 1}`"
                  />
                </div>
                <KIconButton
                  icon="trash"
                  size="small"
                  :disabled="widgets[wKey].options.categories.length <= 2"
                  :ariaLabel="removeChoiceLabel$()"
                  @click="removeCategory(wKey, cIdx)"
                />
              </div>
              <KButton
                :text="addCategoryColumnAction$()"
                appearance="flat-button"
                icon="plus"
                size="small"
                @click="addCategory(wKey)"
              />
            </div>

            <div class="items-classification-setup">
              <h5 :style="{ margin: '0 0 8px', color: $themeTokens.text }">
                {{ itemsToClassifyTitle$() }}
              </h5>
              <div
                v-for="(itemText, iIdx) in widgets[wKey].options.items"
                :key="`cat-item-${iIdx}`"
                class="item-mapping-row mb-10"
                style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;"
              >
                <div style="flex: 2; min-width: 200px;">
                  <KTextbox
                    v-model="widgets[wKey].options.items[iIdx]"
                    :label="`${itemToClassifyLabel$()} ${iIdx + 1}`"
                  />
                </div>
                <div style="flex: 1; min-width: 160px;">
                  <select
                    v-model="widgets[wKey].options.values[iIdx]"
                    class="category-select"
                    :style="{
                      width: '100%',
                      padding: '8px',
                      borderRadius: '4px',
                      borderColor: $themeTokens.fineLine,
                      backgroundColor: $themeTokens.surface,
                      color: $themeTokens.text,
                    }"
                  >
                    <option
                      v-for="(catName, cIdx) in widgets[wKey].options.categories"
                      :key="`opt-cat-${cIdx}`"
                      :value="cIdx"
                    >
                      {{ catName || `${categoryColumnLabel$()} ${cIdx + 1}` }}
                    </option>
                  </select>
                </div>
                <KIconButton
                  icon="trash"
                  size="small"
                  :disabled="widgets[wKey].options.items.length <= 1"
                  :ariaLabel="removeChoiceLabel$()"
                  @click="removeCategorizerItem(wKey, iIdx)"
                />
              </div>
              <KButton
                :text="addItemToClassifyAction$()"
                appearance="flat-button"
                icon="plus"
                size="small"
                @click="addCategorizerItem(wKey)"
              />
            </div>
          </div>

          <!-- WIDGET TYPE 6: MATCHING PAIRS -->
          <div
            v-else-if="widgets[wKey]?.type === 'matcher'"
            class="widget-matcher-editor"
          >
            <div class="matcher-headers-row mb-12" style="display: flex; gap: 12px;">
              <div style="flex: 1;">
                <KTextbox
                  v-model="widgets[wKey].options.leftHeader"
                  :label="leftColumnHeaderLabel$()"
                  placeholder="e.g. Term / Event"
                />
              </div>
              <div style="flex: 1;">
                <KTextbox
                  v-model="widgets[wKey].options.rightHeader"
                  :label="rightColumnHeaderLabel$()"
                  placeholder="e.g. Definition / Date"
                />
              </div>
            </div>

            <div
              v-for="(pair, pIdx) in widgets[wKey].options.left"
              :key="`match-${pIdx}`"
              class="matcher-pair-row mb-8"
              style="display: flex; align-items: center; gap: 8px;"
            >
              <div style="flex: 1;">
                <KTextbox
                  v-model="widgets[wKey].options.left[pIdx]"
                  :label="`${leftItemLabel$()} ${pIdx + 1}`"
                />
              </div>
              <span :style="{ color: $themeTokens.annotation, fontWeight: 'bold' }">⇄</span>
              <div style="flex: 1;">
                <KTextbox
                  v-model="widgets[wKey].options.right[pIdx]"
                  :label="`${matchingRightItemLabel$()} ${pIdx + 1}`"
                />
              </div>
              <KIconButton
                icon="trash"
                size="small"
                :disabled="widgets[wKey].options.left.length <= 2"
                :ariaLabel="removeChoiceLabel$()"
                @click="removeMatcherPair(wKey, pIdx)"
              />
            </div>
            <KButton
              :text="addMatchingPairAction$()"
              appearance="flat-button"
              icon="plus"
              size="small"
              @click="addMatcherPair(wKey)"
            />
          </div>

          <!-- WIDGET TYPE 7: MATH EXPRESSION / NUMERIC INPUT -->
          <div
            v-else-if="widgets[wKey]?.type === 'expression' || widgets[wKey]?.type === 'numeric-input'"
            class="widget-math-editor"
          >
            <KTextbox
              v-model="widgets[wKey].options.value"
              :label="correctAnswerExpressionLabel$()"
              placeholder="e.g. 2x + 5 or 42"
              class="mb-12"
            />
            <p :style="{ margin: 0, fontSize: '0.85rem', color: $themeTokens.annotation }">
              {{ mathInputTip$() }}
            </p>
          </div>
        </div>
      </div>

      <!-- Progressive Step-by-Step Hints Section -->
      <div
        class="hints-card mb-20"
        :style="{
          backgroundColor: $themeTokens.surface,
          border: `1px solid ${$themeTokens.fineLine}`,
          borderRadius: '8px',
          padding: '16px',
        }"
      >
        <div class="hints-header-row mb-12">
          <div>
            <h4 :style="{ margin: '0 0 4px', color: $themeTokens.text }">
              {{ progressiveHintsTitle$() }} ({{ hints.length }})
            </h4>
            <p :style="{ margin: 0, color: $themeTokens.annotation, fontSize: '0.85rem' }">
              {{ progressiveHintsSubtitle$() }}
            </p>
          </div>
          <KButton
            :text="addHintAction$()"
            icon="plus"
            appearance="flat-button"
            @click="addHint"
          />
        </div>

        <div
          v-for="(hint, hIdx) in hints"
          :key="`hint-${hIdx}`"
          class="hint-row-card mb-12"
          :style="{
            backgroundColor: $themePalette.grey.v_100,
            border: `1px solid ${$themeTokens.fineLine}`,
            borderRadius: '6px',
            padding: '12px',
          }"
        >
          <div class="hint-card-top mb-8" style="display: flex; justify-content: space-between; align-items: center;">
            <strong :style="{ color: $themeTokens.text }">
              {{ hintStepLabel$() }} {{ hIdx + 1 }}
            </strong>
            <KIconButton
              icon="trash"
              size="small"
              :ariaLabel="removeHintLabel$()"
              @click="removeHint(hIdx)"
            />
          </div>
          <KTextbox
            v-model="hint.content"
            :label="`${hintContentLabel$()} ${hIdx + 1}`"
            :textArea="true"
            :rows="2"
            placeholder="Explain the step, vocabulary hint, or historical clue..."
          />
        </div>
      </div>
    </div>

    <!-- TAB 2: INTERACTIVE LIVE PREVIEW -->
    <div
      v-else-if="studioMode === 'preview'"
      class="preview-mode-wrapper mb-20"
    >
      <div
        class="preview-header-banner mb-12"
        :style="{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: $themePalette.grey.v_100,
          border: `1px solid ${$themeTokens.fineLine}`,
          borderRadius: '8px',
          padding: '12px 16px',
        }"
      >
        <div>
          <span :style="{ fontWeight: 'bold', color: $themeTokens.text }">
            {{ livePreviewBannerTitle$() }}
          </span>
          <p :style="{ margin: '2px 0 0', color: $themeTokens.annotation, fontSize: '0.85rem' }">
            {{ livePreviewBannerSubtitle$() }}
          </p>
        </div>
        <KButton
          :text="refreshPreviewAction$()"
          icon="refresh"
          appearance="flat-button"
          @click="refreshLivePreview"
        />
      </div>

      <!-- Live Perseus Renderer Mount -->
      <div
        class="live-perseus-container"
        :style="{
          backgroundColor: $themeTokens.surface,
          border: `1px solid ${$themeTokens.fineLine}`,
          borderRadius: '8px',
          padding: '24px',
          minHeight: '480px',
        }"
      >
        <component
          :is="perseusViewerComponent"
          v-if="perseusViewerComponent && compiledPerseusItem"
          :key="previewRenderKey"
          :itemData="compiledPerseusItem"
          :interactive="true"
          :lang="currentLocale"
          @answerGiven="onPreviewAnswerGiven"
          @interaction="onPreviewInteraction"
        />
        <div
          v-else
          class="preview-fallback-container"
          style="text-align: center; padding: 40px;"
        >
          <KCircularLoader :delay="false" />
          <p :style="{ marginTop: '12px', color: $themeTokens.annotation }">
            {{ loadingPerseusPreviewText$() }}
          </p>
        </div>

        <!-- Preview Feedback Banner -->
        <div
          v-if="previewResult"
          class="preview-result-banner mt-16"
          :style="{
            padding: '12px 16px',
            borderRadius: '6px',
            backgroundColor: previewResult.correct ? '#f0fdf4' : '#fef2f2',
            border: `1px solid ${previewResult.correct ? '#bbf7d0' : '#fecaca'}`,
            color: previewResult.correct ? '#15803d' : '#dc2626',
            fontWeight: 'bold',
          }"
        >
          <KIcon :icon="previewResult.correct ? 'check' : 'close'" class="mr-8" />
          <span>{{ previewResult.correct ? previewAnswerCorrectNotice$() : previewAnswerIncorrectNotice$() }}</span>
        </div>
      </div>
    </div>

    <!-- TAB 3: RAW PERSEUS JSON INSPECTOR -->
    <div
      v-else
      class="json-mode-wrapper mb-20"
    >
      <div
        class="json-header-banner mb-12"
        :style="{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: $themePalette.grey.v_100,
          border: `1px solid ${$themeTokens.fineLine}`,
          borderRadius: '8px',
          padding: '12px 16px',
        }"
      >
        <p :style="{ margin: 0, color: $themeTokens.annotation, fontSize: '0.85rem' }">
          {{ rawJsonHelpText$() }}
        </p>
        <KButton
          :text="applyJsonChangesAction$()"
          icon="check"
          appearance="flat-button"
          :primary="true"
          @click="applyRawJsonChanges"
        />
      </div>

      <KTextbox
        v-model="rawJsonString"
        :label="perseusJsonLabel$()"
        :textArea="true"
        :rows="18"
        style="font-family: monospace; font-size: 0.9rem;"
      />
    </div>
  </div>

</template>


<script>

  import { ref, computed, onMounted } from 'vue';
  import { createTranslator } from 'kolibri/utils/i18n';
  import useSnackbar from 'kolibri/composables/useSnackbar';
  import Vue from 'vue';

  const strings = createTranslator('PerseusActivityStudioStrings', {
    titleLabel: {
      message: 'Activity Title',
      context: 'Title of the Perseus activity',
    },
    subjectLabel: {
      message: 'Subject Discipline',
      context: 'Subject category selector',
    },
    descriptionLabel: {
      message: 'Description (Optional)',
      context: 'Description input',
    },
    templateLibraryTitle: {
      message: 'Multi-Subject Template Library',
      context: 'Title of template section',
    },
    templateLibrarySubtitle: {
      message:
        'Choose a ready-to-use interactive template for Language Arts, History, Science, Math, or Logic.',
      context: 'Subtitle of template section',
    },
    visualEditorModeLabel: {
      message: 'Visual Studio Builder',
      context: 'Editor tab mode',
    },
    interactivePreviewModeLabel: {
      message: 'Interactive Live Preview',
      context: 'Live preview tab mode',
    },
    rawJsonModeLabel: {
      message: 'Perseus JSON Code',
      context: 'Raw JSON tab mode',
    },
    questionPromptHeader: {
      message: 'Question Prompt & Narrative',
      context: 'Question prompt section title',
    },
    promptHelpText: {
      message: 'Use markdown for formatting and insert widget tags like [[☃ radio 1]] or [[☃ passage 1]].',
      context: 'Instructions for prompt',
    },
    insertWidgetPrompt: {
      message: 'Insert Widget',
      context: 'Toolbar prompt',
    },
    questionContentLabel: {
      message: 'Prompt Content (Markdown + Widget Tags)',
      context: 'Textbox label',
    },
    widgetConfigurationsHeader: {
      message: 'Configured Widgets in Activity',
      context: 'Header for widget configuration cards',
    },
    removeWidgetAction: {
      message: 'Remove Widget',
      context: 'Button to remove a widget',
    },
    passageTitleLabel: {
      message: 'Passage Title',
      context: 'Title of reading passage',
    },
    passageTextLabel: {
      message: 'Passage Text',
      context: 'Text content of reading passage',
    },
    footnotesOptionalLabel: {
      message: 'Footnotes (Optional)',
      context: 'Footnotes for reading passage',
    },
    dropdownChoicesHelp: {
      message: 'Select the radio button next to the choice that represents the correct answer.',
      context: 'Help text for dropdown choices',
    },
    choiceLabel: {
      message: 'Choice',
      context: 'Choice text label',
    },
    markAsCorrectLabel: {
      message: 'Mark as correct answer',
      context: 'Radio tooltip',
    },
    removeChoiceLabel: {
      message: 'Remove Choice',
      context: 'Button tooltip',
    },
    addChoiceAction: {
      message: '+ Add Choice',
      context: 'Button to add choice',
    },
    allowMultipleAnswersLabel: {
      message: 'Allow multiple correct answers (Checkboxes)',
      context: 'Checkbox setting',
    },
    randomizeChoicesLabel: {
      message: 'Randomize choice order for learners',
      context: 'Checkbox setting',
    },
    ordererItemsHelp: {
      message: 'Enter items in their CORRECT sequential order. They will be shuffled when presented to learners.',
      context: 'Help text for orderer widget',
    },
    sequenceItemLabel: {
      message: 'Sequence Step',
      context: 'Label for orderer item',
    },
    moveUpLabel: {
      message: 'Move Up',
      context: 'Button tooltip',
    },
    moveDownLabel: {
      message: 'Move Down',
      context: 'Button tooltip',
    },
    addSequenceItemAction: {
      message: '+ Add Sequence Step',
      context: 'Button to add sequence step',
    },
    categoryColumnsTitle: {
      message: 'Category Bins / Columns',
      context: 'Section title for categorizer bins',
    },
    categoryColumnLabel: {
      message: 'Category Column',
      context: 'Label for category column',
    },
    addCategoryColumnAction: {
      message: '+ Add Category Column',
      context: 'Button to add category column',
    },
    itemsToClassifyTitle: {
      message: 'Items & Concepts to Classify',
      context: 'Section title for items to classify',
    },
    itemToClassifyLabel: {
      message: 'Item / Concept',
      context: 'Label for item to classify',
    },
    addItemToClassifyAction: {
      message: '+ Add Item to Classify',
      context: 'Button to add item to classify',
    },
    leftColumnHeaderLabel: {
      message: 'Left Column Header',
      context: 'Header for left matcher column',
    },
    rightColumnHeaderLabel: {
      message: 'Right Column Header',
      context: 'Header for right matcher column',
    },
    leftItemLabel: {
      message: 'Left Item',
      context: 'Label for left matching item',
    },
    matchingRightItemLabel: {
      message: 'Matching Right Item',
      context: 'Label for right matching item',
    },
    addMatchingPairAction: {
      message: '+ Add Matching Pair',
      context: 'Button to add matching pair',
    },
    correctAnswerExpressionLabel: {
      message: 'Correct Formula / Expression',
      context: 'Input for mathematical expression',
    },
    mathInputTip: {
      message: 'Learners can enter algebraic notation or numbers with the interactive math keypad.',
      context: 'Tip for math input',
    },
    progressiveHintsTitle: {
      message: 'Progressive Step-by-Step Hints',
      context: 'Section title for hints',
    },
    progressiveHintsSubtitle: {
      message: 'Learners can reveal hints sequentially if they get stuck during the activity.',
      context: 'Subtitle for hints',
    },
    addHintAction: {
      message: '+ Add Step Hint',
      context: 'Button to add hint',
    },
    hintStepLabel: {
      message: 'Hint Step',
      context: 'Label for hint step',
    },
    removeHintLabel: {
      message: 'Remove Hint',
      context: 'Button tooltip',
    },
    hintContentLabel: {
      message: 'Hint Content',
      context: 'Label for hint text',
    },
    livePreviewBannerTitle: {
      message: 'Interactive Learner Preview',
      context: 'Preview banner title',
    },
    livePreviewBannerSubtitle: {
      message: 'Test interacting, selecting choices, ordering items, and answering exactly as learners will.',
      context: 'Preview banner subtitle',
    },
    refreshPreviewAction: {
      message: 'Reset Preview',
      context: 'Button to reset preview',
    },
    loadingPerseusPreviewText: {
      message: 'Initializing Perseus interactive renderer...',
      context: 'Loading text for preview',
    },
    previewAnswerCorrectNotice: {
      message: 'Excellent! Your answer is correct.',
      context: 'Notice when preview answer is correct',
    },
    previewAnswerIncorrectNotice: {
      message: 'Keep trying! That answer is not quite right.',
      context: 'Notice when preview answer is incorrect',
    },
    rawJsonHelpText: {
      message: 'Directly view or paste standard Perseus item JSON specification.',
      context: 'Help text for JSON mode',
    },
    applyJsonChangesAction: {
      message: 'Apply JSON to Editor',
      context: 'Button to apply JSON changes',
    },
    perseusJsonLabel: {
      message: 'Perseus Item JSON',
      context: 'Textbox label for JSON',
    },
    jsonParseErrorNotice: {
      message: 'Invalid JSON format. Please check syntax.',
      context: 'Snackbar error message',
    },
    jsonAppliedSuccessNotice: {
      message: 'Perseus JSON successfully applied!',
      context: 'Snackbar success message',
    },
  });

  // MULTI-SUBJECT TEMPLATES LIBRARY
  const TEMPLATES = [
    {
      id: 'reading_passage',
      subject: 'language_arts',
      subjectTag: 'Language Arts',
      icon: '📖',
      name: 'Reading Comprehension & Analysis',
      description: 'Side-by-side passage with line numbers, text analysis, and comprehension questions.',
      title: 'Reading Analysis: The Gettysburg Address',
      desc: 'Examine Lincoln\'s famous speech and answer questions regarding its central themes.',
      content:
        'Read the following historical document carefully and answer the questions below.\n\n[[☃ passage 1]]\n\nWhat is the central theme of the opening paragraph?\n\n[[☃ radio 1]]',
      widgets: {
        'passage 1': {
          type: 'passage',
          options: {
            passageTitle: 'The Gettysburg Address (1863)',
            passageText:
              'Four score and seven years ago our fathers brought forth on this continent, a new nation, conceived in Liberty, and dedicated to the proposition that all men are created equal.\n\nNow we are engaged in a great civil war, testing whether that nation, or any nation so conceived and so dedicated, can long endure. We are met on a great battle-field of that war. We have come to dedicate a portion of that field, as a final resting place for those who here gave their lives that that nation might live.',
            footnotes: 'Score: An archaic unit of measure representing 20 years.',
          },
        },
        'radio 1': {
          type: 'radio',
          options: {
            choices: [
              { content: 'Reaffirming the foundational principle that all human beings are created equal.', correct: true },
              { content: 'Declaring military victory over Confederate armies in Pennsylvania.', correct: false },
              { content: 'Outlining economic reconstruction plans for the southern states.', correct: false },
              { content: 'Proposing foreign diplomatic treaties with European nations.', correct: false },
            ],
            multipleSelect: false,
            randomize: true,
          },
        },
      },
      hints: [
        { content: 'Review the very first sentence: "dedicated to the proposition that all men are created equal."' },
        { content: 'Lincoln emphasizes enduring dedication to equality as the cornerstone of the nation.' },
      ],
    },
    {
      id: 'grammar_cloze',
      subject: 'language_arts',
      subjectTag: 'Language Arts',
      icon: '✍️',
      name: 'Grammar & Context Cloze',
      description: 'Paragraph with embedded inline dropdowns to test correct verb tense and prepositions.',
      title: 'Grammar in Context: Past Tense & Prepositions',
      desc: 'Complete the sentences by selecting the correct grammatical forms.',
      content:
        'Yesterday, the students [[☃ dropdown 1]] to the natural history museum. When they arrived, they gathered [[☃ dropdown 2]] the grand entrance hall.',
      widgets: {
        'dropdown 1': {
          type: 'dropdown',
          options: {
            choices: [
              { content: 'traveled', correct: true },
              { content: 'travels', correct: false },
              { content: 'will travel', correct: false },
              { content: 'traveling', correct: false },
            ],
          },
        },
        'dropdown 2': {
          type: 'dropdown',
          options: {
            choices: [
              { content: 'inside', correct: true },
              { content: 'between', correct: false },
              { content: 'throughout', correct: false },
              { content: 'onto', correct: false },
            ],
          },
        },
      },
      hints: [
        { content: 'The word "Yesterday" signals an action completed in the past.' },
      ],
    },
    {
      id: 'vocab_categorizer',
      subject: 'language_arts',
      subjectTag: 'Language Arts',
      icon: '🗂️',
      name: 'Vocabulary Parts of Speech Sorter',
      description: 'Sort academic vocabulary terms into grammatical categories (Nouns, Verbs, Adjectives).',
      title: 'Classifying Academic Vocabulary by Part of Speech',
      desc: 'Categorize each vocabulary term into its correct grammatical category.',
      content: 'Sort the following vocabulary words into their correct parts of speech:\n\n[[☃ categorizer 1]]',
      widgets: {
        'categorizer 1': {
          type: 'categorizer',
          options: {
            categories: ['Noun', 'Verb', 'Adjective', 'Adverb'],
            items: ['Eloquent', 'Perseverance', 'Accelerate', 'Meticulously'],
            values: [2, 0, 1, 3], // 2 = Adjective, 0 = Noun, 1 = Verb, 3 = Adverb
          },
        },
      },
      hints: [
        { content: 'Eloquent describes a speaker or expression (adjective).' },
        { content: 'Words ending in -ly often function as adverbs modifying an action.' },
      ],
    },
    {
      id: 'history_timeline',
      subject: 'history',
      subjectTag: 'History & Civics',
      icon: '⏳',
      name: 'Historical Event Timeline',
      description: 'Order pivotal historical events, treaties, or milestones in sequential order.',
      title: 'Timeline: Major Milestones of the American Revolution',
      desc: 'Drag and arrange the events in correct chronological order.',
      content:
        'Place the following revolutionary events in the correct chronological order from earliest to latest:\n\n[[☃ orderer 1]]',
      widgets: {
        'orderer 1': {
          type: 'orderer',
          options: {
            layout: 'vertical',
            correctOptions: [
              { content: 'The Boston Tea Party (1773)' },
              { content: 'The Battles of Lexington and Concord (1775)' },
              { content: 'The Adoption of the Declaration of Independence (1776)' },
              { content: 'The Surrender of Lord Cornwallis at Yorktown (1781)' },
              { content: 'The Signing of the Treaty of Paris (1783)' },
            ],
          },
        },
      },
      hints: [
        { content: 'The Boston Tea Party occurred prior to active military engagements.' },
        { content: 'The Treaty of Paris concluded the war in 1783.' },
      ],
    },
    {
      id: 'civics_categorizer',
      subject: 'history',
      subjectTag: 'History & Civics',
      icon: '🏛️',
      name: 'Government Powers & Branches',
      description: 'Sort constitutional responsibilities into Legislative, Executive, and Judicial branches.',
      title: 'Branches of Government: Separation of Powers',
      desc: 'Categorize constitutional powers according to the respective branch of government.',
      content: 'Categorize each government function under the correct branch:\n\n[[☃ categorizer 1]]',
      widgets: {
        'categorizer 1': {
          type: 'categorizer',
          options: {
            categories: ['Legislative (Congress)', 'Executive (President)', 'Judicial (Supreme Court)'],
            items: [
              'Originates and passes federal laws',
              'Serves as Commander-in-Chief of armed forces',
              'Interprets constitutional validity of statutes',
              'Negotiates treaties with foreign powers',
            ],
            values: [0, 1, 2, 1],
          },
        },
      },
      hints: [
        { content: 'Article I establishes Congress and the lawmaking power.' },
        { content: 'Article II designates the President as Commander-in-Chief.' },
      ],
    },
    {
      id: 'science_process',
      subject: 'science',
      subjectTag: 'Science',
      icon: '🔬',
      name: 'Scientific Method & Life Cycles',
      description: 'Order experimental procedure steps or biological metamorphosis stages.',
      title: 'Sequential Steps of the Scientific Method',
      desc: 'Arrange the scientific inquiry steps in the standard empirical sequence.',
      content:
        'Order the sequential steps of a scientific investigation from start to finish:\n\n[[☃ orderer 1]]',
      widgets: {
        'orderer 1': {
          type: 'orderer',
          options: {
            layout: 'vertical',
            correctOptions: [
              { content: 'Make an observation and ask a question' },
              { content: 'Formulate a testable hypothesis' },
              { content: 'Design and execute a controlled experiment' },
              { content: 'Collect and analyze experimental data' },
              { content: 'Draw conclusions and share findings' },
            ],
          },
        },
      },
      hints: [
        { content: 'Empirical inquiry always begins with an initial observation.' },
        { content: 'Hypotheses must be established before conducting experiments to test them.' },
      ],
    },
    {
      id: 'science_matter',
      subject: 'science',
      subjectTag: 'Science',
      icon: '🧪',
      name: 'Matter & Taxonomy Classification',
      description: 'Sort physical states of matter, biological taxonomy, or chemical properties.',
      title: 'Classification of Matter: States of Matter',
      desc: 'Group the given substances into Solid, Liquid, or Gas at standard temperature and pressure.',
      content: 'Classify each substance under its state of matter at room temperature:\n\n[[☃ categorizer 1]]',
      widgets: {
        'categorizer 1': {
          type: 'categorizer',
          options: {
            categories: ['Solid', 'Liquid', 'Gas'],
            items: ['Copper Coin', 'Olive Oil', 'Helium', 'Water', 'Iron Nail', 'Oxygen'],
            values: [0, 1, 2, 1, 0, 2],
          },
        },
      },
      hints: [
        { content: 'Metals such as copper and iron maintain a fixed shape and volume.' },
        { content: 'Gases like helium and oxygen expand to fill any container.' },
      ],
    },
    {
      id: 'math_equation',
      subject: 'math',
      subjectTag: 'Mathematics',
      icon: '📐',
      name: 'Algebraic Equation with Hints',
      description: 'Formula solving with mathematical notation and progressive step-by-step guidance.',
      title: 'Solving Linear Equations: One-Variable',
      desc: 'Find the value of $x$ that satisfies the linear equation.',
      content: 'Solve for $x$ in the following equation:\n\n$$3x + 15 = 42$$\n\n$x =$ [[☃ numeric-input 1]]',
      widgets: {
        'numeric-input 1': {
          type: 'numeric-input',
          options: {
            answers: [
              { value: 9, status: 'correct', message: '' },
            ],
            size: 'normal',
          },
        },
      },
      hints: [
        { content: 'Step 1: Subtract 15 from both sides of the equation:\n\n$$3x = 42 - 15 = 27$$' },
        { content: 'Step 2: Divide both sides by 3:\n\n$$x = \\frac{27}{3} = 9$$' },
      ],
    },
    {
      id: 'blank_custom',
      subject: 'all',
      subjectTag: 'Custom',
      icon: '✨',
      name: 'Blank Custom Interactive Canvas',
      description: 'Start with a clean slate and build your own multi-widget interactive exercise.',
      title: 'Custom Interactive Exercise',
      desc: 'A flexible custom interactive Perseus exercise.',
      content: 'Enter your instructions or prompt here.\n\n[[☃ radio 1]]',
      widgets: {
        'radio 1': {
          type: 'radio',
          options: {
            choices: [
              { content: 'Choice A', correct: true },
              { content: 'Choice B', correct: false },
            ],
            multipleSelect: false,
            randomize: false,
          },
        },
      },
      hints: [],
    },
  ];

  export default {
    name: 'PerseusActivityStudio',
    props: {
      initialItem: {
        type: Object,
        default: null,
      },
      initialTitle: {
        type: String,
        default: '',
      },
      initialDescription: {
        type: String,
        default: '',
      },
    },
    emits: ['change', 'save'],
    setup(props, { emit }) {
      const { createSnackbar } = useSnackbar();

      const title = ref(props.initialTitle || 'Reading & Text Analysis');
      const titleError = ref('');
      const description = ref(props.initialDescription || '');
      const selectedSubject = ref('all');
      const activeTemplateId = ref('reading_passage');
      const studioMode = ref('editor'); // 'editor' | 'preview' | 'json'
      const previewRenderKey = ref(0);
      const previewResult = ref(null);
      const rawJsonString = ref('');

      const questionContent = ref(TEMPLATES[0].content);
      const widgets = ref(JSON.parse(JSON.stringify(TEMPLATES[0].widgets)));
      const hints = ref(JSON.parse(JSON.stringify(TEMPLATES[0].hints)));

      const currentLocale = ref('en');

      const subjectOptions = computed(() => [
        { value: 'all', label: 'All Subjects' },
        { value: 'language_arts', label: '📖 Language Arts & Literature' },
        { value: 'history', label: '🏛️ History & Social Studies' },
        { value: 'science', label: '🔬 Natural & Physical Sciences' },
        { value: 'math', label: '📐 Mathematics' },
      ]);

      const filteredTemplates = computed(() => {
        if (selectedSubject.value === 'all') {
          return TEMPLATES;
        }
        return TEMPLATES.filter(
          t => t.subject === selectedSubject.value || t.subject === 'all',
        );
      });

      const detectedWidgetKeys = computed(() => {
        return Object.keys(widgets.value || {});
      });

      const perseusViewerComponent = computed(() => {
        // If Vue has registered exercise_viewer component globally, use it!
        if (Vue.options.components && Vue.options.components['exercise_viewer']) {
          return 'exercise_viewer';
        }
        return null;
      });

      const compiledPerseusItem = computed(() => {
        return {
          question: {
            content: questionContent.value,
            images: {},
            widgets: widgets.value,
          },
          hints: hints.value,
          answerArea: {
            calculator: false,
            periodicTable: false,
          },
        };
      });

      function emitChanges() {
        emit('change', {
          title: title.value,
          description: description.value,
          subject: selectedSubject.value,
          perseusItem: compiledPerseusItem.value,
          item: compiledPerseusItem.value,
          jsonString: JSON.stringify(compiledPerseusItem.value, null, 2),
        });
      }

      function handleSubjectFilterChange() {
        // Filter change keeps current activity unless user selects a template
      }

      function applyTemplate(tpl) {
        activeTemplateId.value = tpl.id;
        if (tpl.subject) {
          selectedSubject.value = tpl.subject;
        }
        title.value = tpl.title;
        description.value = tpl.desc;
        questionContent.value = tpl.content;
        widgets.value = JSON.parse(JSON.stringify(tpl.widgets));
        hints.value = JSON.parse(JSON.stringify(tpl.hints));
        previewResult.value = null;
        emitChanges();
      }

      function getWidgetIcon(type) {
        if (type === 'passage') return '📖';
        if (type === 'radio') return '🔘';
        if (type === 'dropdown') return '🔽';
        if (type === 'orderer') return '🔢';
        if (type === 'categorizer') return '🗂️';
        if (type === 'matcher') return '🔗';
        if (type === 'expression' || type === 'numeric-input') return '📐';
        return '⚙️';
      }

      function getNextWidgetIndex(type) {
        let maxIndex = 0;
        const prefix = `${type} `;
        for (const k of Object.keys(widgets.value || {})) {
          if (k.startsWith(prefix)) {
            const num = parseInt(k.replace(prefix, ''), 10);
            if (!isNaN(num) && num > maxIndex) {
              maxIndex = num;
            }
          }
        }
        return maxIndex + 1;
      }

      function insertWidgetPlaceholder(type) {
        const nextIdx = getNextWidgetIndex(type);
        const widgetKey = `${type} ${nextIdx}`;
        const placeholder = `[[☃ ${widgetKey}]]`;

        questionContent.value += `\n\n${placeholder}`;

        // Create default configuration based on widget type
        if (type === 'passage') {
          widgets.value[widgetKey] = {
            type: 'passage',
            options: {
              passageTitle: 'Reading Passage Title',
              passageText: 'Enter reading passage or historical excerpt here...',
              footnotes: '',
            },
          };
        } else if (type === 'dropdown') {
          widgets.value[widgetKey] = {
            type: 'dropdown',
            options: {
              choices: [
                { content: 'Option 1', correct: true },
                { content: 'Option 2', correct: false },
                { content: 'Option 3', correct: false },
              ],
            },
          };
        } else if (type === 'radio') {
          widgets.value[widgetKey] = {
            type: 'radio',
            options: {
              choices: [
                { content: 'Choice A', correct: true },
                { content: 'Choice B', correct: false },
                { content: 'Choice C', correct: false },
              ],
              multipleSelect: false,
              randomize: true,
            },
          };
        } else if (type === 'orderer') {
          widgets.value[widgetKey] = {
            type: 'orderer',
            options: {
              layout: 'vertical',
              correctOptions: [
                { content: 'Step 1' },
                { content: 'Step 2' },
                { content: 'Step 3' },
              ],
            },
          };
        } else if (type === 'categorizer') {
          widgets.value[widgetKey] = {
            type: 'categorizer',
            options: {
              categories: ['Category A', 'Category B'],
              items: ['Concept 1', 'Concept 2'],
              values: [0, 1],
            },
          };
        } else if (type === 'matcher') {
          widgets.value[widgetKey] = {
            type: 'matcher',
            options: {
              leftHeader: 'Column A',
              rightHeader: 'Column B',
              left: ['Term 1', 'Term 2'],
              right: ['Definition 1', 'Definition 2'],
            },
          };
        } else if (type === 'expression') {
          widgets.value[widgetKey] = {
            type: 'expression',
            options: {
              value: 'x + 1',
            },
          };
        } else if (type === 'numeric-input') {
          widgets.value[widgetKey] = {
            type: 'numeric-input',
            options: {
              answers: [{ value: 42, status: 'correct', message: '' }],
              size: 'normal',
            },
          };
        }

        emitChanges();
      }

      function syncWidgetsFromContent() {
        emitChanges();
      }

      function removeWidget(wKey) {
        // Remove from content text
        const tag = `[[☃ ${wKey}]]`;
        questionContent.value = questionContent.value.replace(tag, '').trim();
        const updated = { ...widgets.value };
        delete updated[wKey];
        widgets.value = updated;
        emitChanges();
      }

      // Dropdown operations
      function setDropdownCorrect(wKey, cIdx) {
        const choices = widgets.value[wKey].options.choices;
        choices.forEach((c, idx) => {
          c.correct = idx === cIdx;
        });
        emitChanges();
      }

      function addDropdownChoice(wKey) {
        widgets.value[wKey].options.choices.push({
          content: `Option ${widgets.value[wKey].options.choices.length + 1}`,
          correct: false,
        });
        emitChanges();
      }

      function removeDropdownChoice(wKey, cIdx) {
        widgets.value[wKey].options.choices.splice(cIdx, 1);
        emitChanges();
      }

      // Radio operations
      function toggleRadioChoiceCorrect(wKey, cIdx) {
        const w = widgets.value[wKey];
        if (!w.options.multipleSelect) {
          w.options.choices.forEach((c, idx) => {
            c.correct = idx === cIdx;
          });
        } else {
          w.options.choices[cIdx].correct = !w.options.choices[cIdx].correct;
        }
        emitChanges();
      }

      function addRadioChoice(wKey) {
        widgets.value[wKey].options.choices.push({
          content: `Choice ${widgets.value[wKey].options.choices.length + 1}`,
          correct: false,
        });
        emitChanges();
      }

      function removeRadioChoice(wKey, cIdx) {
        widgets.value[wKey].options.choices.splice(cIdx, 1);
        emitChanges();
      }

      // Orderer operations
      function addOrderItem(wKey) {
        widgets.value[wKey].options.correctOptions.push({
          content: `Step ${widgets.value[wKey].options.correctOptions.length + 1}`,
        });
        emitChanges();
      }

      function removeOrderItem(wKey, oIdx) {
        widgets.value[wKey].options.correctOptions.splice(oIdx, 1);
        emitChanges();
      }

      function moveOrderItem(wKey, oIdx, delta) {
        const arr = widgets.value[wKey].options.correctOptions;
        const target = oIdx + delta;
        if (target < 0 || target >= arr.length) return;
        const item = arr.splice(oIdx, 1)[0];
        arr.splice(target, 0, item);
        emitChanges();
      }

      // Categorizer operations
      function addCategory(wKey) {
        widgets.value[wKey].options.categories.push(
          `Category ${widgets.value[wKey].options.categories.length + 1}`,
        );
        emitChanges();
      }

      function removeCategory(wKey, cIdx) {
        widgets.value[wKey].options.categories.splice(cIdx, 1);
        // adjust item values if out of range
        widgets.value[wKey].options.values = widgets.value[wKey].options.values.map(val =>
          val >= cIdx ? Math.max(0, val - 1) : val,
        );
        emitChanges();
      }

      function addCategorizerItem(wKey) {
        widgets.value[wKey].options.items.push(
          `Concept ${widgets.value[wKey].options.items.length + 1}`,
        );
        widgets.value[wKey].options.values.push(0);
        emitChanges();
      }

      function removeCategorizerItem(wKey, iIdx) {
        widgets.value[wKey].options.items.splice(iIdx, 1);
        widgets.value[wKey].options.values.splice(iIdx, 1);
        emitChanges();
      }

      // Matcher operations
      function addMatcherPair(wKey) {
        const count = widgets.value[wKey].options.left.length + 1;
        widgets.value[wKey].options.left.push(`Term ${count}`);
        widgets.value[wKey].options.right.push(`Definition ${count}`);
        emitChanges();
      }

      function removeMatcherPair(wKey, pIdx) {
        widgets.value[wKey].options.left.splice(pIdx, 1);
        widgets.value[wKey].options.right.splice(pIdx, 1);
        emitChanges();
      }

      // Hints operations
      function addHint() {
        hints.value.push({
          content: `Hint ${hints.value.length + 1}: Consider the primary clues in the text...`,
        });
        emitChanges();
      }

      function removeHint(hIdx) {
        hints.value.splice(hIdx, 1);
        emitChanges();
      }

      // Tab switching & Preview
      function switchToPreview() {
        studioMode.value = 'preview';
        previewRenderKey.value += 1;
        previewResult.value = null;
      }

      function refreshLivePreview() {
        previewRenderKey.value += 1;
        previewResult.value = null;
      }

      function onPreviewAnswerGiven(answerData) {
        if (answerData && answerData.correct !== undefined) {
          previewResult.value = { correct: answerData.correct };
        }
      }

      function onPreviewInteraction() {
        // live interaction
      }

      function switchToRawJson() {
        rawJsonString.value = JSON.stringify(compiledPerseusItem.value, null, 2);
        studioMode.value = 'json';
      }

      function applyRawJsonChanges() {
        try {
          const parsed = JSON.parse(rawJsonString.value);
          if (parsed && parsed.question) {
            questionContent.value = parsed.question.content || '';
            widgets.value = parsed.question.widgets || {};
            hints.value = parsed.hints || [];
            createSnackbar(strings.jsonAppliedSuccessNotice$());
            emitChanges();
          } else {
            createSnackbar(strings.jsonParseErrorNotice$());
          }
        } catch (e) {
          createSnackbar(strings.jsonParseErrorNotice$());
        }
      }

      onMounted(() => {
        if (props.initialItem && props.initialItem.question) {
          questionContent.value = props.initialItem.question.content || '';
          widgets.value = props.initialItem.question.widgets || {};
          hints.value = props.initialItem.hints || [];
        }
        emitChanges();
      });

      return {
        title,
        titleError,
        description,
        selectedSubject,
        subjectOptions,
        activeTemplateId,
        filteredTemplates,
        studioMode,
        previewRenderKey,
        previewResult,
        rawJsonString,
        questionContent,
        widgets,
        detectedWidgetKeys,
        hints,
        perseusViewerComponent,
        compiledPerseusItem,
        currentLocale,
        handleSubjectFilterChange,
        applyTemplate,
        getWidgetIcon,
        insertWidgetPlaceholder,
        syncWidgetsFromContent,
        removeWidget,
        setDropdownCorrect,
        addDropdownChoice,
        removeDropdownChoice,
        toggleRadioChoiceCorrect,
        addRadioChoice,
        removeRadioChoice,
        addOrderItem,
        removeOrderItem,
        moveOrderItem,
        addCategory,
        removeCategory,
        addCategorizerItem,
        removeCategorizerItem,
        addMatcherPair,
        removeMatcherPair,
        addHint,
        removeHint,
        switchToPreview,
        refreshLivePreview,
        onPreviewAnswerGiven,
        onPreviewInteraction,
        switchToRawJson,
        applyRawJsonChanges,
        ...strings,
      };
    },
  };

</script>


<style lang="scss" scoped>

  .perseus-activity-studio {
    width: 100%;
  }

  .top-row {
    display: flex;
    gap: 16px;
    align-items: flex-start;
    flex-wrap: wrap;
  }

  .title-field {
    flex: 3;
    min-width: 260px;
  }

  .subject-select-field {
    flex: 2;
    min-width: 220px;
  }

  .templates-scroll-row {
    display: flex;
    gap: 12px;
    overflow-x: auto;
    padding-bottom: 8px;
  }

  .template-pill-card {
    flex: 0 0 240px;
    border: 1px solid;
    border-radius: 8px;
    padding: 12px;
    text-align: left;
    cursor: pointer;
    transition: all 0.2s ease-in-out;

    &:hover {
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
  }

  .pill-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
  }

  .tpl-icon {
    font-size: 1.3rem;
  }

  .subject-tag {
    font-size: 0.75rem;
    font-weight: bold;
    padding: 2px 6px;
    border-radius: 4px;
  }

  .tpl-name {
    font-weight: bold;
    font-size: 0.9rem;
    margin-bottom: 4px;
  }

  .tpl-desc {
    font-size: 0.78rem;
    line-height: 1.3;
  }

  .rotate-up {
    transform: rotate(90deg);
  }

  .rotate-down {
    transform: rotate(90deg);
  }

</style>
