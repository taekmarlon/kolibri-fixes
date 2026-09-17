<template>

  <KModal
    :title="modalTitle$()"
    :submitText="addResourceButton$()"
    :cancelText="cancelButton$()"
    :submitDisabled="isSubmitDisabled || isSubmitting"
    size="large"
    @submit="handleSubmit"
    @cancel="$emit('close')"
  >
    <div class="add-custom-resource-modal">
      <!-- Tabs Navigation -->
      <div
        class="tab-button-group"
        :style="{ borderBottom: `1px solid ${$themeTokens.fineLine}` }"
      >
        <KButton
          :text="tabLessonBuilderLabel$()"
          icon="edit"
          :appearance="activeTab === 'builder' ? 'raised-button' : 'flat-button'"
          :primary="activeTab === 'builder'"
          class="tab-btn"
          @click="activeTab = 'builder'"
        />
        <KButton
          :text="tabH5PInteractiveLabel$()"
          icon="html5"
          :appearance="activeTab === 'h5p' ? 'raised-button' : 'flat-button'"
          :primary="activeTab === 'h5p'"
          class="tab-btn"
          @click="activeTab = 'h5p'"
        />
        <KButton
          :text="tabPerseusLabel$()"
          icon="practice"
          :appearance="activeTab === 'perseus' ? 'raised-button' : 'flat-button'"
          :primary="activeTab === 'perseus'"
          class="tab-btn"
          @click="activeTab = 'perseus'"
        />
        <KButton
          :text="tabFilesLabel$()"
          icon="document"
          :appearance="activeTab === 'file' ? 'raised-button' : 'flat-button'"
          :primary="activeTab === 'file'"
          class="tab-btn"
          @click="activeTab = 'file'"
        />
        <KButton
          :text="tabYoutubeLabel$()"
          icon="video"
          :appearance="activeTab === 'youtube' ? 'raised-button' : 'flat-button'"
          :primary="activeTab === 'youtube'"
          class="tab-btn"
          @click="activeTab = 'youtube'"
        />
        <KButton
          :text="tabHtml5Label$()"
          icon="html5"
          :appearance="activeTab === 'html5' ? 'raised-button' : 'flat-button'"
          :primary="activeTab === 'html5'"
          class="tab-btn"
          @click="activeTab = 'html5'"
        />
        <KButton
          :text="tabCardLabel$()"
          icon="topic"
          :appearance="activeTab === 'card' ? 'raised-button' : 'flat-button'"
          :primary="activeTab === 'card'"
          class="tab-btn"
          @click="activeTab = 'card'"
        />
        <KButton
          :text="tabAiLabel$()"
          icon="hint"
          :appearance="activeTab === 'ai' ? 'raised-button' : 'flat-button'"
          :primary="activeTab === 'ai'"
          class="tab-btn"
          @click="activeTab = 'ai'"
        />
      </div>

      <!-- TAB 0: CUSTOM LESSON BUILDER -->
      <div
        v-if="activeTab === 'builder'"
        class="tab-content builder-tab-content"
      >
        <!-- Builder Header Banner -->
        <div
          class="builder-header-banner"
          :style="{
            backgroundColor: $themePalette.grey.v_100,
            border: `1px solid ${$themeTokens.fineLine}`,
            borderRadius: '8px',
            padding: '16px',
            marginBottom: '16px',
          }"
        >
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <div>
              <h3 :style="{ margin: 0, color: $themeTokens.text }">
                {{ builderHeaderTitle$() }}
              </h3>
              <p :style="{ margin: '4px 0 0', color: $themeTokens.annotation, fontSize: '0.9rem' }">
                {{ builderHeaderSubtitle$() }}
              </p>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span
                class="stats-badge"
                :style="{
                  backgroundColor: $themePalette.grey.v_200,
                  color: $themeTokens.text,
                  padding: '4px 10px',
                  borderRadius: '16px',
                  fontWeight: 'bold',
                  fontSize: '0.85rem',
                }"
              >
                {{ builderBlocks.length }} {{ builderBlocks.length === 1 ? 'block' : 'blocks' }}
              </span>
              <KButton
                :text="addBlockAction$()"
                icon="plus"
                :primary="true"
                appearance="raised-button"
                @click="addNewBlock('text')"
              />
            </div>
          </div>
        </div>

        <!-- Lesson Meta Inputs -->
        <div class="mb-16">
          <KTextbox
            v-model="builderTitle"
            :label="titleLabel$()"
            placeholder="e.g. Cell Biology 101: Structure and Organelles"
            :invalid="Boolean(builderTitleError)"
            :invalidText="builderTitleError"
            :autofocus="true"
            @input="builderTitleError = ''"
          />
        </div>

        <div class="mb-16">
          <KTextbox
            v-model="builderDescription"
            :label="descriptionLabel$()"
            placeholder="e.g. Comprehensive reading guide with diagrams and checkpoints"
            :textArea="true"
            rows="2"
          />
        </div>

        <!-- Empty State if no blocks -->
        <div
          v-if="builderBlocks.length === 0"
          class="empty-state-box"
          :style="{
            backgroundColor: $themeTokens.surface,
            border: `2px dashed ${$themeTokens.fineLine}`,
            borderRadius: '8px',
            padding: '32px 16px',
            textAlign: 'center',
            margin: '16px 0',
          }"
        >
          <div
            style="width: 50px; height: 50px; border-radius: 50%; margin: 0 auto 12px; display: flex; align-items: center; justify-content: center;"
            :style="{ backgroundColor: $themePalette.grey.v_100 }"
          >
            <KIcon icon="edit" />
          </div>
          <h4 style="margin: 0 0 6px;">{{ emptyBlocksNotice$() }}</h4>
          <p :style="{ color: $themeTokens.annotation, margin: '0 0 16px' }">
            {{ emptyBlocksPrompt$() }}
          </p>
          <div style="display: flex; gap: 8px; justify-content: center; flex-wrap: wrap;">
            <KButton
              :text="blockTypeHeading$()"
              icon="plus"
              appearance="flat-button"
              @click="addNewBlock('heading')"
            />
            <KButton
              :text="blockTypeText$()"
              icon="plus"
              appearance="flat-button"
              @click="addNewBlock('text')"
            />
            <KButton
              :text="blockTypeImage$()"
              icon="plus"
              appearance="flat-button"
              @click="addNewBlock('image')"
            />
            <KButton
              :text="blockTypeVideo$()"
              icon="plus"
              appearance="flat-button"
              @click="addNewBlock('video')"
            />
            <KButton
              :text="blockTypeCallout$()"
              icon="plus"
              appearance="flat-button"
              @click="addNewBlock('callout')"
            />
            <KButton
              :text="blockTypeCheckpoint$()"
              icon="plus"
              appearance="flat-button"
              @click="addNewBlock('checkpoint')"
            />
          </div>
        </div>

        <!-- Blocks Container -->
        <div
          v-else
          class="builder-blocks-list"
        >
          <div
            v-for="(block, bIndex) in builderBlocks"
            :key="block.id || `b-${bIndex}`"
            class="builder-block-card"
            :class="{ 'is-active': activeBlockIndex === bIndex }"
            :style="{
              backgroundColor: $themeTokens.surface,
              border: activeBlockIndex === bIndex ? `2px solid ${$themeTokens.primary}` : `1px solid ${$themeTokens.fineLine}`,
              borderLeft: activeBlockIndex === bIndex ? `6px solid ${$themeTokens.primary}` : `1px solid ${$themeTokens.fineLine}`,
              borderRadius: '8px',
              padding: '14px',
              marginBottom: '16px',
            }"
            @click="activeBlockIndex = bIndex"
          >
            <!-- Card Top Toolbar -->
            <div
              class="block-card-header"
              :style="{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingBottom: '10px',
                marginBottom: '12px',
                borderBottom: `1px solid ${$themePalette.grey.v_200}`,
              }"
            >
              <div style="display: flex; align-items: center; gap: 6px;">
                <span
                  class="block-number-pill"
                  :style="{
                    backgroundColor: activeBlockIndex === bIndex ? $themeTokens.primary : $themePalette.grey.v_300,
                    color: activeBlockIndex === bIndex ? $themeTokens.textInverted : $themeTokens.text,
                    padding: '2px 8px',
                    borderRadius: '12px',
                    fontWeight: 'bold',
                    fontSize: '0.85rem',
                  }"
                >
                  {{ bIndex + 1 }}
                </span>
                <KIconButton
                  icon="back"
                  class="rotate-up"
                  :ariaLabel="moveUpAction$()"
                  :tooltip="moveUpAction$()"
                  :disabled="bIndex === 0"
                  size="small"
                  @click.stop="moveBlockUp(bIndex)"
                />
                <KIconButton
                  icon="forward"
                  class="rotate-down"
                  :ariaLabel="moveDownAction$()"
                  :tooltip="moveDownAction$()"
                  :disabled="bIndex === builderBlocks.length - 1"
                  size="small"
                  @click.stop="moveBlockDown(bIndex)"
                />
              </div>

              <!-- Block Type Selector -->
              <div style="display: flex; align-items: center; gap: 8px;">
                <select
                  v-model="block.type"
                  class="block-type-select"
                  :style="{
                    padding: '4px 8px',
                    borderRadius: '4px',
                    borderColor: $themeTokens.fineLine,
                    backgroundColor: $themeTokens.surface,
                    color: $themeTokens.text,
                    fontWeight: '600',
                  }"
                  @click.stop
                >
                  <option value="heading">{{ blockTypeHeading$() }}</option>
                  <option value="text">{{ blockTypeText$() }}</option>
                  <option value="image">{{ blockTypeImage$() }}</option>
                  <option value="video">{{ blockTypeVideo$() }}</option>
                  <option value="callout">{{ blockTypeCallout$() }}</option>
                  <option value="checkpoint">{{ blockTypeCheckpoint$() }}</option>
                </select>

                <KIconButton
                  icon="copy"
                  size="small"
                  :tooltip="duplicateBlockAction$()"
                  :ariaLabel="duplicateBlockAction$()"
                  @click.stop="duplicateBlock(bIndex)"
                />
                <KIconButton
                  icon="clear"
                  size="small"
                  :tooltip="deleteBlockAction$()"
                  :ariaLabel="deleteBlockAction$()"
                  @click.stop="removeBlock(bIndex)"
                />
              </div>
            </div>

            <!-- Block Body by Type -->
            <!-- 1. Heading Block -->
            <div v-if="block.type === 'heading'">
              <div class="mb-8">
                <KTextbox
                  v-model="block.title"
                  :label="sectionHeadingLabel$()"
                  :placeholder="sectionHeadingPlaceholder$()"
                />
              </div>
              <div>
                <KTextbox
                  v-model="block.subtitle"
                  :label="sectionSubtitleLabel$()"
                  :placeholder="sectionSubtitlePlaceholder$()"
                />
              </div>
            </div>

            <!-- 2. Text Block -->
            <div v-else-if="block.type === 'text'">
              <KTextbox
                v-model="block.text"
                :label="textContentLabel$()"
                :placeholder="textContentPlaceholder$()"
                :textArea="true"
                rows="4"
              />
            </div>

            <!-- 3. Image / Diagram Block -->
            <div v-else-if="block.type === 'image'">
              <div
                v-if="!block.image_url"
                class="image-upload-zone"
                :style="{
                  border: `2px dashed ${$themeTokens.fineLine}`,
                  borderRadius: '6px',
                  padding: '20px',
                  textAlign: 'center',
                  backgroundColor: $themePalette.grey.v_50,
                  cursor: 'pointer',
                }"
                @click.stop="triggerBlockImageUpload(block)"
              >
                <KIcon icon="image" style="font-size: 28px; margin-bottom: 6px;" />
                <p style="margin: 0; font-weight: 500;">{{ uploadImagePrompt$() }}</p>
              </div>
              <div
                v-else
                class="image-preview-container"
                style="margin-bottom: 8px; position: relative;"
              >
                <img
                  :src="block.image_url"
                  alt="Lesson illustration"
                  style="max-width: 100%; max-height: 240px; border-radius: 6px; display: block; margin: 0 auto;"
                >
                <div style="text-align: center; margin-top: 6px;">
                  <KButton
                    appearance="flat-button"
                    icon="clear"
                    :text="removeImage$()"
                    @click.stop="block.image_url = ''"
                  />
                </div>
              </div>

              <div class="mt-8">
                <KTextbox
                  v-model="block.caption"
                  :label="imageCaptionLabel$()"
                  :placeholder="imageCaptionPlaceholder$()"
                />
              </div>
            </div>

            <!-- 4. Video Embed Block -->
            <div v-else-if="block.type === 'video'">
              <div class="mb-8">
                <KTextbox
                  v-model="block.url"
                  :label="videoUrlLabel$()"
                  placeholder="https://www.youtube.com/watch?v=..."
                />
              </div>
              <div>
                <KTextbox
                  v-model="block.notes"
                  :label="videoNotesLabel$()"
                  placeholder="e.g. Pay close attention to the formula discussed at 2:15"
                />
              </div>
            </div>

            <!-- 5. Callout / Key Concept Block -->
            <div v-else-if="block.type === 'callout'">
              <div style="display: flex; gap: 8px; margin-bottom: 8px; align-items: center;">
                <label :style="{ color: $themeTokens.annotation, fontWeight: '500' }">
                  {{ calloutTypeLabel$() }}:
                </label>
                <select
                  v-model="block.callout_type"
                  :style="{
                    padding: '4px 8px',
                    borderRadius: '4px',
                    borderColor: $themeTokens.fineLine,
                    backgroundColor: $themeTokens.surface,
                    color: $themeTokens.text,
                  }"
                  @click.stop
                >
                  <option value="concept">💡 Key Concept / Definition</option>
                  <option value="tip">🌟 Study Tip</option>
                  <option value="warning">⚠️ Important Warning</option>
                </select>
              </div>
              <div class="mb-8">
                <KTextbox
                  v-model="block.title"
                  :label="calloutTitleLabel$()"
                  :placeholder="calloutTitlePlaceholder$()"
                />
              </div>
              <div>
                <KTextbox
                  v-model="block.text"
                  :label="calloutContentLabel$()"
                  :placeholder="calloutContentPlaceholder$()"
                  :textArea="true"
                  rows="3"
                />
              </div>
            </div>

            <!-- 6. Practice Checkpoint Block -->
            <div v-else-if="block.type === 'checkpoint'">
              <div class="mb-8">
                <KTextbox
                  v-model="block.question"
                  :label="checkpointQuestionLabel$()"
                  :placeholder="checkpointQuestionPlaceholder$()"
                  :textArea="true"
                  rows="2"
                />
              </div>
              <div>
                <KTextbox
                  v-model="block.answer"
                  :label="checkpointAnswerLabel$()"
                  :placeholder="checkpointAnswerPlaceholder$()"
                  :textArea="true"
                  rows="2"
                />
              </div>
            </div>
          </div>

          <!-- Add More Blocks Buttons Toolbar -->
          <div
            class="add-more-blocks-toolbar"
            :style="{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexWrap: 'wrap',
              gap: '8px',
              padding: '12px',
              backgroundColor: $themePalette.grey.v_100,
              borderRadius: '8px',
            }"
          >
            <span :style="{ color: $themeTokens.annotation, fontWeight: 'bold' }">
              {{ addBlockAction$() }}:
            </span>
            <KButton
              :text="blockTypeHeading$()"
              icon="plus"
              appearance="flat-button"
              @click="addNewBlock('heading')"
            />
            <KButton
              :text="blockTypeText$()"
              icon="plus"
              appearance="flat-button"
              @click="addNewBlock('text')"
            />
            <KButton
              :text="blockTypeImage$()"
              icon="plus"
              appearance="flat-button"
              @click="addNewBlock('image')"
            />
            <KButton
              :text="blockTypeVideo$()"
              icon="plus"
              appearance="flat-button"
              @click="addNewBlock('video')"
            />
            <KButton
              :text="blockTypeCallout$()"
              icon="plus"
              appearance="flat-button"
              @click="addNewBlock('callout')"
            />
            <KButton
              :text="blockTypeCheckpoint$()"
              icon="plus"
              appearance="flat-button"
              @click="addNewBlock('checkpoint')"
            />
          </div>
        </div>

        <!-- Hidden file input for builder image uploads -->
        <input
          ref="builderImageInput"
          type="file"
          class="hidden-file-input"
          accept=".png,.jpg,.jpeg,.gif,.webp,.svg"
          style="display: none;"
          @change="onBuilderImageSelected"
        >
      </div>

      <!-- TAB: H5P INTERACTIVE ACTIVITIES -->
      <div
        v-if="activeTab === 'h5p'"
        class="tab-content"
      >
        <div
          class="h5p-mode-bar mb-16"
          :style="{
            display: 'flex',
            gap: '8px',
            borderBottom: `1px solid ${$themeTokens.fineLine}`,
            paddingBottom: '12px',
          }"
        >
          <KButton
            :text="h5pStudioModeLabel$()"
            icon="html5"
            :appearance="h5pMode === 'hub' ? 'raised-button' : 'flat-button'"
            :primary="h5pMode === 'hub'"
            @click="h5pMode = 'hub'"
          />
          <KButton
            :text="h5pQuickModeLabel$()"
            icon="plus"
            :appearance="h5pMode === 'create' ? 'raised-button' : 'flat-button'"
            :primary="h5pMode === 'create'"
            @click="h5pMode = 'create'"
          />
          <KButton
            :text="uploadH5PModeLabel$()"
            icon="document"
            :appearance="h5pMode === 'upload' ? 'raised-button' : 'flat-button'"
            :primary="h5pMode === 'upload'"
            @click="h5pMode = 'upload'"
          />
        </div>

        <!-- Mode A: Official H5P Authoring Studio (All 50+ Types) -->
        <div
          v-if="h5pMode === 'hub'"
          class="h5p-hub-studio-wrapper"
        >
          <div
            class="h5p-hub-header-banner"
            :style="{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              backgroundColor: $themePalette.grey.v_100,
              border: `1px solid ${$themeTokens.fineLine}`,
              borderRadius: '6px',
              padding: '10px 16px',
              marginBottom: '12px',
            }"
          >
            <div>
              <h4 :style="{ margin: '0 0 2px', color: $themeTokens.text }">
                {{ h5pStudioHeaderTitle$() }}
              </h4>
              <p :style="{ margin: 0, color: $themeTokens.annotation, fontSize: '0.85rem' }">
                {{ h5pStudioHeaderSubtitle$() }}
              </p>
            </div>
            <KButton
              :text="refreshStudioLabel$()"
              icon="refresh"
              appearance="flat-button"
              @click="reloadH5PEditor"
            />
          </div>

          <div
            v-if="isSavingH5P"
            class="h5p-saving-banner"
            :style="{
              textAlign: 'center',
              padding: '20px',
              backgroundColor: $themeTokens.surface,
              borderRadius: '8px',
              border: `1px solid ${$themeTokens.fineLine}`,
              marginBottom: '12px',
            }"
          >
            <KCircularLoader :delay="false" />
            <p :style="{ marginTop: '8px', fontWeight: 'bold', color: $themeTokens.text }">
              {{ savingToLessonNotice$() }}
            </p>
          </div>

          <div
            v-if="isIframeLoading"
            class="h5p-loading-banner"
            :style="{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '420px',
              backgroundColor: $themeTokens.surface,
              borderRadius: '8px',
              border: `1px solid ${$themeTokens.fineLine}`,
              marginBottom: '12px',
            }"
          >
            <KCircularLoader :delay="false" />
            <p :style="{ marginTop: '16px', fontWeight: '500', color: $themeTokens.annotation }">
              {{ h5pLoadingNotice$() }}
            </p>
          </div>

          <iframe
            v-show="!isIframeLoading"
            ref="h5pEditorIframe"
            :src="h5pEditorUrl"
            class="h5p-hub-iframe"
            style="width: 100%; height: 720px; border: 1px solid #e2e8f0; border-radius: 8px; background: #ffffff;"
            allow="fullscreen; geolocation; microphone; camera; midi"
            @load="onIframeLoaded"
          ></iframe>
        </div>

        <!-- Mode B: In-System Quick Activity Templates -->
        <div v-else-if="h5pMode === 'create'">
          <H5PActivityBuilder ref="activityBuilderRef" />
        </div>

        <!-- Mode C: Upload .h5p File -->
        <div v-else>
          <p :style="{ color: $themeTokens.annotation }">
            {{ h5pUploadDesc$() }}
          </p>

          <button
            type="button"
            class="drop-zone"
            :style="{
              borderColor: selectedH5PFile ? $themeTokens.primary : $themeTokens.fineLine,
              backgroundColor: selectedH5PFile ? $themePalette.grey.v_100 : $themeTokens.surface,
            }"
            @click="triggerFileInput('h5pInput')"
          >
            <input
              ref="h5pInput"
              type="file"
              class="hidden-file-input"
              :aria-label="selectH5PPrompt$()"
              accept=".h5p,.zip"
              @change="onFileSelected($event, 'h5p')"
            >
            <KIcon
              icon="html5"
              class="upload-icon"
            />
            <p
              v-if="!selectedH5PFile"
              class="drop-text"
            >
              {{ selectH5PPrompt$() }}
            </p>
            <div
              v-else
              class="file-info-badge"
            >
              <span class="file-name">{{ selectedH5PFile.name }}</span>
              <span
                class="file-size"
                :style="{ color: $themeTokens.annotation }"
              >
                ({{ formatFileSize(selectedH5PFile.size) }})
              </span>
            </div>
          </button>

          <div
            v-if="selectedH5PFile"
            class="mt-16"
          >
            <KTextbox
              v-model="h5pTitle"
              :label="titleLabel$()"
              class="mb-16"
            />
            <KTextbox
              v-model="h5pDescription"
              :label="descriptionLabel$()"
              :textArea="true"
              class="mb-16"
            />
          </div>
        </div>
      </div>

      <!-- TAB 1: UPLOAD FILE (PDF, Images, Docs) -->
      <div
        v-if="activeTab === 'file'"
        class="tab-content"
      >
        <p :style="{ color: $themeTokens.annotation }">
          {{ uploadFileDesc$() }}
        </p>

        <button
          type="button"
          class="drop-zone"
          :style="{
            borderColor: selectedFile ? $themeTokens.primary : $themeTokens.fineLine,
            backgroundColor: selectedFile ? $themePalette.grey.v_100 : $themeTokens.surface,
          }"
          @click="triggerFileInput('fileInput')"
        >
          <input
            ref="fileInput"
            type="file"
            class="hidden-file-input"
            :aria-label="uploadResourceFileLabel$()"
            accept=".pdf,.png,.jpg,.jpeg,.gif,.webp,.svg,.docx,.doc,.txt,.pptx,.xlsx,.odt,.csv,.md"
            @change="onFileSelected($event, 'file')"
          >
          <KIcon
            icon="document"
            class="upload-icon"
          />
          <p
            v-if="!selectedFile"
            class="drop-text"
          >
            {{ selectFilePrompt$() }}
          </p>
          <div
            v-else
            class="file-info-badge"
          >
            <span class="file-name">{{ selectedFile.name }}</span>
            <span
              class="file-size"
              :style="{ color: $themeTokens.annotation }"
            >
              ({{ formatFileSize(selectedFile.size) }})
            </span>
          </div>
        </button>

        <div
          v-if="uploadWarningError && activeTab === 'file'"
          class="file-error-alert mt-8"
          :style="{
            color: $themePalette.red.v_700,
            backgroundColor: $themePalette.red.v_50,
            border: `1.5px solid ${$themePalette.red.v_300}`,
            padding: '10px 14px',
            borderRadius: '6px',
            fontWeight: '600',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }"
        >
          <span style="font-size: 18px;">⚠️</span>
          <span>{{ uploadWarningError }}</span>
        </div>

        <KTextbox
          v-model="fileTitle"
          :label="titleLabel$()"
          :invalid="Boolean(fileTitleError)"
          :invalidText="fileTitleError"
          class="mt-16"
        />

        <KTextbox
          v-model="fileDescription"
          :label="descriptionLabel$()"
          :textArea="true"
          class="mt-16"
        />
      </div>

      <!-- TAB 2: YOUTUBE VIDEO -->
      <div
        v-if="activeTab === 'youtube'"
        class="tab-content"
      >
        <p :style="{ color: $themeTokens.annotation }">
          {{ youtubeDesc$() }}
        </p>

        <KTextbox
          v-model="youtubeUrl"
          :label="youtubeUrlLabel$()"
          placeholder="https://www.youtube.com/watch?v=..."
          :invalid="Boolean(youtubeUrlError)"
          :invalidText="youtubeUrlError"
        />

        <KTextbox
          v-model="youtubeTitle"
          :label="titleLabel$()"
          :invalid="Boolean(youtubeTitleError)"
          :invalidText="youtubeTitleError"
          class="mt-16"
        />

        <KTextbox
          v-model="youtubeDescription"
          :label="descriptionLabel$()"
          :textArea="true"
          class="mt-16"
        />

        <!-- Live In-Kolibri YouTube Preview -->
        <div
          v-if="isValidYoutubeUrl"
          class="mt-16 video-preview"
        >
          <h4 :style="{ color: $themeTokens.text, marginBottom: '8px' }">
            {{ videoPreviewLabel$() }}
          </h4>
          <YouTubePlayer
            :url="youtubeUrl"
            :title="youtubeTitle || 'Video Preview'"
          />
        </div>
      </div>

      <!-- TAB 3: HTML5 PACKAGE -->
      <div
        v-if="activeTab === 'html5'"
        class="tab-content"
      >
        <p :style="{ color: $themeTokens.annotation }">
          {{ html5Desc$() }}
        </p>

        <button
          type="button"
          class="drop-zone"
          :style="{
            borderColor: selectedHtml5File ? $themeTokens.primary : $themeTokens.fineLine,
            backgroundColor: selectedHtml5File ? $themePalette.grey.v_100 : $themeTokens.surface,
          }"
          @click="triggerFileInput('html5Input')"
        >
          <input
            ref="html5Input"
            type="file"
            class="hidden-file-input"
            :aria-label="uploadHtml5ZipLabel$()"
            accept=".zip,.html,.htm"
            @change="onFileSelected($event, 'html5')"
          >
          <KIcon
            icon="html5"
            class="upload-icon"
          />
          <p
            v-if="!selectedHtml5File"
            class="drop-text"
          >
            {{ selectHtml5Prompt$() }}
          </p>
          <div
            v-else
            class="file-info-badge"
          >
            <span class="file-name">{{ selectedHtml5File.name }}</span>
            <span
              class="file-size"
              :style="{ color: $themeTokens.annotation }"
            >
              ({{ formatFileSize(selectedHtml5File.size) }})
            </span>
          </div>
        </button>

        <div
          v-if="uploadWarningError && activeTab === 'html5'"
          class="file-error-alert mt-8"
          :style="{
            color: $themePalette.red.v_700,
            backgroundColor: $themePalette.red.v_50,
            border: `1.5px solid ${$themePalette.red.v_300}`,
            padding: '10px 14px',
            borderRadius: '6px',
            fontWeight: '600',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }"
        >
          <span style="font-size: 18px;">⚠️</span>
          <span>{{ uploadWarningError }}</span>
        </div>

        <KTextbox
          v-model="html5Title"
          :label="titleLabel$()"
          :invalid="Boolean(html5TitleError)"
          :invalidText="html5TitleError"
          class="mt-16"
        />

        <KTextbox
          v-model="html5Description"
          :label="descriptionLabel$()"
          :textArea="true"
          class="mt-16"
        />
      </div>

      <!-- TAB 4: AI GENERATOR -->
      <div
        v-if="activeTab === 'ai'"
        class="tab-content"
      >
        <p :style="{ color: $themeTokens.annotation }">
          {{ aiDesc$() }}
        </p>

        <KTextbox
          v-model="aiTopic"
          :label="aiTopicLabel$()"
          :placeholder="aiTopicPlaceholder$()"
          :invalid="Boolean(aiTopicError)"
          :invalidText="aiTopicError"
          :disabled="isGeneratingAi"
        />

        <div class="mt-16 row-2">
          <KSelect
            v-model="aiGrade"
            :label="gradeLevelLabel$()"
            :options="gradeOptions"
            :disabled="isGeneratingAi"
          />
          <KSelect
            v-model="aiFormat"
            :label="materialTypeLabel$()"
            :options="formatOptions"
            :disabled="isGeneratingAi"
          />
        </div>

        <div class="d-flex mt-16">
          <KButton
            :text="isGeneratingAi ? aiGenerating$() : aiGenerateButton$()"
            :primary="true"
            appearance="raised-button"
            icon="hint"
            :disabled="!aiTopic.trim() || isGeneratingAi"
            @click="handleGenerateAiContent"
          />
        </div>

        <div
          v-if="isGeneratingAi"
          class="ai-loading mt-16"
        >
          <KCircularLoader :delay="false" />
          <span class="loading-msg">{{ aiGeneratingText$() }}</span>
        </div>

        <div
          v-if="aiContent && !isGeneratingAi"
          class="mt-16"
        >
          <KTextbox
            v-model="aiTitle"
            :label="titleLabel$()"
            class="mb-16"
          />
          <h4 :style="{ color: $themeTokens.text, marginBottom: '8px' }">
            {{ generatedContentLabel$() }}
          </h4>
          <KTextbox
            v-model="aiContent"
            :textArea="true"
            :label="aiContentLabel$()"
            rows="10"
          />
        </div>
      </div>

      <!-- TAB 5: CONTENT CARD -->
      <div
        v-if="activeTab === 'card'"
        class="tab-content"
      >
        <p :style="{ color: $themeTokens.annotation }">
          {{ cardDesc$() }}
        </p>

        <KTextbox
          v-model="cardTitle"
          :label="titleLabel$()"
          :invalid="Boolean(cardTitleError)"
          :invalidText="cardTitleError"
          class="mb-16"
        />

        <KTextbox
          v-model="cardDescription"
          :label="descriptionLabel$()"
          :textArea="true"
          class="mb-16"
        />

        <!-- Optional Banner Image -->
        <div class="mb-16">
          <label :style="{ color: $themeTokens.annotation, display: 'block', marginBottom: '8px' }">
            {{ cardImagePrompt$() }}
          </label>
          <button
            type="button"
            class="drop-zone"
            :style="{
              borderColor: selectedCardImage ? $themeTokens.primary : $themeTokens.fineLine,
              backgroundColor: selectedCardImage ? $themePalette.grey.v_100 : $themeTokens.surface,
              padding: '16px',
            }"
            @click="triggerFileInput('cardInput')"
          >
            <input
              ref="cardInput"
              type="file"
              class="hidden-file-input"
              :aria-label="uploadCardImageLabel$()"
              accept=".png,.jpg,.jpeg,.gif,.webp,.svg"
              @change="onFileSelected($event, 'card')"
            >
            <div v-if="!selectedCardImage">
              <KIcon
                icon="image"
                class="upload-icon"
              />
              <p class="drop-text">{{ selectFilePrompt$() }}</p>
            </div>
            <div
              v-else
              class="card-img-preview-container"
            >
              <img
                :src="cardImagePreview"
                alt="Card image preview"
                class="card-preview-thumb"
              >
              <div class="file-info-badge">
                <span class="file-name">{{ selectedCardImage.name }}</span>
                <span
                  class="file-size"
                  :style="{ color: $themeTokens.annotation }"
                >
                  ({{ formatFileSize(selectedCardImage.size) }})
                </span>
              </div>
              <KIconButton
                icon="clear"
                size="small"
                :tooltip="removeImage$()"
                :ariaLabel="removeImage$()"
                @click.stop="clearCardImage"
              />
            </div>
          </button>

          <div
            v-if="uploadWarningError && activeTab === 'card'"
            class="file-error-alert mt-8"
            :style="{
              color: $themePalette.red.v_700,
              backgroundColor: $themePalette.red.v_50,
              border: `1.5px solid ${$themePalette.red.v_300}`,
              padding: '10px 14px',
              borderRadius: '6px',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }"
          >
            <span style="font-size: 18px;">⚠️</span>
            <span>{{ uploadWarningError }}</span>
          </div>
        </div>

        <KTextbox
          v-model="cardContent"
          :textArea="true"
          :label="cardContentLabel$()"
          :placeholder="cardContentPlaceholder$()"
          rows="8"
        />
      </div>

      <!-- TAB: PERSEUS MULTI-SUBJECT STUDIO -->
      <div
        v-if="activeTab === 'perseus'"
        class="tab-content perseus-tab-content"
      >
        <PerseusActivityStudio
          @change="onPerseusStudioChange"
        />
      </div>

      <!-- Submitting Indicator -->
      <div
        v-if="isSubmitting"
        class="submitting-overlay"
      >
        <KCircularLoader :delay="false" />
        <p>{{ savingResource$() }}</p>
      </div>
    </div>
  </KModal>

