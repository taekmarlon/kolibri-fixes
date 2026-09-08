<template>

  <LearnAppBarPage
    :appBarTitle="learnString('learnLabel')"
    :loading="pageLoading"
  >
    <div
      v-if="!pageLoading && resource"
      role="main"
      class="custom-resource-page"
    >
      <KBreadcrumbs
        :items="breadcrumbs"
        :ariaLabel="learnString('classesAndAssignmentsLabel')"
        class="mb-16"
      />

      <!-- Resource Header -->
      <section class="mb-24 resource-header">
        <div class="header-top">
          <div class="title-row">
            <KIcon
              :icon="resourceKindIcon"
              class="kind-icon"
            />
            <h1
              dir="auto"
              class="resource-title"
              :style="{ color: $themeTokens.text }"
            >
              {{ resource.title }}
            </h1>
            <span
              class="type-pill"
              :style="{
                backgroundColor: $themePalette.grey.v_200,
                color: $themeTokens.annotation,
              }"
            >
              {{ typePillText }}
            </span>
          </div>

          <div class="completion-action">
            <KButton
              v-if="!isCompleted"
              :text="markCompletedLabel$()"
              icon="check"
              :primary="true"
              appearance="raised-button"
              @click="handleMarkAsCompleted"
            />
            <div
              v-else
              class="completed-badge"
              :style="{
                backgroundColor: '#dcfce7',
                color: '#15803d',
                borderColor: '#86efac',
              }"
            >
              <KIcon icon="check" />
              <span>{{ completedNotice$() }}</span>
            </div>
          </div>
        </div>

        <div
          v-if="resource.description"
          class="mt-8 teacher-note"
        >
          <p
            dir="auto"
            :style="{ color: $themeTokens.annotation }"
          >
            {{ resource.description }}
          </p>
        </div>
      </section>

      <!-- Main Viewer Area -->
      <section
        class="resource-viewer-container"
        :style="{
          backgroundColor: $themeTokens.surface,
          borderColor: $themeTokens.fineLine,
        }"
      >
        <!-- 1. YouTube Video Player -->
        <div
          v-if="resource.resource_type === 'youtube'"
          class="viewer-wrapper"
        >
          <YouTubePlayer
            :url="resource.url"
            :title="resource.title"
          />
        </div>

        <!-- 2. PDF Document Viewer -->
        <div
          v-else-if="resource.resource_type === 'pdf'"
          class="pdf-box viewer-wrapper"
        >
          <div class="action-bar mb-8">
            <KButton
              :text="downloadPdfLabel$()"
              icon="download"
              appearance="flat-button"
              @click="downloadFile(resource.file_url)"
            />
          </div>
          <iframe
            :src="resource.file_url"
            class="pdf-iframe"
            :title="pdfDocTitle$()"
          ></iframe>
        </div>

        <!-- 3. Image Viewer -->
        <div
          v-else-if="resource.resource_type === 'image'"
          class="image-box viewer-wrapper"
        >
          <img
            :src="resource.file_url"
            :alt="resource.title"
            class="responsive-image"
          >
        </div>

        <!-- 4. HTML5 Interactive Simulation / App -->
        <div
          v-else-if="resource.resource_type === 'html5'"
          class="html5-box viewer-wrapper"
        >
          <iframe
            :src="resource.file_url"
            sandbox="allow-scripts allow-same-origin"
            allow="fullscreen"
            class="html5-iframe"
            :title="html5DocTitle$()"
          ></iframe>
        </div>

        <!-- 5. Standalone Content Card (Banner Image + Formatted Content) -->
        <div
          v-else-if="resource.resource_type === 'content_card'"
          class="content-card-box viewer-wrapper"
        >
          <div
            v-if="resource.file_url"
            class="card-banner-box"
          >
            <img
              :src="resource.file_url"
              :alt="resource.title"
              class="card-banner-image"
            >
          </div>
          <div class="card-text-body">
            <AiMessageRenderer :content="resource.content" />
          </div>
        </div>

        <!-- 6. AI Generated Study Guide / Markdown Notes -->
        <div
          v-else-if="resource.resource_type === 'ai_text' || resource.content"
          class="ai-box viewer-wrapper"
        >
          <div
            class="ai-card"
            :style="{
              backgroundColor: $themePalette.grey.v_100,
              border: `1px solid ${$themeTokens.fineLine}`,
            }"
          >
            <div
              class="ai-card-header"
              :style="{ borderBottom: `1px solid ${$themeTokens.fineLine}` }"
            >
              <span
                class="ai-badge"
                :style="{ backgroundColor: $themeTokens.primary, color: 'white' }"
              >
                {{ aiStudyNotesBadge$() }}
              </span>
            </div>
            <div class="ai-card-body">
              <AiMessageRenderer :content="resource.content" />
            </div>
          </div>
        </div>

        <!-- 6. Generic Document (DOCX, PPTX, etc.) -->
        <div
          v-else
          class="doc-box viewer-wrapper"
        >
          <div
            class="doc-download-card"
            :style="{ backgroundColor: $themePalette.grey.v_100 }"
          >
            <KIcon
              icon="document"
              class="doc-icon"
            />
            <h3>{{ resource.file_name || resource.title }}</h3>
            <p
              v-if="resource.file_size"
              :style="{ color: $themeTokens.annotation }"
            >
              {{ formatFileSize(resource.file_size) }}
            </p>
            <KButton
              v-if="resource.file_url"
              :text="downloadDocLabel$()"
              icon="download"
              :primary="true"
              appearance="raised-button"
              class="mt-16"
              @click="downloadFile(resource.file_url)"
            />
          </div>
        </div>
      </section>

      <!-- Inline AI Study Assistant (Khanmigo-style) -->
      <section class="mt-24">
        <InlineAiTutor
          :resourceTitle="resource.title || ''"
          :resourceDescription="resource.description || resource.content || ''"
          :resourceKind="resource.resource_type || 'document'"
        />
      </section>
    </div>

    <KCircularLoader v-else />
  </LearnAppBarPage>

