import ContentNodeResource from 'kolibri-common/apiResources/ContentNodeResource';
import useUser from 'kolibri/composables/useUser';
import { handleApiError } from 'kolibri/utils/appError';
import { get } from '@vueuse/core';
import { pageLoading } from 'kolibri-common/composables/usePageLoading';
import useContentNodeProgress from '../../composables/useContentNodeProgress';
import { LearnerLessonResource } from '../../apiResources';
import { ClassesPageNames } from '../../constants';

const { fetchContentNodeProgress } = useContentNodeProgress();

// For a given Lesson, shows a "playlist" of all the resources in the Lesson
export function showLessonPlaylist(store, { lessonId }) {
  pageLoading.value = true;
  // Only load contentnode progress if the user is logged in
  const { isUserLoggedIn } = useUser();
  if (get(isUserLoggedIn)) {
    fetchContentNodeProgress({ lesson: lessonId });
  }
  let currentLessonObj = null;
  const contentNodePromise = ContentNodeResource.fetchLessonResources(lessonId);
  return LearnerLessonResource.fetchModel({ id: lessonId })
    .then(lesson => {
      currentLessonObj = lesson;
      store.commit('SET_PAGE_NAME', ClassesPageNames.LESSON_PLAYLIST);
      store.commit('lessonPlaylist/SET_CURRENT_LESSON', lesson);
      const hasChannelResources = (lesson.resources || []).some(r => !r.is_custom);
      if (hasChannelResources) {
        return contentNodePromise;
      }
      return Promise.resolve([]);
    })
    .then(contentNodes => {
      const contentNodesMap = {};
      for (const node of contentNodes) {
        contentNodesMap[node.id] = node;
      }
      if (currentLessonObj && currentLessonObj.resources) {
        for (const r of currentLessonObj.resources) {
          if (r.is_custom) {
            const kind =
              r.resource_type === 'youtube'
                ? 'video'
                : r.resource_type === 'image'
                ? 'image'
                : r.resource_type === 'html5'
                ? 'html5'
                : 'document';

            contentNodesMap[r.contentnode_id] = {
              id: r.contentnode_id,
              content_id: r.content_id,
              title: r.title || 'Custom Resource',
              description: r.description || '',
              kind,
              is_custom: true,
              is_leaf: true,
              resource_type: r.resource_type,
              url: r.url,
              file_url: r.file_url,
              file_name: r.file_name,
              file_size: r.file_size,
              content: r.content,
            };
          }
        }
      }
      store.commit('lessonPlaylist/SET_LESSON_CONTENTNODES', contentNodesMap);
      pageLoading.value = false;
    })
    .catch(error => {
      pageLoading.value = false;
      handleApiError({ error, reloadOnReconnect: true });
    });
}
