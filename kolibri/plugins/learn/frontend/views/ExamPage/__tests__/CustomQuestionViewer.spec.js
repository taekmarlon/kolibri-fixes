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
});