</template>


<script>

  import { ref, computed, onMounted } from 'vue';
  import { useRoute } from 'vue-router/composables';
  import client from 'kolibri/client';
  import urls from 'kolibri/urls';
  import { createTranslator } from 'kolibri/utils/i18n';
  import KBreadcrumbs from 'kolibri-design-system/lib/KBreadcrumbs';
  import commonCoreStrings from 'kolibri/uiText/commonCoreStrings';
  import { pageLoading } from 'kolibri-common/composables/usePageLoading';
  import useSnackbar from 'kolibri/composables/useSnackbar';
  import YouTubePlayer from 'kolibri-common/components/YouTubePlayer';
  import AiMessageRenderer from 'kolibri-common/components/AiMessageRenderer';
  import InlineAiTutor from 'kolibri-common/components/InlineAiTutor';
  import { setContentNodeProgress } from '../../composables/useContentNodeProgress';
  import { LearnerLessonResource } from '../../apiResources';
  import { PageNames, ClassesPageNames } from '../../constants';
  import commonLearnStrings from '../commonLearnStrings';
  import LearnAppBarPage from '../LearnAppBarPage';

  const resourceStrings = createTranslator('LessonCustomResourcePageStrings', {
    markCompletedLabel: {
      message: 'Mark as Completed',
      context: 'Button label',
    },
    completedNotice: {
      message: 'Completed',
      context: 'Status badge label',
    },
    downloadPdfLabel: {
      message: 'Download PDF',
      context: 'Download button',
    },
    downloadDocLabel: {
      message: 'Download Document',
      context: 'Download button',
    },
    progressSavedNotice: {
      message: 'Progress recorded! Great job completing this resource.',
      context: 'Confirmation notification',
    },
    pdfDocTitle: {
      message: 'PDF Document',
      context: 'Title attribute for PDF viewer iframe',
    },
    html5DocTitle: {
      message: 'Interactive Simulation',
      context: 'Title attribute for HTML5 viewer iframe',
    },
    aiStudyNotesBadge: {
      message: '✨ AI Study Notes',
      context: 'Badge label for AI generated notes',
    },
  });

  export default {
    name: 'LessonCustomResourcePage',
    components: {
      KBreadcrumbs,
      LearnAppBarPage,
      YouTubePlayer,
      AiMessageRenderer,
      InlineAiTutor,
    },
    mixins: [commonCoreStrings, commonLearnStrings],
    setup() {
      const route = useRoute();
      const { createSnackbar } = useSnackbar();

      const currentLesson = ref(null);
      const resource = ref(null);
      const isCompleted = ref(false);

      const classId = computed(() => route.params.classId);
      const lessonId = computed(() => route.params.lessonId);
      const resourceId = computed(() => route.params.resourceId);

      const resourceKindIcon = computed(() => {
        if (!resource.value) return 'document';
        const type = resource.value.resource_type;
        if (type === 'youtube') return 'video';
        if (type === 'image') return 'image';
        if (type === 'html5') return 'html5';
        if (type === 'content_card') return 'topic';
        if (type === 'ai_text') return 'hint';
        return 'document';
      });

      const typePillText = computed(() => {
        if (!resource.value) return 'RESOURCE';
        const type = resource.value.resource_type;
        if (type === 'youtube') return 'YOUTUBE VIDEO';
        if (type === 'pdf') return 'PDF DOCUMENT';
        if (type === 'image') return 'PICTURE / DIAGRAM';
        if (type === 'html5') return 'HTML5 SIMULATION';
        if (type === 'content_card') return 'CONTENT CARD';
        if (type === 'ai_text') return 'AI STUDY GUIDE';
        return 'DOCUMENT';
      });

      const breadcrumbs = computed(() => {
        const classroomName =
          (currentLesson.value &&
            currentLesson.value.classroom &&
            currentLesson.value.classroom.name) ||
          'Class';
        return [
          {
            text: 'Home',
            link: { name: PageNames.HOME },
          },
          {
            text: 'Classes',
            link: { name: ClassesPageNames.ALL_CLASSES },
          },
          {
            text: classroomName,
            link: {
              name: ClassesPageNames.CLASS_ASSIGNMENTS,
              params: { classId: classId.value },
            },
          },
          {
            text: (currentLesson.value && currentLesson.value.title) || 'Lesson',
            link: {
              name: ClassesPageNames.LESSON_PLAYLIST,
              params: {
                classId: classId.value,
                lessonId: lessonId.value,
              },
            },
          },
          {
            text: resource.value ? resource.value.title : 'Custom Resource',
          },
        ];
      });

      function formatFileSize(bytes) {
        if (!bytes) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
      }

      async function loadData() {
        pageLoading.value = true;
        try {
          const lesson = await LearnerLessonResource.fetchModel({
            id: lessonId.value,
            force: true,
          });
          currentLesson.value = lesson;
          const found = (lesson.resources || []).find(
            r => r.contentnode_id === resourceId.value || r.content_id === resourceId.value,
          );
          if (found) {
            resource.value = found;
            if (found.progress >= 1.0) {
              isCompleted.value = true;
            }
          }
        } catch (err) {
          // ignore
        } finally {
          pageLoading.value = false;
        }
      }

      async function handleMarkAsCompleted() {
        if (!resource.value) return;
        isCompleted.value = true;

        setContentNodeProgress({
          content_id: resource.value.content_id,
          progress: 1.0,
        });

        try {
          const now = new Date().toISOString();
          await client({
            url: urls['kolibri:core:contentsummarylog_list'](),
            method: 'POST',
            data: {
              content_id: resource.value.content_id,
              start_timestamp: now,
              end_timestamp: now,
              completion_timestamp: now,
              progress: 1.0,
              time_spent: 120,
              kind: resource.value.resource_type === 'youtube' ? 'video' : 'document',
            },
          });
          createSnackbar(resourceStrings.progressSavedNotice$());
        } catch (err) {
          // Keep completed state
        }
      }

      function downloadFile(url) {
        if (url) {
          window.open(url, '_blank');
        }
      }

      onMounted(() => {
        loadData();
      });

      return {
        pageLoading,
        resource,
        isCompleted,
        resourceKindIcon,
        typePillText,
        breadcrumbs,
        formatFileSize,
        handleMarkAsCompleted,
        downloadFile,
        ...resourceStrings,
      };
    },
  };

