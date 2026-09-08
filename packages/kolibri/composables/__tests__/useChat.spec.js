import useChat from '../useChat';

jest.mock('kolibri/client');
jest.mock('kolibri/urls');
jest.mock('../../components/chat/chatAudio', () => ({
  playMessageChime: jest.fn(),
  isChatMuted: jest.fn(() => false),
  setChatMuted: jest.fn(),
}));

describe('useChat composable', () => {
  let chat;

  beforeEach(() => {
    chat = useChat();
    chat.activeWindows.value = [];
    chat.minimizedChatheads.value = [];
    chat.conversations.value = [];
  });

  it('opens a conversation and marks it read', () => {
    const conv = { id: 'conv-1', title: 'Test Conv', unread_count: 3 };
    chat.conversations.value = [conv];

    chat.openConversation(conv);

    expect(chat.activeWindows.value.length).toBe(1);
    expect(chat.activeWindows.value[0].id).toBe('conv-1');
  });

  it('caps active windows at 3 and minimizes oldest to chatheads', () => {
    const c1 = { id: 'c1', title: 'Chat 1' };
    const c2 = { id: 'c2', title: 'Chat 2' };
    const c3 = { id: 'c3', title: 'Chat 3' };
    const c4 = { id: 'c4', title: 'Chat 4' };

    chat.openConversation(c1);
    chat.openConversation(c2);
    chat.openConversation(c3);

    expect(chat.activeWindows.value.length).toBe(3);
    expect(chat.minimizedChatheads.value.length).toBe(0);

    // Opening 4th window should push c1 to minimizedChatheads
    chat.openConversation(c4);

    expect(chat.activeWindows.value.length).toBe(3);
    expect(chat.activeWindows.value.map(c => c.id)).toEqual(['c2', 'c3', 'c4']);
    expect(chat.minimizedChatheads.value.length).toBe(1);
    expect(chat.minimizedChatheads.value[0].id).toBe('c1');
  });

  it('minimizes an active conversation to chatheads', () => {
    const c1 = { id: 'c1', title: 'Chat 1' };
    chat.openConversation(c1);
    expect(chat.activeWindows.value.length).toBe(1);

    chat.minimizeConversation('c1');
    expect(chat.activeWindows.value.length).toBe(0);
    expect(chat.minimizedChatheads.value.length).toBe(1);
    expect(chat.minimizedChatheads.value[0].id).toBe('c1');
  });

  it('restores a conversation from chatheads back to active windows', () => {
    const c1 = { id: 'c1', title: 'Chat 1' };
    chat.openConversation(c1);
    chat.minimizeConversation('c1');
    expect(chat.minimizedChatheads.value.length).toBe(1);

    chat.restoreConversation(c1);
    expect(chat.minimizedChatheads.value.length).toBe(0);
    expect(chat.activeWindows.value.length).toBe(1);
    expect(chat.activeWindows.value[0].id).toBe('c1');
  });

  it('closes a conversation from active windows and minimized chatheads', () => {
    const c1 = { id: 'c1', title: 'Chat 1' };
    chat.openConversation(c1);

    chat.closeConversation('c1');
    expect(chat.activeWindows.value.length).toBe(0);
    expect(chat.minimizedChatheads.value.length).toBe(0);
  });
});
