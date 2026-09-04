import { ClassesPageNames } from '../../constants';

export function classAssignmentsLink(classId) {
  return {
    name: ClassesPageNames.CLASS_ASSIGNMENTS,
    params: {
      classId,
    },
  };
}

export function lessonPlaylistLink(lessonId) {
  return {
    name: ClassesPageNames.LESSON_PLAYLIST,
    params: {
      lessonId,
    },
  };
}

export function assignmentDetailLink(classId, assignmentId) {
  return {
    name: ClassesPageNames.COURSEWORK_ASSIGNMENT_DETAIL,
    params: {
      classId,
      assignmentId,
    },
  };
}

export function classDiscussionsLink(classId) {
  return {
    name: ClassesPageNames.COURSEWORK_DISCUSSIONS,
    params: {
      classId,
    },
  };
}
