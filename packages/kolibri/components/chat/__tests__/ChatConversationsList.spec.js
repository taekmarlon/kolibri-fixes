/* eslint-disable kolibri/tests-no-hardcoded-strings */
import { render, screen } from '@testing-library/vue';
import ChatConversationsList from '../ChatConversationsList';

jest.mock('../../../composables/useChat', () => {
  const { ref } = require('vue');
  return () => ({
    conversations: ref([
      {
        id: 'conv-1',
        title: 'Grade 1 Sec-Diamond',
        kind: 'classroom',
        facility_name: 'CEDARHALL ACADEMY INC.',
        unread_count: 0,
        last_message: { content: 'Welcome class', is_self: false, created_at: new Date().toISOString() },
      },
    ]),
    contacts: ref([]),
    classrooms: ref([
      { id: 'c-1', name: 'Grade 1 Sec-Diamond', facility_name: 'CEDARHALL ACADEMY INC.' },
    ]),
    isMuted: ref(false),
    fetchConversations: jest.fn(),
    fetchContacts: jest.fn(),
    openConversation: jest.fn(),
    startDirectChat: jest.fn(),
    startClassroomChat: jest.fn(),
    toggleMute: jest.fn(),
  });
});

jest.mock('kolibri/composables/useUser', () => {
  const { ref } = require('vue');
  return () => ({
    userFacilityName: ref('CEDARHALL ACADEMY INC.'),
    isUserLoggedIn: ref(true),
    isAdmin: ref(true),
    isSuperuser: ref(true),
  });
});

describe('ChatConversationsList', () => {
  it('displays the active facility strip and conversation facility chip', () => {
    render(ChatConversationsList);

    // Active facility strip
    expect(screen.getByText(/Facility:/i)).toBeInTheDocument();
    expect(screen.getByText('CEDARHALL ACADEMY INC.')).toBeInTheDocument();

    // Conversation card facility tag
    const chips = screen.getAllByText(/CEDARHALL ACADEMY INC./i);
    expect(chips.length).toBeGreaterThanOrEqual(1);
  });
});