</template>


<script>

  import { ref, computed, onMounted, onUnmounted } from 'vue';
  import client from 'kolibri/client';
  import { createTranslator } from 'kolibri/utils/i18n';
  import useSnackbar from 'kolibri/composables/useSnackbar';
  import useAiTutor from 'kolibri-common/composables/useAiTutor';
  import YouTubePlayer from 'kolibri-common/components/YouTubePlayer';
  import H5PActivityBuilder from './H5PActivityBuilder';
  import PerseusActivityStudio from '../../common/PerseusActivityStudio.vue';

  const modalStrings = createTranslator('AddCustomResourceModalStrings', {
    modalTitle: {
      message: 'Add Custom Resource to Lesson',
      context: 'Modal header title',
    },
    addResourceButton: {
      message: 'Add to Lesson',
      context: 'Submit button',
    },
    cancelButton: {
      message: 'Cancel',
      context: 'Cancel button',
    },
    tabH5PInteractiveLabel: {
      message: 'H5P Interactive',
      context: 'Tab label for interactive H5P activities',
    },
    tabPerseusLabel: {
      message: 'Perseus Studio',
      context: 'Tab button label for Perseus interactive studio',
    },
    h5pStudioModeLabel: {
      message: 'H5P Interactive Studio',
      context: 'Button label for full H5P Hub studio mode',
    },
    h5pQuickModeLabel: {
      message: 'Quick Templates',
      context: 'Button label for quick built-in templates',
    },
    h5pStudioHeaderTitle: {
      message: 'H5P Interactive Authoring Studio',
      context: 'Header title for H5P Hub',
    },
    h5pStudioHeaderSubtitle: {
      message: 'Visually author, configure, and assign any official interactive activity type.',
      context: 'Header subtitle for H5P Hub',
    },
    refreshStudioLabel: {
      message: 'Reset Studio',
      context: 'Button label to reload the studio iframe',
    },
    h5pLoadingNotice: {
      message: 'Loading H5P Interactive Studio...',
      context: 'Notice while loading H5P studio',
    },
    validationPrompt: {
      message: 'Please select an interactive activity type and fill in the required fields before saving.',
      context: 'Snackbar warning when user attempts to save without selecting an activity',
    },
    savingToLessonNotice: {
      message: 'Saving interactive activity and adding to lesson...',
      context: 'Notice while saving H5P to lesson',
    },
    h5pSavedSuccess: {
      message: 'H5P Interactive activity successfully added to lesson!',
      context: 'Success notification after H5P save',
    },
    createInteractiveModeLabel: {
      message: 'Create Interactive Activity',
      context: 'Button label to create activity',
    },
    uploadH5PModeLabel: {
      message: 'Upload .h5p File',
      context: 'Button label to upload activity file',
    },
    h5pUploadDesc: {
      message: 'Upload an interactive .h5p activity file to assign to your learners.',
      context: 'Upload description',
    },
    selectH5PPrompt: {
      message: 'Click or drop a .h5p file here',
      context: 'File drop area text',
    },
    tabFilesLabel: {
      message: 'Upload File',
      context: 'Tab label for files',
    },
    tabYoutubeLabel: {
      message: 'YouTube Video',
      context: 'Tab label for YouTube videos',
    },
    tabHtml5Label: {
      message: 'HTML5 Package',
      context: 'Tab label for HTML5 packages',
    },
    tabAiLabel: {
      message: 'Generate with AI',
      context: 'Tab label for AI generated notes',
    },
    uploadFileDesc: {
      message: 'Upload documents, PDFs, pictures, or notes for your learners to view.',
      context: 'Tab description',
    },
    selectFilePrompt: {
      message: 'Click or drop a file here (.pdf, .png, .jpg, .docx, .txt, etc.)',
      context: 'File drop area text',
    },
    youtubeDesc: {
      message: 'Paste a YouTube video link. It will play safely inside PHIEDU for your learners.',
      context: 'YouTube tab description',
    },
    youtubeUrlLabel: {
      message: 'YouTube Video URL',
      context: 'URL textbox label',
    },
    videoPreviewLabel: {
      message: 'Video Preview',
      context: 'Preview title',
    },
    html5Desc: {
      message: 'Upload an interactive HTML5 simulation or activity (.zip or .html).',
      context: 'HTML5 tab description',
    },
    selectHtml5Prompt: {
      message: 'Click or drop a .zip or .html file here',
      context: 'HTML5 drop area text',
    },
    aiDesc: {
      message: 'Create structured study guides, summaries, or practice notes instantly with AI.',
      context: 'AI tab description',
    },
    aiTopicLabel: {
      message: 'Topic or Concept',
      context: 'Input label',
    },
    aiTopicPlaceholder: {
      message: 'e.g. Introduction to Photosynthesis, Civil War Timeline, Solving Linear Equations',
      context: 'Input placeholder',
    },
    gradeLevelLabel: {
      message: 'Target Level',
      context: 'Grade dropdown label',
    },
    materialTypeLabel: {
      message: 'Resource Style',
      context: 'Format dropdown label',
    },
    aiGenerateButton: {
      message: 'Generate Material with AI',
      context: 'Generate button',
    },
    aiGenerating: {
      message: 'Generating...',
      context: 'Button generating text',
    },
    aiGeneratingText: {
      message: 'Crafting comprehensive study notes with AI...',
      context: 'Loading text',
    },
    generatedContentLabel: {
      message: 'Generated Resource (Markdown)',
      context: 'Textarea header',
    },
    aiContentLabel: {
      message: 'Edit Content',
      context: 'Textarea label',
    },
    titleLabel: {
      message: 'Resource Title',
      context: 'Title textbox label',
    },
    descriptionLabel: {
      message: 'Description or Coach Instructions (Optional)',
      context: 'Description label',
    },
    savingResource: {
      message: 'Saving resource to lesson...',
      context: 'Saving status',
    },
    successNotice: {
      message: 'Resource successfully added to lesson!',
      context: 'Snackbar success message',
    },
    errorNotice: {
      message: 'Could not add resource. Please check the inputs and try again.',
      context: 'Snackbar error message',
    },
    uploadResourceFileLabel: {
      message: 'Upload resource file',
      context: 'Accessibility label for file input',
    },
    uploadHtml5ZipLabel: {
      message: 'Upload HTML5 zip package',
      context: 'Accessibility label for HTML5 file input',
    },
    tabCardLabel: {
      message: 'Content Card',
      context: 'Tab label for standalone content card',
    },
    cardDesc: {
      message:
        'Create a standalone learning card with formatted notes, key concepts, and an optional image.',
      context: 'Content card tab description',
    },
    cardImagePrompt: {
      message: 'Card Banner / Illustration (Optional)',
      context: 'Card image field label',
    },
    cardContentLabel: {
      message: 'Card Body Content (Markdown supported)',
      context: 'Content textbox label',
    },
    cardContentPlaceholder: {
      message:
        'Write explanations, key definitions, formulas, or instructions for your students...',
      context: 'Content textbox placeholder',
    },
    uploadCardImageLabel: {
      message: 'Upload card image',
      context: 'Accessibility label for image file input',
    },
    removeImage: {
      message: 'Remove image',
      context: 'Tooltip for removing card image',
    },
    fileSizeExceededWarning: {
      message: 'File size ({size}) exceeds the 5MB maximum limit. Please choose a file smaller than 5MB.',
      context: 'Warning displayed when uploaded file exceeds 5MB',
    },
    packageFileSizeExceededWarning: {
      message: 'Package size ({size}) exceeds the 20MB maximum limit. Please choose a file smaller than 20MB.',
      context: 'Warning displayed when uploaded zip or h5p package exceeds 20MB',
    },
    tabLessonBuilderLabel: {
      message: 'Lesson Builder',
      context: 'Tab label for custom lesson builder',
    },
    builderHeaderTitle: {
      message: 'Author Custom Lesson',
      context: 'Title for lesson builder header',
    },
    builderHeaderSubtitle: {
      message:
        'Design a structured, multi-section lesson with headings, explanations, diagrams, media, key concepts, and checkpoints.',
      context: 'Subtitle for lesson builder header',
    },
    addBlockAction: {
      message: 'Add Block',
      context: 'Button label to add a new content block',
    },
    emptyBlocksNotice: {
      message: 'No lesson content blocks added yet',
      context: 'Empty state heading',
    },
    emptyBlocksPrompt: {
      message: 'Click any block type below to begin crafting your structured lesson content.',
      context: 'Empty state prompt',
    },
    blockTypeHeading: {
      message: 'Section Heading',
      context: 'Block type label',
    },
    blockTypeText: {
      message: 'Text & Notes',
      context: 'Block type label',
    },
    blockTypeImage: {
      message: 'Diagram / Image',
      context: 'Block type label',
    },
    blockTypeVideo: {
      message: 'Video Embed',
      context: 'Block type label',
    },
    blockTypeCallout: {
      message: 'Key Concept / Callout',
      context: 'Block type label',
    },
    blockTypeCheckpoint: {
      message: 'Practice Checkpoint',
      context: 'Block type label',
    },
    sectionHeadingLabel: {
      message: 'Section Title',
      context: 'Input label for section heading',
    },
    sectionHeadingPlaceholder: {
      message: 'e.g. 1. Introduction to Cells',
      context: 'Placeholder for section heading',
    },
    sectionSubtitleLabel: {
      message: 'Subtitle or Section Goal (Optional)',
      context: 'Input label for section subtitle',
    },
    sectionSubtitlePlaceholder: {
      message: 'e.g. Understanding eukaryotic vs prokaryotic structures',
      context: 'Placeholder for section subtitle',
    },
    textContentLabel: {
      message: 'Lesson Content (Markdown supported)',
      context: 'Input label for text block',
    },
    textContentPlaceholder: {
      message: 'Write explanations, definitions, key points, or instructions...',
      context: 'Placeholder for text block',
    },
    uploadImagePrompt: {
      message: 'Click or drop an image here (PNG, JPG, SVG up to 5MB)',
      context: 'Dropzone prompt for diagram upload',
    },
    imageCaptionLabel: {
      message: 'Image Caption / Description (Optional)',
      context: 'Input label for image caption',
    },
    imageCaptionPlaceholder: {
      message: 'e.g. Figure 1. Diagram of chloroplast structures',
      context: 'Placeholder for image caption',
    },
    videoUrlLabel: {
      message: 'Video URL (YouTube or MP4)',
      context: 'Input label for video URL',
    },
    videoNotesLabel: {
      message: 'Video Description or Viewing Guidance (Optional)',
      context: 'Input label for video notes',
    },
    calloutTypeLabel: {
      message: 'Callout Style',
      context: 'Label for callout tone selector',
    },
    calloutTitleLabel: {
      message: 'Callout Heading',
      context: 'Input label for callout title',
    },
    calloutTitlePlaceholder: {
      message: 'e.g. Key Concept, Did You Know?, Important Rule',
      context: 'Placeholder for callout title',
    },
    calloutContentLabel: {
      message: 'Callout Content',
      context: 'Input label for callout text',
    },
    calloutContentPlaceholder: {
      message: 'Important rule or definition for students to remember...',
      context: 'Placeholder for callout text',
    },
    checkpointQuestionLabel: {
      message: 'Reflection Question / Quick Check',
      context: 'Input label for checkpoint question',
    },
    checkpointQuestionPlaceholder: {
      message: 'e.g. How does photosynthesis differ from cellular respiration?',
      context: 'Placeholder for checkpoint question',
    },
    checkpointAnswerLabel: {
      message: 'Model Answer / Teacher Explanation (Optional)',
      context: 'Input label for checkpoint answer',
    },
    checkpointAnswerPlaceholder: {
      message: 'This explanation can be revealed by students to verify their understanding...',
      context: 'Placeholder for checkpoint answer',
    },
    duplicateBlockAction: {
      message: 'Duplicate block',
      context: 'Button tooltip',
    },
    deleteBlockAction: {
      message: 'Delete block',
      context: 'Button tooltip',
    },
    moveUpAction: {
      message: 'Move up',
      context: 'Button tooltip',
    },
    moveDownAction: {
      message: 'Move down',
      context: 'Button tooltip',
    },
  });

  export default {
    name: 'AddCustomResourceModal',
    components: {
      YouTubePlayer,
      H5PActivityBuilder,
      PerseusActivityStudio,
    },
    setup(props, { emit }) {
      const { createSnackbar } = useSnackbar();
      const { generateLesson } = useAiTutor();

      const activeTab = ref(props.initialTab || 'builder');
      const isSubmitting = ref(false);
      const uploadWarningError = ref('');

      // Perseus Studio State
      const perseusActivityData = ref(null);

      function onPerseusStudioChange(data) {
        perseusActivityData.value = data;
      }

      // Lesson Builder State
      const builderTitle = ref('');
      const builderDescription = ref('');
      const builderTitleError = ref('');
      const activeBlockIndex = ref(0);
      const builderImageInput = ref(null);
      const builderTargetBlock = ref(null);
      const builderBlocks = ref([
        {
          id: 'b-1',
          type: 'heading',
          title: '',
          subtitle: '',
        },
        {
          id: 'b-2',
          type: 'text',
          text: '',
        },
      ]);

      function createBlock(type = 'text') {
        const id = `b-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`;
        if (type === 'heading') {
          return { id, type: 'heading', title: '', subtitle: '' };
        }
        if (type === 'image') {
          return { id, type: 'image', image_url: '', caption: '' };
        }
        if (type === 'video') {
          return { id, type: 'video', url: '', notes: '' };
        }
        if (type === 'callout') {
          return { id, type: 'callout', callout_type: 'concept', title: '', text: '' };
        }
        if (type === 'checkpoint') {
          return { id, type: 'checkpoint', question: '', answer: '' };
        }
        return { id, type: 'text', text: '' };
      }

      function addNewBlock(type = 'text') {
        const newBlock = createBlock(type);
        builderBlocks.value.push(newBlock);
        activeBlockIndex.value = builderBlocks.value.length - 1;
      }

      function moveBlockUp(index) {
        if (index > 0) {
          const item = builderBlocks.value.splice(index, 1)[0];
          builderBlocks.value.splice(index - 1, 0, item);
          activeBlockIndex.value = index - 1;
        }
      }

      function moveBlockDown(index) {
        if (index < builderBlocks.value.length - 1) {
          const item = builderBlocks.value.splice(index, 1)[0];
          builderBlocks.value.splice(index + 1, 0, item);
          activeBlockIndex.value = index + 1;
        }
      }

      function duplicateBlock(index) {
        const original = builderBlocks.value[index];
        if (!original) return;
        const copy = JSON.parse(JSON.stringify(original));
        copy.id = `b-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`;
        builderBlocks.value.splice(index + 1, 0, copy);
        activeBlockIndex.value = index + 1;
      }

      function removeBlock(index) {
        builderBlocks.value.splice(index, 1);
        if (activeBlockIndex.value >= builderBlocks.value.length) {
          activeBlockIndex.value = Math.max(0, builderBlocks.value.length - 1);
        }
      }

      function triggerBlockImageUpload(block) {
        builderTargetBlock.value = block;
        if (builderImageInput.value) {
          builderImageInput.value.value = '';
          builderImageInput.value.click();
        }
      }

      async function onBuilderImageSelected(event) {
        const file = event.target.files && event.target.files[0];
        if (!file || !builderTargetBlock.value) return;

        if (file.size > 5 * 1024 * 1024) {
          const warning = modalStrings.fileSizeExceededWarning$({
            size: formatFileSize(file.size),
          });
          createSnackbar(warning);
          return;
        }

        const formData = new FormData();
        formData.append('file', file);
        try {
          const response = await client({
            url: '/api/lessons/lesson/upload_image/',
            method: 'POST',
            data: formData,
            headers: { 'Content-Type': 'multipart/form-data' },
          });
          if (response.data && response.data.url) {
            builderTargetBlock.value.image_url = response.data.url;
            createSnackbar('Image uploaded successfully!');
          }
        } catch (err) {
          const detailMsg = err.response && err.response.data && err.response.data.detail;
          createSnackbar(detailMsg || 'Failed to upload image. Please try again.');
        }
      }

      // File Tab State
      const selectedFile = ref(null);
      const fileTitle = ref('');
      const fileDescription = ref('');
      const fileTitleError = ref('');
      const fileInput = ref(null);

      // YouTube Tab State
      const youtubeUrl = ref('');
      const youtubeTitle = ref('');
      const youtubeDescription = ref('');
      const youtubeUrlError = ref('');
      const youtubeTitleError = ref('');

      // HTML5 Tab State
      const selectedHtml5File = ref(null);
      const html5Title = ref('');
      const html5Description = ref('');
      const html5TitleError = ref('');
      const html5Input = ref(null);

      // H5P Tab State
      const h5pMode = ref('hub');
      const activityBuilderRef = ref(null);
      const selectedH5PFile = ref(null);
      const h5pTitle = ref('');
      const h5pDescription = ref('');
      const h5pInput = ref(null);
      const h5pEditorIframe = ref(null);
      const isSavingH5P = ref(false);
      const isIframeLoading = ref(true);
      const h5pEditorUrl = ref('/h5p/new');

      function reloadH5PEditor() {
        isIframeLoading.value = true;
        h5pEditorUrl.value = `/h5p/new?t=${Date.now()}`;
      }

      function onIframeLoaded() {
        setTimeout(() => {
          isIframeLoading.value = false;
        }, 3000);
      }

      async function handleH5PContentSaved(contentId, title) {
        isSavingH5P.value = true;
        try {
          const endpointUrl = `/api/lessons/lesson/${props.lessonId}/custom_resource/`;
          const response = await client({
            url: endpointUrl,
            method: 'POST',
            data: {
              resource_type: 'h5p',
              h5p_content_id: String(contentId),
              title: title ? title.trim() : 'H5P Interactive Activity',
            },
          });
          createSnackbar(modalStrings.h5pSavedSuccess$());
          emit('added', response.data);
          emit('close');
        } catch (err) {
          const detailMsg = err.response && err.response.data && err.response.data.detail;
          createSnackbar(detailMsg || modalStrings.errorNotice$());
        } finally {
          isSavingH5P.value = false;
        }
      }

      function onWindowMessage(event) {
        if (event.data) {
          if (event.data.type === 'KOLIBRI_H5P_READY') {
            isIframeLoading.value = false;
          } else if (event.data.type === 'KOLIBRI_H5P_SAVED') {
            handleH5PContentSaved(event.data.contentId, event.data.title);
          } else if (event.data.type === 'KOLIBRI_H5P_VALIDATION_ERROR') {
            isSubmitting.value = false;
            isSavingH5P.value = false;
            createSnackbar(event.data.message || modalStrings.validationPrompt$());
          }
        }
      }

      onMounted(() => {
        window.addEventListener('message', onWindowMessage);
      });

      onUnmounted(() => {
        window.removeEventListener('message', onWindowMessage);
      });

      // AI Tab State
      const aiTopic = ref('');
      const aiGrade = ref('elementary');
      const aiFormat = ref('notes');
      const aiContent = ref('');
      const aiTitle = ref('');
      const aiTopicError = ref('');
      const isGeneratingAi = ref(false);

      // Card Tab State
      const selectedCardImage = ref(null);
      const cardImagePreview = ref('');
      const cardTitle = ref('');
      const cardDescription = ref('');
      const cardContent = ref('');
      const cardTitleError = ref('');
      const cardInput = ref(null);

      const gradeOptions = [
        { label: 'Elementary School', value: 'elementary' },
        { label: 'Middle School', value: 'middle' },
        { label: 'High School', value: 'high' },
        { label: 'Higher Education / Adult', value: 'college' },
      ];

      const formatOptions = [
        { label: 'Comprehensive Study Notes & Key Definitions', value: 'notes' },
        { label: 'Brief Summary & Key Takeaways', value: 'summary' },
        { label: 'Practice Questions & Discussion Prompts', value: 'practice' },
      ];

      const isValidYoutubeUrl = computed(() => {
        const u = youtubeUrl.value.trim();
        return u.includes('youtube.com') || u.includes('youtu.be');
      });

      const isSubmitDisabled = computed(() => {
        if (activeTab.value === 'builder') {
          return !builderTitle.value.trim() || builderBlocks.value.length === 0;
        }
        if (activeTab.value === 'h5p') {
          if (h5pMode.value === 'hub') {
            return false;
          }
          if (h5pMode.value === 'create') {
            return !activityBuilderRef.value || !activityBuilderRef.value.isValid;
          }
          return !selectedH5PFile.value || !h5pTitle.value.trim();
        }
        if (activeTab.value === 'file') {
          return !selectedFile.value || !fileTitle.value.trim();
        }
        if (activeTab.value === 'youtube') {
          return !isValidYoutubeUrl.value || !youtubeTitle.value.trim();
        }
        if (activeTab.value === 'html5') {
          return !selectedHtml5File.value || !html5Title.value.trim();
        }
        if (activeTab.value === 'ai') {
          return !aiContent.value.trim() || !aiTitle.value.trim();
        }
        if (activeTab.value === 'perseus') {
          return !perseusActivityData.value || !perseusActivityData.value.item;
        }
        if (activeTab.value === 'card') {
          return !cardTitle.value.trim() || (!cardContent.value.trim() && !selectedCardImage.value);
        }
        return true;
      });

      function formatFileSize(bytes) {
        if (!bytes) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
      }

      function triggerFileInput(refName) {
        if (refName === 'fileInput' && fileInput.value) {
          fileInput.value.click();
        } else if (refName === 'html5Input' && html5Input.value) {
          html5Input.value.click();
        } else if (refName === 'h5pInput' && h5pInput.value) {
          h5pInput.value.click();
        } else if (refName === 'cardInput' && cardInput.value) {
          cardInput.value.click();
        }
      }

      function onFileSelected(event, type) {
        const file = event.target.files && event.target.files[0];
        if (!file) return;

        const isPackage = type === 'html5' || type === 'h5p';
        const maxSize = isPackage ? 20 * 1024 * 1024 : 5 * 1024 * 1024;

        if (file.size > maxSize) {
          uploadWarningError.value = isPackage
            ? modalStrings.packageFileSizeExceededWarning$({
                size: formatFileSize(file.size),
              })
            : modalStrings.fileSizeExceededWarning$({
                size: formatFileSize(file.size),
              });
          createSnackbar(uploadWarningError.value);
          event.target.value = '';
          if (type === 'file') {
            selectedFile.value = null;
          } else if (type === 'html5') {
            selectedHtml5File.value = null;
          } else if (type === 'h5p') {
            selectedH5PFile.value = null;
          } else if (type === 'card') {
            clearCardImage();
          }
          return;
        }

        uploadWarningError.value = '';
        const baseName = file.name.replace(/\.[^/.]+$/, '');

        if (type === 'file') {
          selectedFile.value = file;
          if (!fileTitle.value) {
            fileTitle.value = baseName;
          }
        } else if (type === 'html5') {
          selectedHtml5File.value = file;
          if (!html5Title.value) {
            html5Title.value = baseName;
          }
        } else if (type === 'h5p') {
          selectedH5PFile.value = file;
          if (!h5pTitle.value) {
            h5pTitle.value = baseName;
          }
        } else if (type === 'card') {
          selectedCardImage.value = file;
          cardImagePreview.value = URL.createObjectURL(file);
          if (!cardTitle.value) {
            cardTitle.value = baseName;
          }
        }
      }

      function clearCardImage() {
        selectedCardImage.value = null;
        cardImagePreview.value = '';
      }

      async function handleGenerateAiContent() {
        if (!aiTopic.value.trim()) {
          aiTopicError.value = 'Please enter a topic';
          return;
        }
        aiTopicError.value = '';
        isGeneratingAi.value = true;
        try {
          const result = await generateLesson(aiTopic.value, aiGrade.value, '45');
          aiContent.value = result || `# ${aiTopic.value}\n\nKey Concepts and Learning Notes.`;
          aiTitle.value = `AI Study Guide: ${aiTopic.value}`;
        } catch (err) {
          aiContent.value = `# ${aiTopic.value}\n\n### Summary\nOverview of ${aiTopic.value} for students.\n\n### Key Points\n- Point 1\n- Point 2\n\n### Review Questions\n1. Explain the main idea in your own words.`;
          aiTitle.value = `Study Notes: ${aiTopic.value}`;
        } finally {
          isGeneratingAi.value = false;
        }
      }

      async function handleSubmit() {
        isSubmitting.value = true;
        try {
          const endpointUrl = `/api/lessons/lesson/${props.lessonId}/custom_resource/`;
          let response;

          if (activeTab.value === 'h5p') {
            if (h5pMode.value === 'hub') {
              if (h5pEditorIframe.value && h5pEditorIframe.value.contentWindow) {
                try {
                  const doc = h5pEditorIframe.value.contentWindow.document;
                  const saveBtn = doc.querySelector('#save-h5p');
                  if (saveBtn) {
                    saveBtn.click();
                    isSubmitting.value = false;
                    return;
                  }
                } catch (e) {
                  // Fallback
                }
              }
              isSubmitting.value = false;
              return;
            } else if (h5pMode.value === 'create') {
              const builder = activityBuilderRef.value;
              response = await client({
                url: endpointUrl,
                method: 'POST',
                data: {
                  resource_type: 'h5p',
                  title: builder.title.trim(),
                  description: builder.description.trim(),
                  content: builder.compiledHtml,
                },
              });
            } else {
              const formData = new FormData();
              formData.append('file', selectedH5PFile.value);
              formData.append('title', h5pTitle.value.trim());
              formData.append('description', h5pDescription.value.trim());
              formData.append('resource_type', 'h5p');

              response = await client({
                url: endpointUrl,
                method: 'POST',
                data: formData,
                headers: { 'Content-Type': 'multipart/form-data' },
              });
            }
          } else if (activeTab.value === 'file' || activeTab.value === 'html5') {
            const formData = new FormData();
            const file = activeTab.value === 'file' ? selectedFile.value : selectedHtml5File.value;
            const title = activeTab.value === 'file' ? fileTitle.value : html5Title.value;
            const desc =
              activeTab.value === 'file' ? fileDescription.value : html5Description.value;

            formData.append('file', file);
            formData.append('title', title);
            formData.append('description', desc);
            formData.append('resource_type', activeTab.value === 'html5' ? 'html5' : '');

            response = await client({
              url: endpointUrl,
              method: 'POST',
              data: formData,
              headers: { 'Content-Type': 'multipart/form-data' },
            });
          } else if (activeTab.value === 'youtube') {
            response = await client({
              url: endpointUrl,
              method: 'POST',
              data: {
                resource_type: 'youtube',
                title: youtubeTitle.value,
                description: youtubeDescription.value,
                url: youtubeUrl.value,
              },
            });
          } else if (activeTab.value === 'ai') {
            response = await client({
              url: endpointUrl,
              method: 'POST',
              data: {
                resource_type: 'ai_text',
                title: aiTitle.value || `Study Notes: ${aiTopic.value}`,
                description: `AI-generated study material on ${aiTopic.value}`,
                content: aiContent.value,
              },
            });
          } else if (activeTab.value === 'card') {
            const formData = new FormData();
            if (selectedCardImage.value) {
              formData.append('file', selectedCardImage.value);
            }
            formData.append('title', cardTitle.value);
            formData.append('description', cardDescription.value);
            formData.append('content', cardContent.value);
            formData.append('resource_type', 'content_card');

            response = await client({
              url: endpointUrl,
              method: 'POST',
              data: formData,
              headers: { 'Content-Type': 'multipart/form-data' },
            });
          } else if (activeTab.value === 'builder') {
            response = await client({
              url: endpointUrl,
              method: 'POST',
              data: {
                resource_type: 'lesson_builder',
                title: builderTitle.value.trim(),
                description: builderDescription.value.trim(),
                content: JSON.stringify(builderBlocks.value),
              },
            });
          } else if (activeTab.value === 'perseus') {
            const pData = perseusActivityData.value;
            response = await client({
              url: endpointUrl,
              method: 'POST',
              data: {
                resource_type: 'perseus',
                title:
                  pData && pData.title && pData.title.trim()
                    ? pData.title.trim()
                    : 'Perseus Interactive Activity',
                description: pData && pData.description ? pData.description.trim() : '',
                content: JSON.stringify((pData && pData.item) || pData || {}),
              },
            });
          }

          createSnackbar(modalStrings.successNotice$());
          emit('added', response.data);
          emit('close');
        } catch (err) {
          const detailMsg = err.response && err.response.data && err.response.data.detail;
          createSnackbar(detailMsg || modalStrings.errorNotice$());
        } finally {
          isSubmitting.value = false;
        }
      }

      return {
        activeTab,
        isSubmitting,
        isSubmitDisabled,
        uploadWarningError,
        // Lesson Builder tab
        builderTitle,
        builderDescription,
        builderTitleError,
        activeBlockIndex,
        builderBlocks,
        builderImageInput,
        addNewBlock,
        moveBlockUp,
        moveBlockDown,
        duplicateBlock,
        removeBlock,
        triggerBlockImageUpload,
        onBuilderImageSelected,
        // File tab
        selectedFile,
        fileTitle,
        fileDescription,
        fileTitleError,
        fileInput,
        // YouTube tab
        youtubeUrl,
        youtubeTitle,
        youtubeDescription,
        youtubeUrlError,
        youtubeTitleError,
        isValidYoutubeUrl,
        // HTML5 tab
        selectedHtml5File,
        html5Title,
        html5Description,
        html5TitleError,
        html5Input,
        // H5P tab
        h5pMode,
        activityBuilderRef,
        selectedH5PFile,
        h5pTitle,
        h5pDescription,
        h5pInput,
        h5pEditorIframe,
        isSavingH5P,
        isIframeLoading,
        onIframeLoaded,
        h5pEditorUrl,
        reloadH5PEditor,
        // AI tab
        aiTopic,
        aiGrade,
        aiFormat,
        aiContent,
        aiTitle,
        aiTopicError,
        isGeneratingAi,
        gradeOptions,
        formatOptions,
        // Card tab
        selectedCardImage,
        cardImagePreview,
        cardTitle,
        cardDescription,
        cardContent,
        cardTitleError,
        cardInput,
        // Methods
        formatFileSize,
        triggerFileInput,
        onFileSelected,
        clearCardImage,
        handleGenerateAiContent,
        handleSubmit,
        // Perseus tab
        perseusActivityData,
        onPerseusStudioChange,
        // Strings
        ...modalStrings,
      };
    },
    props: {
      lessonId: {
        type: String,
        required: true,
      },
      initialTab: {
        type: String,
        default: 'builder',
      },
    },
    emits: ['close', 'added'],
  };

