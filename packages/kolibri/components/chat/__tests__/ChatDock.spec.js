/* eslint-disable kolibri/tests-no-hardcoded-strings */
import { render, screen, fireEvent } from '@testing-library/vue';
import ChatDock from '../ChatDock';

describe('ChatDock', () => {
  const sampleChatheads = [
    {
      id: 'conv-1',
      title: 'Rachelle Manalili',
      kind: 'direct',
      unread_count: 2,
    },
    {
      id: 'conv-2',
      title: 'Math Grade 5',
      kind: 'classroom',
      unread_count: 0,
    },
  ];

  it('renders chatheads for each docked conversation', () => {
    render(ChatDock, {
      props: {
        chatheads: sampleChatheads,
      },
    });

    expect(screen.getByText(/RM/)).toBeInTheDocument();
    expect(screen.getByText(/👥/)).toBeInTheDocument();
    expect(screen.getByText(/2/)).toBeInTheDocument();
  });

  it('emits restore with conversation when a chathead is clicked', async () => {
    const { emitted } = render(ChatDock, {
      props: {
        chatheads: sampleChatheads,
      },
    });

    const directItem = screen.getByTitle(/Rachelle Manalili/);
    await fireEvent.click(directItem);

    expect(emitted().restore).toBeTruthy();
    expect(emitted().restore[0][0].id).toBe('conv-1');
  });

  it('emits close with conversation id when close button is clicked', async () => {
    const { emitted } = render(ChatDock, {
      props: {
        chatheads: sampleChatheads,
      },
    });

    const closeBtns = screen.getAllByRole('button', { name: /Close/i });
    expect(closeBtns.length).toBe(2);

    await fireEvent.click(closeBtns[0]);
    expect(emitted().close).toBeTruthy();
    expect(emitted().close[0][0]).toBe('conv-1');
  });
});