</script>


<style lang="scss" scoped>

  .custom-resource-page {
    padding: 0 16px 32px;
  }

  .mb-16 {
    margin-bottom: 16px;
  }

  .mb-24 {
    margin-bottom: 24px;
  }

  .mt-8 {
    margin-top: 8px;
  }

  .mt-16 {
    margin-top: 16px;
  }

  .mt-24 {
    margin-top: 24px;
  }

  .resource-header {
    .header-top {
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      align-items: center;
      justify-content: space-between;
    }

    .title-row {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
    }

    .kind-icon {
      font-size: 32px;
    }

    .resource-title {
      margin: 0;
      font-size: 1.75rem;
      font-weight: 700;
    }

    .type-pill {
      padding: 4px 10px;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.5px;
      border-radius: 9999px;
    }
  }

  .completed-badge {
    display: inline-flex;
    gap: 6px;
    align-items: center;
    padding: 6px 14px;
    font-weight: 600;
    border: 1px solid;
    border-radius: 20px;
  }

  .resource-viewer-container {
    min-height: 400px;
    overflow: hidden;
    border: 1px solid;
    border-radius: 8px;
  }

  .viewer-wrapper {
    width: 100%;
  }

  .pdf-box {
    padding: 16px;

    .pdf-iframe {
      width: 100%;
      height: 750px;
      border: 1px solid #e5e7eb;
      border-radius: 6px;
    }
  }

  .image-box {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
    background-color: #0000000d;

    .responsive-image {
      max-width: 100%;
      max-height: 800px;
      border-radius: 6px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
  }

  .html5-box {
    .html5-iframe {
      width: 100%;
      height: 720px;
      border: 0;
    }
  }

  .content-card-box {
    padding: 28px;

    .card-banner-box {
      margin-bottom: 24px;
      text-align: center;

      .card-banner-image {
        max-width: 100%;
        max-height: 480px;
        object-fit: cover;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
      }
    }

    .card-text-body {
      font-size: 1.05rem;
      line-height: 1.7;
    }
  }

  .ai-box {
    padding: 20px;

    .ai-card {
      overflow: hidden;
      border-radius: 8px;

      .ai-card-header {
        padding: 12px 16px;
      }

      .ai-badge {
        display: inline-block;
        padding: 4px 10px;
        font-size: 12px;
        font-weight: 700;
        border-radius: 4px;
      }

      .ai-card-body {
        padding: 20px;
      }
    }
  }

  .doc-box {
    display: flex;
    justify-content: center;
    padding: 48px 16px;

    .doc-download-card {
      width: 100%;
      max-width: 480px;
      padding: 32px;
      text-align: center;
      border-radius: 12px;

      .doc-icon {
        margin-bottom: 12px;
        font-size: 56px;
      }
    }
  }

  .download-link {
    text-decoration: none;
  }

</style>