</script>


<style lang="scss" scoped>

  .add-custom-resource-modal {
    padding-top: 8px;
  }

  .tab-button-group {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    padding-bottom: 16px;
    margin-bottom: 16px;
  }

  .tab-btn {
    min-width: 130px;
  }

  .tab-content {
    animation: fade-in 0.2s ease-in-out;
  }

  .drop-zone {
    display: block;
    width: 100%;
    padding: 24px;
    font-family: inherit;
    text-align: center;
    cursor: pointer;
    border: 2px dashed;
    border-radius: 8px;
    transition: all 0.2s ease;

    &:hover {
      opacity: 0.9;
    }
  }

  .hidden-file-input {
    display: none;
  }

  .upload-icon {
    margin-bottom: 8px;
    font-size: 36px;
  }

  .drop-text {
    margin: 0;
    font-weight: 500;
  }

  .file-info-badge {
    display: inline-flex;
    gap: 8px;
    align-items: center;
    font-weight: 600;
  }

  .mt-16 {
    margin-top: 16px;
  }

  .mb-16 {
    margin-bottom: 16px;
  }

  .row-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }

  .d-flex {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .ai-loading {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .submitting-overlay {
    padding: 16px;
    margin-top: 16px;
    text-align: center;
  }

  .card-img-preview-container {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
    justify-content: center;
  }

  .card-preview-thumb {
    max-width: 120px;
    max-height: 80px;
    object-fit: cover;
    border-radius: 4px;
  }

  .rotate-up {
    transform: rotate(90deg);
  }

  .rotate-down {
    transform: rotate(90deg);
  }

  .builder-tab-content {
    max-height: 70vh;
    overflow-y: auto;
    padding-right: 4px;
  }

  .builder-block-card {
    transition: all 0.2s ease;
  }

  .mt-8 {
    margin-top: 8px;
  }

  .mt-12 {
    margin-top: 12px;
  }

  .mb-8 {
    margin-bottom: 8px;
  }

  @keyframes fade-in {
    from {
      opacity: 0;
      transform: translateY(4px);
    }

    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

</style>
