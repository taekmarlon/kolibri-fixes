/* eslint-disable kolibri/tests-no-hardcoded-strings */
import { render, screen } from '@testing-library/vue';
import CustomQuestionViewer from '../CustomQuestionViewer.vue';

describe('CustomQuestionViewer', () => {
  it('renders a multiple choice question with prompt and choices', () => {
    const question = {
      is_custom: true,
      question_type: 'multiple_choice',
      prompt: 'What is 2 + 2?',
      options: [
        { id: 'opt1', text: '3', image: '' },
        { id: 'opt2', text: '4', image: '' },
      ],
      answer_key: ['opt2'],
      point_value: 1,
    };

    render(CustomQuestionViewer, {
      props: {
        question,
        answerState: null,
      },
    });

    expect(screen.getByText('What is 2 + 2?')).toBeTruthy();
    expect(screen.getByText('3')).toBeTruthy();
    expect(screen.getByText('4')).toBeTruthy();
  });

  it('renders an iframe pointing to file_url when standalone bundle is available', () => {
    const question = {
      is_custom: true,
      question_type: 'h5p',
      title: 'Addition 1-5',
      prompt: 'Addition 1-5',
      h5p_content_id: '42',
      h5p_url: '/h5p/play/42',
      file_url: '/media/lessons/interactive/abc1234/index.html',
      content: '<html>standalone bundle</html>',
      options: [],
      answer_key: [],
      point_value: 10,
    };

    const { container } = render(CustomQuestionViewer, {
      props: {
        question,
        answerState: null,
      },
    });

    const iframe = container.querySelector('iframe.interactive-player-iframe');
    expect(iframe).toBeTruthy();
    expect(iframe.getAttribute('src')).toBe('/media/lessons/interactive/abc1234/index.html');
  });

  it('falls back to h5p_url or /h5p/play/:id if file_url is not present', () => {
    const question = {
      is_custom: true,
      question_type: 'h5p',
      title: 'Subtraction 1-5',
      prompt: 'Subtraction 1-5',
      h5p_content_id: '99',
      h5p_url: '/h5p/play/99',
      file_url: '',
      content: '',
      options: [],
      answer_key: [],
      point_value: 10,
    };

    const { container } = render(CustomQuestionViewer, {
      props: {
        question,
        answerState: null,
      },
    });

    const iframe = container.querySelector('iframe.interactive-player-iframe');
    expect(iframe).toBeTruthy();
    expect(iframe.getAttribute('src')).toBe('/h5p/play/99');
  });

  it('marks activity completed upon receiving H5P_COMPLETE postMessage', async () => {
    const question = {
      is_custom: true,
      question_type: 'h5p',
      title: 'Addition 1-5',
      prompt: 'Addition 1-5',
      h5p_content_id: '42',
      file_url: '/media/lessons/interactive/abc1234/index.html',
      options: [],
      answer_key: [],
      point_value: 10,
    };

    const { emitted } = render(CustomQuestionViewer, {
      props: {
        question,
        answerState: null,
      },
    });

    window.dispatchEvent(
      new MessageEvent('message', {
        data: { type: 'H5P_COMPLETE' },
      }),
    );

    expect(await screen.findByText('Interactive Activity Completed!')).toBeTruthy();
    expect(emitted().interaction).toBeTruthy();
  });

  it('toggles activity completion when clicking the manual completion button', async () => {
    const question = {
      is_custom: true,
      question_type: 'h5p',
      title: 'Addition 1-5',
      prompt: 'Addition 1-5',
      h5p_content_id: '42',
      file_url: '/media/lessons/interactive/abc1234/index.html',
      options: [],
      answer_key: [],
      point_value: 10,
    };

    const { emitted } = render(CustomQuestionViewer, {
      props: {
        question,
        answerState: null,
      },
    });

    const button = screen.getByRole('button', { name: /mark as completed/i });
    expect(button).toBeTruthy();
    await button.click();

    expect(screen.getByText('Interactive Activity Completed!')).toBeTruthy();
    expect(emitted().interaction).toBeTruthy();
  });

  it('renders preview mode with interactive score badge and status', () => {
    const question = {
      is_custom: true,
      question_type: 'interactive',
      title: 'Addition 1-3',
      prompt: 'Addition 1-3',
      file_url: '/media/lessons/interactive/1fb6259c50774362acc5e90a041c4938/index.html',
      options: [],
      answer_key: [],
      point_value: 5,
    };

    render(CustomQuestionViewer, {
      props: {
        question,
        answerState: {
          value: 'completed',
          type: 'h5p',
          simple_answer: '2/3 (Completed)',
        },
        preview: true,
      },
    });

    expect(screen.getByText('Interactive Activity Completed!')).toBeTruthy();
    expect(screen.getByText(/2\/3 \(Completed\)/)).toBeTruthy();
    expect(screen.getByText('5 point(s)')).toBeTruthy();
    // Manual mark as completed button should NOT be displayed in preview mode
    expect(screen.queryByRole('button', { name: /mark as completed/i })).toBeNull();
  });

  it('renders preview mode for multiple choice with learner answer and correct answer badges', () => {
    const question = {
      is_custom: true,
      question_type: 'multiple_choice',
      prompt: 'Which is 3 + 5?',
      options: [
        { id: 'optA', text: '7', image: '' },
        { id: 'optB', text: '8', image: '' },
      ],
      answer_key: ['optB'],
      point_value: 2,
    };

    render(CustomQuestionViewer, {
      props: {
        question,
        answerState: 'optA',
        preview: true,
        showCorrectAnswer: true,
      },
    });

    expect(screen.getByText('Which is 3 + 5?')).toBeTruthy();
    expect(screen.getByText('2 point(s)')).toBeTruthy();
    expect(screen.getByText('Learner answer')).toBeTruthy();
    expect(screen.getByText('Correct answer')).toBeTruthy();
  });

  it('renders a Perseus interactive question with prompt and points badge', () => {
    const perseusItem = {
      question: {
        content: 'Read the passage below and answer the question:\n\n[[☃ dropdown 1]]',
        images: {},
        widgets: {
          'dropdown 1': {
            type: 'dropdown',
            options: {
              choices: [
                { content: 'Photosynthesis', correct: true },
                { content: 'Respiration', correct: false },
              ],
            },
          },
        },
      },
      hints: [],
    };

    const question = {
      is_custom: true,
      question_type: 'perseus',
      prompt: 'Biological Processes Comprehension',
      content: JSON.stringify(perseusItem),
      point_value: 3,
    };

    render(CustomQuestionViewer, {
      props: {
        question,
        answerState: null,
      },
    });

    expect(screen.getByText('Biological Processes Comprehension')).toBeTruthy();
    expect(screen.getByText('3 point(s)')).toBeTruthy();
  });
});
