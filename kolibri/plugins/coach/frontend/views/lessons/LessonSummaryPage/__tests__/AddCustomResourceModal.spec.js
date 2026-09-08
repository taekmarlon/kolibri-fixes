import { render, screen, fireEvent } from '@testing-library/vue';
import AddCustomResourceModal from '../AddCustomResourceModal';

jest.mock('kolibri/client');
jest.mock('kolibri/composables/useSnackbar', () => () => ({
  createSnackbar: jest.fn(),
  clearSnackbar: jest.fn(),
}));
jest.mock('kolibri-common/composables/useAiTutor', () => () => ({
  isAiEnabled: { value: true },
  generateLesson: jest.fn().mockResolvedValue('Mock AI lesson content'),
  isLoading: { value: false },
}));

describe('AddCustomResourceModal', () => {
  const props = {
    lessonId: 'lesson_123',
  };

  it('renders modal title and all four resource tabs', () => {
    render(AddCustomResourceModal, {
      props,
    });

    expect(screen.getByText('Add Custom Resource to Lesson')).toBeTruthy();
    expect(screen.getByText('Upload File')).toBeTruthy();
    expect(screen.getByText('YouTube Video')).toBeTruthy();
    expect(screen.getByText('HTML5 Package')).toBeTruthy();
    expect(screen.getByText('Generate with AI')).toBeTruthy();
  });

  it('switches to YouTube Video tab when clicked', async () => {
    render(AddCustomResourceModal, {
      props,
    });

    const youtubeTabBtn = screen.getByText('YouTube Video');
    await fireEvent.click(youtubeTabBtn);

    expect(
      screen.getByText('Paste a YouTube video link. It will play safely inside PHIEDU for your learners.')
    ).toBeTruthy();
    expect(screen.getByLabelText('YouTube Video URL')).toBeTruthy();
  });

  it('switches to HTML5 Package tab when clicked', async () => {
    render(AddCustomResourceModal, {
      props,
    });

    const html5TabBtn = screen.getByText('HTML5 Package');
    await fireEvent.click(html5TabBtn);

    expect(
      screen.getByText('Upload an interactive HTML5 simulation or activity (.zip or .html).')
    ).toBeTruthy();
    expect(screen.getByText('Click or drop a .zip or .html file here')).toBeTruthy();
  });

  it('switches to AI Generator tab and displays prompt inputs', async () => {
    render(AddCustomResourceModal, {
      props,
    });

    const aiTabBtn = screen.getByText('Generate with AI');
    await fireEvent.click(aiTabBtn);

    expect(
      screen.getByText('Create structured study guides, summaries, or practice notes instantly with AI.')
    ).toBeTruthy();
    expect(screen.getByText('Generate Material with AI')).toBeTruthy();
  });
});
